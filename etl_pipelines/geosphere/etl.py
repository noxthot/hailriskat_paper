import datetime
import glob
import multiprocessing as mp
import os
import pickle

from functools import partial

import dask.dataframe as dd
import h5py
import numpy as np
import pandas as pd
import xarray as xr

from scipy import ndimage
from tqdm import tqdm

import ccc

import utils

PATH_DATA = os.path.join(".", "data")
PATH_DATA_SOURCE = os.path.join(PATH_DATA, "raw_data")

PATH_DATA_PROCESSED = os.path.join(PATH_DATA, "processed_data")
PATH_DATA_TARGET = os.path.join(
    PATH_DATA_PROCESSED, 
    "dataparquet_" + datetime.date.today().strftime("%Y_%m_%d")
)

PATH_CACHE = os.path.join(".", "cache")  # Will be created

PATH_ALDIS = os.path.join(PATH_DATA_SOURCE, "aldis")  # Place where ALDIS data needs to be provided
PATH_ERA5 = os.path.join(PATH_DATA_SOURCE, "ERA5")  # Place where ERA5 data needs to be provided
PATH_INCA = os.path.join(PATH_DATA_SOURCE, "ZAMG", "covariables", "5_inca_final_corrected_by_9km")  # Place where INCA data needs to be provided

ALDIS_FROM_CACHE = False
CAPE_FROM_CACHE = False
INCA_FROM_CACHE = False

CACHE = {
    "inca": "etl_inca.pickle",
    "cape": "etl_cape.pickle",
    "aldis": "etl_aldis.pickle",
}


