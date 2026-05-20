using CSV
using DataFrames
using Statistics

include("../../utils/config.jl")


function bootstrap_statistics(data::Vector{Float64})
    qs = [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    quantile_vals = Statistics.quantile(data, qs)
    std1_val = std(data)

    return Dict(
        "q01" => quantile_vals[1],
        "q05" => quantile_vals[2],
        "q10" => quantile_vals[3],
        "q25" => quantile_vals[4],
        "q75" => quantile_vals[6],
        "q90" => quantile_vals[7],
        "q95" => quantile_vals[8],
        "q99" => quantile_vals[9],
        "mean" => mean(data),
        "median" => quantile_vals[5],
        "90p_conf_band" => quantile_vals[8] - quantile_vals[2],
        "98p_conf_band" => quantile_vals[9] - quantile_vals[1],
    )
end


function retrieve_data(ensemble_path::String, csv_filename::String, target_col_name::Symbol, ignore_dir::String)
    data = Dict{Tuple{Float64, Float64}, Vector{Float64}}()

    cnt = 0

    for path in filter(isdir, readdir(ensemble_path, join=true))
        occursin(ignore_dir, splitdir(path)[end]) && continue

        csv_path = joinpath(path, csv_filename)

        if isfile(csv_path)
            df = CSV.read(csv_path, DataFrame)

            for row in eachrow(df)
                lon, lat = row[:lon], row[:lat]

                if !haskey(data, (lon, lat))
                    data[lon, lat] = []
                end

                push!(data[lon, lat], row[target_col_name])
            end
        else
            @warn "Skipping $(path) as it does not contain the required CSV file"
            continue
        end

        cnt += 1
    end

    return data
end




function bootstrap(data::Dict{Tuple{Float64, Float64}, Vector{Float64}}, N::Int)
    bootstrap_results = Dict{Tuple{Float64, Float64}, Dict{String, Float64}}()
    medians = Float64[]
    coords = Tuple{Float64, Float64}[]
    sample_medians_map = Dict{Tuple{Float64, Float64}, Vector{Float64}}()

    for (coord, values) in data
        sample_medians = Float64[]
        for _ in 1:N
            sample = rand(values, length(values))
            push!(sample_medians, median(sample))
        end
        bootstrap_results[coord] = bootstrap_statistics(sample_medians)
        sample_medians_map[coord] = sample_medians
        push!(medians, bootstrap_results[coord]["median"])
        push!(coords, coord)
    end

    # Calculate domain-wide median (null hypothesis)
    domain_median = median(medians)

    # Compute p-values using each cell's bootstrap median distribution
    for coord in coords
        r = bootstrap_results[coord]
        samples = sample_medians_map[coord]

        # proportion greater or equal to domain_median
        prop_ge = sum(x -> x >= domain_median, samples) / length(samples)
        prop_le = sum(x -> x <= domain_median, samples) / length(samples)
        pval = 2.0 * min(prop_ge, prop_le) # two-sided p-value
        pval = min(pval, 1.0)
        r["p_value"] = pval
        r["domain_median"] = domain_median
    end

    return bootstrap_results
end


function write_to_csv(bootstrap_results::Dict{Tuple{Float64, Float64}, Dict{String, Float64}}, output_path::String)
    initcols = Dict(k => Float64[] for k in keys(first(values(bootstrap_results))))
    initcols["lat"] = Float64[]
    initcols["lon"] = Float64[]

    results_df = DataFrame(initcols)

    for (coord, stats) in bootstrap_results
        lon, lat = coord
        row = Dict("lon" => lon, "lat" => lat)

        for (key, value) in stats
            row[key] = value
        end

        push!(results_df, row)
    end

    CSV.write(output_path, results_df)
end

ensemble_path = get_ensemble_path()
output_path = get_output_dir("current_results")

N_bootstrap = 1000
rl_years = [10, 20, 30]
hs_values = [3, 4, 5]

mkpath(output_path)

for rl_year in rl_years
    output_fp = joinpath(output_path, "bootstrap_results_$(rl_year).csv")

    @info "Retrieving data for $(rl_year) return level years"
    data = retrieve_data(ensemble_path, "returns_y$(rl_year)_best_model.bson.csv", :target, basename(output_path))

    @info "Starting bootstrap analysis for $(rl_year) return level years"
    bootstrap_results = bootstrap(data, N_bootstrap)

    @info "Writing bootstrap results to $(output_path)"
    write_to_csv(bootstrap_results, output_fp)
end


for hs in hs_values
    output_fp = joinpath(output_path, "bootstrap_results_$(hs)cm.csv")

    @info "Retrieving data for $(hs)cm"
    data = retrieve_data(ensemble_path, "returnperiod_$(hs)cm_best_model.bson.csv", :years, basename(output_path))

    @info "Starting bootstrap analysis for $(hs)cm"
    bootstrap_results = bootstrap(data, N_bootstrap)

    @info "Writing bootstrap results to $(output_path)"
    write_to_csv(bootstrap_results, output_fp)
end

@info "Bootstrap analysis completed successfully"
