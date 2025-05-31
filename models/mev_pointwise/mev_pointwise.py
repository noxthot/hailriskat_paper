import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import swifter

from datetime import date
from mpl_toolkits.basemap import Basemap
from multiprocess import Pool
from scipy import stats

import ccc
import models.mev_pointwise.mev_pointwise_utils as mev_pointwise_utils
import models.mev_pointwise.mev_pointwise_utils_ui as utils_ui

PATH_DATA = os.path.join('.', 'data')
PATH_DATA_PROCESSED = os.path.join(PATH_DATA, 'processed_data')
PATH_DATA_MODELS = os.path.join(PATH_DATA, 'models', 'mev_pointwise')

DIR_DATABUNDLE = 'dataparquet_2023_12_20'


class MEV:
    def execute():
        config_model = utils_ui.ask_model_cfg()

        path_save = os.path.join(PATH_DATA_MODELS, f"{date.today()}", config_model["target"])
        os.makedirs(path_save, exist_ok=True)

        config_model["databundle"] = DIR_DATABUNDLE

        with open(os.path.join(path_save, "config.json"), "w") as outfile:
            json.dump(config_model, outfile, indent=4, sort_keys=True)

        distr = config_model['distribution']
        method = config_model['method']
        data = pd.read_parquet(os.path.join(PATH_DATA_PROCESSED, DIR_DATABUNDLE), engine='pyarrow')

        print("TRANSFORMING", flush=True)

        data['breite'] = data['lat'] / ccc.CONVERSION_FACTOR_INCA
        data['laenge'] = data['lon'] / ccc.CONVERSION_FACTOR_INCA

        data.query(f'{config_model["target"]} > 0', inplace=True)
        target_col_agg = f'{config_model["target"]}_max'

        print(f"GROUP DATA AND AGGREGATE {config_model['target']}", flush=True)
        dzamgfull = data.groupby(['date', 'breite', 'laenge']).agg({config_model["target"]:['max']}).reset_index()
        dzamgfull.columns = ['date', 'latitude', 'longitude', target_col_agg]
        dzamgfull[target_col_agg] = dzamgfull[target_col_agg].astype(float)

        num_years = len(pd.to_datetime(dzamgfull['date']).dt.year.unique())
        print(f"{num_years} years available")

        print("Fit the distribution parameters", flush=True)
        xdat = dzamgfull.groupby(['latitude', 'longitude'])[target_col_agg].apply(list).reset_index()
        xdat['Mean'] = xdat[target_col_agg].apply(np.mean)
        xdat['totals'] = xdat[target_col_agg].apply(len)
        xdat['n'] = xdat['totals'] / num_years

        xdat.drop(xdat[xdat['totals'] < config_model['threshold']].index, inplace=True)

        for return_period in config_model['return_periods']:
            print(f"Processing return period of {return_period} years", flush=True)

            p = 1 - 1 / return_period

            if distr == 'weibull':
                if method == 'PWM':
                    xdat['M1'] = xdat[target_col_agg].swifter.apply(mev_pointwise_utils.M1)
                    logratio = np.log(xdat['Mean'] / xdat['M1'])
                    xdat['C'] = xdat['Mean'] / (logratio / np.log(2)).swifter.apply(math.gamma)
                    xdat['k'] = np.log(2) / (logratio - np.log(2))
                elif method == 'MLE':
                    pool = Pool()
                    xdat['k'], xdat['C'], xdat['vcov'] = zip(*pool.map(mev_pointwise_utils.paramest, xdat[target_col_agg]))
                else:
                    raise Exception(f"Method {distr} not recognized")

                print("Compute return values", flush=True)
                xdat['RL'] = xdat['C'] * (-np.log(1 - p**(1 / xdat['n'])))**(1 / xdat['k'])

                if method == 'MLE':
                    print("Compute standard errors", flush=True)
                    xdat['rl_diff'] = xdat.swifter.apply(lambda x: mev_pointwise_utils.rl_grad(p, x['C'], x['k'], x['n']), axis=1)
                    xdat['RL_sd'] = np.sqrt(xdat.swifter.apply(lambda x: mev_pointwise_utils.weighted_inner(x['rl_diff'], x['vcov']), axis=1))
                    xdat['RL_upperCI'] = xdat['RL'] + 2 * xdat['RL_sd']
                    xdat['RL_lowerCI'] = xdat['RL'] - 2 * xdat['RL_sd']
            elif distr == "lognorm":
                xdat['params'] = xdat[target_col_agg].swifter.apply(stats.lognorm.fit, floc=0)
                xdat['RL'] = stats.lognorm.ppf(p**(1 / xdat['n']), s=xdat['params'].str[0], scale=xdat['params'].str[2])
            else:
                raise Exception(f"Distribution {distr} not supported")

            print("Prepare data for plotting", flush=True)

            if (distr == 'weibull' and method == 'MLE'):
                xdat['Uncertainty'] = (xdat['RL_upperCI'] - xdat['RL_lowerCI']) / xdat['RL']
                df_pv = xdat[['latitude', 'longitude', 'RL', 'RL_lowerCI', 'RL_upperCI', 'Uncertainty']]
            else:
                df_pv = xdat[['latitude', 'longitude', 'RL']]

            path_save_rl = os.path.join(path_save, f"{return_period}")
            os.makedirs(path_save_rl, exist_ok=True)

            for col in [c for c in df_pv.columns if "RL" in c]:
                df_pv.loc[:, col] /= 10  # mm to cm

            df_pv.to_csv(os.path.join(path_save_rl, f"return_levels_y{return_period}.csv"))
            columns_to_plot = [c for c in df_pv.columns if (("RL" in c) or (c == "Uncertainty"))]

            print("Save return levels plots", flush=True)

            for col in columns_to_plot:
                print(f"Processing {col}", flush=True)
                
                plt.figure(figsize = (15, 10))

                # initialize the Basemap
                m = Basemap(projection='lcc', resolution='f', lat_0=47.5, lon_0=13.3, width=0.6E6, height=3.7E5)
                m.drawmapboundary()
                m.drawcountries(linewidth=2)

                vmin = 1 if "RL" in col else None
                vmax = 6 if "RL" in col else None

                m.scatter(df_pv['longitude'], df_pv['latitude'], c=df_pv[col], cmap="jet", s=0.5, latlon=True, vmin=vmin, vmax=vmax)

                plt.colorbar(label='MEHS', extend="max")
                plt.title(col)

                plt.savefig(os.path.join(path_save_rl, f"hailriskat_{col}_y{return_period}.pdf"), bbox_inches="tight")
                plt.savefig(os.path.join(path_save_rl, f"hailriskat_{col}_y{return_period}.png"), bbox_inches="tight")

                plt.close()

        print("FIN", flush=True)
