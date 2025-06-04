using CSV
using DataFrames
using Statistics


function bootstrap_statistics(data::Vector{Float64})
    std1_val = std(data)

    return Dict(
        "mean" => mean(data),
        "median" => median(data),
        "std1" => std1_val,
        "std2" => 2 * std1_val,
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

    for (coord, values) in data
        means = Float32[]
        medians = Float32[]

        for _ in 1:N
            sample = rand(values, length(values))
            push!(means, mean(sample))
            push!(medians, median(sample))
        end

        mean_mean = mean(means)
        median_median = median(medians)
        std_mean = std(means)
        std_median = std(medians)

        bootstrap_results[coord] = Dict(
                                    "mean" => mean_mean,
                                    "mean_1std" => std_mean,
                                    "mean_2std" => 2 * std_mean,
                                    "mean_1lc" => max(mean_mean - std_mean, 0),
                                    "mean_1uc" => mean_mean + std_mean,
                                    "mean_2lc" => max(mean_mean - 2 * std_mean, 0),
                                    "mean_2uc" => mean_mean + 2 * std_mean,
                                    "median" => median_median,
                                    "median_1std" => std_median,
                                    "median_2std" => 2 * std_median,
                                    "median_1lc" => max(median_median - std_median, 0),
                                    "median_1uc" => median_median + std_median,
                                    "median_2lc" => max(median_median - 2 * std_median, 0),
                                    "median_2uc" => median_median + 2 * std_median,
        )
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

ensemble_path = joinpath("data", "models", "mev_nn", "final_ensemble")
output_dir = "results"

N_bootstrap = 1000
rl_years = [10, 20, 30]
hs_values = [3, 4, 5]

output_path = joinpath(ensemble_path, output_dir)

mkpath(output_path)

for rl_year in rl_years
    output_fp = joinpath(output_path, "bootstrap_results_$(rl_year).csv")

    @info "Retrieving data for $(rl_year) return level years"
    data = retrieve_data(ensemble_path, "returns_y$(rl_year)_best_model.bson.csv", :target, output_dir)

    @info "Starting bootstrap analysis for $(rl_year) return level years"
    bootstrap_results = bootstrap(data, N_bootstrap)

    @info "Writing bootstrap results to $(output_path)"
    write_to_csv(bootstrap_results, output_fp)
end


for hs in hs_values
    output_fp = joinpath(output_path, "bootstrap_results_$(hs)cm.csv")

    @info "Retrieving data for $(hs)cm"
    data = retrieve_data(ensemble_path, "returnperiod_$(hs)cm_best_model.bson.csv", :years, output_dir)

    @info "Starting bootstrap analysis for $(hs)cm"
    bootstrap_results = bootstrap(data, N_bootstrap)

    @info "Writing bootstrap results to $(output_path)"
    write_to_csv(bootstrap_results, output_fp)
end

@info "Bootstrap analysis completed successfully"
