using CSV
using DataFrames
using MultipleTesting
using Statistics


function retrieve_data(ensemble_path::String, csv_filename::String, target_col_name::Symbol, ignore_dir::String)
    data = Dict{Tuple{Float64, Float64}, Vector{Float64}}()

    for path in filter(isdir, readdir(ensemble_path, join=true))
        occursin(ignore_dir, splitdir(path)[end]) && continue
        csv_path = joinpath(path, csv_filename)
        if isfile(csv_path)
            df = CSV.read(csv_path, DataFrame)
            for row in eachrow(df)
                lon, lat = row[:lon], row[:lat]
                if !haskey(data, (lon, lat))
                    data[lon, lat] = Float64[]
                end
                push!(data[lon, lat], Float64(row[target_col_name]))
            end
        else
            @warn "Skipping $(path) as it does not contain the required CSV file"
            continue
        end
    end
    return data
end

function bootstrap_null_test(data::Dict{Tuple{Float64, Float64}, Vector{Float64}}, N_iter::Int)
    coords = collect(keys(data))

    @info "Pool all data across the domain to create a global distribution for the null hypothesis..."
    global_pool = Float64[]
    for values in values(data)
        append!(global_pool, values)
    end

    @info "Generating Null Distribution from global pool ($(length(global_pool)) samples)..."
    ensemble_size = length(first(values(data)))
    null_medians = Float64[]

    for i in 1:N_iter
        mod(i, 100) == 0 && @info "Iteration $i/$N_iter"
        # If the null is true, a cell's models are just random draws from the whole domain
        null_sample = rand(global_pool, ensemble_size)
        push!(null_medians, median(null_sample))
    end
    sort!(null_medians)
    global_median_val = median(global_pool)

    @info "Calculating p-values for each grid point..."
    final_results = Dict{Tuple{Float64, Float64}, Dict{String, Any}}()
    raw_p_values = Float64[]

    for coord in coords
        local_median = median(data[coord])

        # Two-sided test: fraction of null medians more extreme than our observation
        prop_ge = sum(x -> x >= local_median, null_medians) / N_iter
        prop_le = sum(x -> x <= local_median, null_medians) / N_iter

        pval = 2.0 * min(prop_ge, prop_le)
        pval = min(pval, 1.0)

        push!(raw_p_values, pval)

        # Store metadata
        final_results[coord] = Dict(
            "local_median" => local_median,
            "global_median" => global_median_val,
            "p_value_raw" => pval
        )
    end

    @info "Applying Benjamini-Hochberg correction for field significance..."
    adj_p_values = adjust(raw_p_values, BenjaminiHochberg())

    # Count how many points are significant at alpha = 0.05
    sig_count = 0
    sig_count_adj = 0

    for (i, coord) in enumerate(coords)
        final_results[coord]["p_value_adj"] = adj_p_values[i]
        final_results[coord]["is_significant"] = adj_p_values[i] < 0.05 ? 1 : 0
        final_results[coord]["is_significant_raw"] = raw_p_values[i] < 0.05 ? 1 : 0

        if raw_p_values[i] < 0.05
            sig_count += 1
        end

        if adj_p_values[i] < 0.05
            sig_count_adj += 1
        end
    end

    perc = (sig_count / length(coords)) * 100
    perc_adj = (sig_count_adj / length(coords)) * 100
    @info "Field Significance Result (Raw): $(round(perc, digits=2))% of grid is statistically unique."
    @info "Field Significance Result (Adjusted): $(round(perc_adj, digits=2))% of grid is statistically unique."

    return final_results
end

# Updated write function to handle new keys
function write_to_csv(results::Dict, output_path::String)
    df_data = []
    for (coord, stats) in results
        push!(df_data, merge(Dict("lon" => coord[1], "lat" => coord[2]), stats))
    end
    CSV.write(output_path, DataFrame(df_data))
end



ensemble_path = joinpath("data", "models", "mev_nn", "final_ensemble")
output_dir = "results_bootstrap_null"
mkpath(joinpath(ensemble_path, output_dir))

rl_years = [10, 20, 30]

for rl_year in rl_years
    output_fp = joinpath(ensemble_path, output_dir, "null_test_y$(rl_year).csv")

    @info "Processing Return Level: $rl_year"
    data = retrieve_data(ensemble_path, "returns_y$(rl_year)_best_model.bson.csv", :target, output_dir)

    results = bootstrap_null_test(data, 1000)
    write_to_csv(results, output_fp)
end

@info "Analysis Complete."