def transform(idx, path_year, data_lat, data_lon):
    allzamgdata = []
    filepaths = glob.glob(os.path.join(path_year, "**", "*.hdf"), recursive=True)
    year = path_year[-4:]

    for filepath in tqdm(filepaths, desc=year, position=idx):
        with h5py.File(filepath) as file:
            all_vars = []
            data = file["data_mehs_max"]["value"][:]  # INCA (internal source) already comes with calibrated MEHS

            if (data == 0).all():
                continue

            if int(year) > 2015:
                # Unfortunately data starts with 2mm after 2015 (prior it starts with 1mm). As discussed with vema,
                # we can safely subtract 1mm
                data -= 1
                data = np.maximum(np.zeros_like(data), data)  # Safety measure: Zeros stay zeros

            data_xr = xr.DataArray(
                data,
                coords=dict(
                    lon=(["y", "x"], data_lon),
                    lat=(["y", "x"], data_lat),
                ),
                dims=["y", "x"],
                name="data_mehs_orig",
            )

            all_vars.append(data_xr)

            group_keys = list(file.keys())[2:]

            for key in group_keys:
                if "data_mehs" in key or "data_poh" in key:
                    continue

                data = file[key]["value"][:]

                data_xr = xr.DataArray(
                    data,
                    coords=dict(
                        lon=(["y", "x"], data_lon),
                        lat=(["y", "x"], data_lat),
                    ),
                    dims=["y", "x"],
                    name=key,
                )

                all_vars.append(data_xr)

            df = xr.merge(all_vars).to_dataframe()

            df["has_mehs"] = df[[col for col in df.columns if ("data_mehs" in col)]].sum(axis=1)

            df.query("has_mehs > 0", inplace=True)

            df.drop('has_mehs', axis=1, inplace=True)

            df["timestamp"] = file["WHAT"].attrs["timestamp"]
            df["date"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
            allzamgdata.append(df)

    finaldf = pd.concat(allzamgdata).reset_index()

    return dd.from_pandas(finaldf, npartitions=8)


class ETL_GEOSPHERE:
    def execute():
        os.makedirs(PATH_DATA_TARGET, exist_ok=True)
        os.makedirs(PATH_CACHE, exist_ok=True)

        if INCA_FROM_CACHE:
            df_inca = pd.read_pickle(os.path.join(PATH_CACHE, CACHE["inca"]))
            print("INCA: loaded from cache", flush=True)
        else:
            with h5py.File(
                os.path.join(PATH_INCA, "lonlat.hdf")
            ) as lonlat_file:
                data_lat = lonlat_file["data_lat"]["value"][:]
                data_lon = lonlat_file["data_lon"]["value"][:]

            year_dirs = [p for p in os.listdir(PATH_INCA) if os.path.isdir(os.path.join(PATH_INCA, p))]
            year_dirs.sort()

            year_paths = [os.path.join(PATH_INCA, p) for p in year_dirs]

            print(
                f"INCA: READING AND TRANSFORMING {len(year_dirs)} years: {year_dirs}",
                flush=True,
            )

            with mp.Pool() as pool:
                dfdasks = pool.starmap(
                    partial(
                        transform,
                        data_lat=data_lat,
                        data_lon=data_lon,
                    ),
                    enumerate(year_paths),
                )

            df_inca = dd.concat(dfdasks)

            with open(os.path.join(PATH_CACHE, CACHE["inca"]), "wb") as handle:
                pickle.dump(df_inca, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if CAPE_FROM_CACHE:
            df_cape = pd.read_pickle(os.path.join(PATH_CACHE, CACHE["cape"]))
            print("CAPE: loaded from cache", flush=True)
        else:
            files = glob.glob(
                os.path.join(
                    PATH_ERA5,
                    "cape",
                    "*convective_available_potential_energy.nc",
                )
            )
            files.sort()

            print(f"CAPE: READING AND TRANSFORMING {len(files)} FILES", flush=True)

            df_inca_help = df_inca[["lon", "lat", "date"]].compute()
            df_inca_help["lon_rounded"] = utils.custom_round(
                df_inca_help["lon"] / ccc.CONVERSION_FACTOR_INCA, kernel_size=4
            )
            df_inca_help["lat_rounded"] = utils.custom_round(
                df_inca_help["lat"] / ccc.CONVERSION_FACTOR_INCA, kernel_size=4
            )

            cape_var = xr.open_mfdataset(files)

            df_cape_help = cape_var.resample(time="1D").max().to_dataframe().reset_index()

            df_cape_help.rename(columns={"time": "date", "longitude": "lon_rounded", "latitude": "lat_rounded"}, inplace=True)
            df_cape_help["date"] = df_cape_help["date"].apply(pd.to_datetime, utc=True)

            df_cape_help = df_inca_help.merge(
                                            df_cape_help,
                                            on=["lon_rounded", "lat_rounded", "date"]
            )

            df_cape_help.drop(columns=["lon_rounded", "lat_rounded"], inplace=True)

            df_cape = dd.from_pandas(df_cape_help, npartitions=8)

            with open(os.path.join(PATH_CACHE, CACHE["cape"]), "wb") as handle:
                pickle.dump(df_cape, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if ALDIS_FROM_CACHE:
            df_aldis = pd.read_pickle(os.path.join(PATH_CACHE, CACHE["aldis"]))
            print("ALDIS: loaded from cache", flush=True)
        else:
            files = glob.glob(os.path.join(PATH_ALDIS, "*.h5"))
            files.sort()
            print(f"ALDIS: READING AND TRANSFORMING {len(files)} FILES", flush=True)

            df_inca_help = df_inca[["lon", "lat", "date"]].compute()
            df_inca_help["lon_rounded"] = utils.custom_round(
                df_inca_help["lon"] / ccc.CONVERSION_FACTOR_INCA, kernel_size=10
            )
            df_inca_help["lat_rounded"] = utils.custom_round(
                df_inca_help["lat"] / ccc.CONVERSION_FACTOR_INCA, kernel_size=10
            )

            df = []
            for file in files:
                dictionary = {}
                with h5py.File(file, "r") as f:
                    for key in f.keys():
                        ds_arr = f[key][()]  # returns as a numpy array
                        dictionary[
                            key
                        ] = ds_arr  # appends the array in the dict under the key

                df.append(pd.DataFrame.from_dict(dictionary))

            df_aldis_help = pd.concat(df).reset_index()
            df_aldis_help["lon_rounded"] = utils.custom_round(
                df_aldis_help["laenge"] / ccc.CONVERSION_FACTOR_ALDIS,
                kernel_size=10,
            )
            df_aldis_help["lat_rounded"] = utils.custom_round(
                df_aldis_help["breite"] / ccc.CONVERSION_FACTOR_ALDIS,
                kernel_size=10,
            )
            df_aldis_help["date"] = pd.to_datetime(
                df_aldis_help["datetime"], unit="s", utc=True
            ).round("1D")
            df_aldis_help = (
                df_aldis_help.groupby(["date", "lat_rounded", "lon_rounded"])
                .agg({"amplitude": ["max"]})
                .reset_index()
            )
            df_aldis_help.columns = [
                "date",
                "lat_rounded",
                "lon_rounded",
                "amplitude",
            ]

            df_aldis_help = df_inca_help.merge(
                df_aldis_help, on=["lon_rounded", "lat_rounded", "date"], how="left"
            )
            df_aldis_help["amplitude"] = df_aldis_help["amplitude"].fillna(0)
            df_aldis_help.drop(columns=["lon_rounded", "lat_rounded"], inplace=True)

            df_aldis = dd.from_pandas(df_aldis_help, npartitions=8)

            with open(os.path.join(PATH_CACHE, CACHE["aldis"]), "wb") as handle:
                pickle.dump(df_aldis, handle, protocol=pickle.HIGHEST_PROTOCOL)

        print("Merging transformed dataframes", flush=True)

        joined_df = (
            df_inca.merge(df_cape, on=["lon", "lat", "date"])
            .merge(df_aldis, on=["lon", "lat", "date"])
        )

        print("WRITING TO PARQUET", flush=True)
        joined_df.to_parquet(
            PATH_DATA_TARGET,
            write_index=False,
            engine="pyarrow",
            compression="snappy",
        )
