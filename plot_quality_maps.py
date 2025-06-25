import glob
import os

import cmasher as cmr
import matplotlib as mpl
import matplotlib.image as mplimg
import matplotlib.pyplot as plt
import numpy as np

from datetime import datetime
from enum import Enum
from matplotlib.colors import ListedColormap, BoundaryNorm


class PLOT_CATEGORY(Enum):
    ONE_COLUMN_TWO_PLOTS = 0,
    TWO_COLUMNS_ONE_PLOT = 1,

DPI = 300

FILE_PLOT_SETTINGS = {
    "map_beam_height_min": {
        "colorbar_categorical": False,
        "colorbar_orientation": "vertical",
        "colorbar_reverse": True,
        "extend": "max",
        "figure_category": PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT,
        "filename": "f01",
        "label": "height (m)",
        "show_radar": True,
        "vmax": 5000,
        "vmin": 0,
    },
    "map_qual_beam_height_min": {
        "colorbar_categorical": False,
        "colorbar_orientation": "horizontal",
        "colorbar_reverse": False,
        "extend": "neither",
        "figure_category": PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS,
        "filename": "fappxB01a",
        "label": "quality",
        "show_radar": True,
        "vmax": 1,
        "vmin": 0,
    },
    "map_qual_beam_volume": {
        "colorbar_categorical": False,
        "colorbar_orientation": "horizontal",
        "colorbar_reverse": False,
        "extend": "neither",
        "figure_category": PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS,
        "filename": "fappxB01c",
        "label": "quality",
        "show_radar": True,
        "vmax": 1,
        "vmin": 0,
    },
    "map_qual_hext": {
        "colorbar_categorical": False,
        "colorbar_orientation": "horizontal",
        "colorbar_reverse": False,
        "extend": "neither",
        "figure_category": PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS,
        "filename": "fappxB01b",
        "label": "quality",
        "show_radar": True,
        "vmax": 1,
        "vmin": 0,
    },
    "map_qual_radar_hail_indicator": {
        "colorbar_categorical": False,
        "colorbar_orientation": "horizontal",
        "colorbar_reverse": False,
        "extend": "neither",
        "figure_category": PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS,
        "filename": "fappxB01d",
        "label": "quality",
        "show_radar": True,
        "vmax": 1,
        "vmin": 0,
    },
    "map_qual_return_period": {
        "colorbar_categorical": False,
        "colorbar_orientation": "vertical",
        "colorbar_reverse": False,
        "extend": "neither",
        "figure_category": PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT,
        "filename": "fappxB03",
        "label": "quality",
        "show_radar": False,
        "vmax": 1,
        "vmin": 0,
    },
    "map_qual_return_period_categories": {
        "colorbar_categorical": True,
        "colorbar_orientation": "vertical",
        "colorbar_reverse": False,
        "extend": "neither",
        "figure_category": PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT,
        "filename": "f02",
        "label": "quality",
        "show_radar": False,
        "vmax": 5,
        "vmin": 1,
    },
}

PATH_QUALITYMAPS_INPUT = os.path.join("data", "geosphere_plots", "quality_maps", "input")
PATH_QUALITYMAPS_OUTPUT = os.path.join("data", "geosphere_plots", "quality_maps", "output", datetime.now().strftime("%Y%m%d_%H%M%S"))


def plot_map(data_map, input_filename, fn_save, file_plot_settings, bgmap=None, fgmap=None):
    colorbar_orientation = file_plot_settings.get(input_filename, {}).get("colorbar_orientation", "horizontal")
    colorbar_reverse = file_plot_settings.get(input_filename, {}).get("colorbar_reverse", False)
    colorbar_categorical = file_plot_settings.get(input_filename, {}).get("colorbar_categorical", False)
    extend = file_plot_settings.get(input_filename, {}).get("extend", "neither")
    fn_save = os.path.join(PATH_QUALITYMAPS_OUTPUT, file_plot_settings.get(input_filename, {}).get("filename", f"{input_filename}_quality_map"))
    label = file_plot_settings.get(input_filename, {}).get("label", None)
    plot_type = file_plot_settings.get(input_filename, {}).get("figure_category", PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT)
    show_radar = file_plot_settings.get(input_filename, {}).get("show_radar", False)
    vmax = file_plot_settings.get(input_filename, {}).get("vmax", None)
    vmin = file_plot_settings.get(input_filename, {}).get("vmin", None)
    
    if vmax is None:
        vmax = np.nanmax(data_map)
    
    if vmin is None:
        vmin = np.nanmin(data_map)

    if plot_type not in [PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS, PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT]:
        raise ValueError(f"Invalid plot type: {plot_type}. Expected ONE_COLUMN_TWO_PLOTS or TWO_COLUMNS_ONE_PLOT.")

    if plot_type == PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS:
        plt.rcParams.update({'font.size': 18})
    elif plot_type == PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT:
        plt.rcParams.update({'font.size': 35})
    
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)
    ax.set_axis_off()

    cmap_name = f'plasma{"_r" if colorbar_reverse else ""}'
    cmap_quality = cmr.get_sub_cmap(cmap_name, 0.05, 0.9)

    if colorbar_categorical:
        nr_colors = (vmax - vmin) + 1
        colors = [cmap_quality(i / nr_colors) for i in range(nr_colors)]
        cmap_quality = ListedColormap(colors)
        bounds = np.arange(vmin - 0.5, vmax + 1.5)
        norm = BoundaryNorm(bounds, cmap_quality.N)
        ticks = np.arange(vmin, vmax + 1)
    else:
        bounds = None
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        ticks = None

    cmap_quality.set_extremes(over=plt.colormaps.get_cmap(cmap_name)(1.0))

    X, Y = np.meshgrid(np.arange(data_map.shape[1] + 1), np.arange(data_map.shape[0] + 1))

    if bgmap is not None:
        ax.imshow(bgmap, extent=[0, data_map.shape[1], 0, data_map.shape[0]], interpolation='gaussian', origin='upper')

    ax.pcolormesh(X, Y, np.ma.array(data_map, mask=np.isnan(data_map)), alpha=0.6, cmap=cmap_quality, norm=norm)

    if show_radar and (fgmap is not None):
        ax.imshow(fgmap, extent=[0, data_map.shape[1], 0, data_map.shape[0]], interpolation='gaussian', origin='upper', zorder=10)

    print('Save %s' %(fn_save), flush=True)
    plt.savefig(f"{fn_save}.png", bbox_inches='tight', dpi=DPI)
    plt.close()

    if plot_type == PLOT_CATEGORY.ONE_COLUMN_TWO_PLOTS:
        plt.rcParams.update({'font.size': 10})
    elif plot_type == PLOT_CATEGORY.TWO_COLUMNS_ONE_PLOT:
        plt.rcParams.update({'font.size': 20})

    if colorbar_orientation == "horizontal":
        fig = plt.figure(figsize=(8, 3))
        ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.05])
    elif colorbar_orientation == "vertical":
        fig = plt.figure(figsize=(3, 8))
        ax1 = fig.add_axes([0.05, 0.80, 0.2, 0.9])
    else:
        raise ValueError(f"Invalid colorbar orientation: {colorbar_orientation}. Expected 'horizontal' or 'vertical'.")

    cb1 = mpl.colorbar.ColorbarBase(
                                        ax1,
                                        boundaries=bounds,
                                        cmap=cmap_quality,
                                        extend=extend,
                                        format='%1i' if colorbar_categorical else None,
                                        norm=norm,
                                        orientation=colorbar_orientation,
                                        ticks=ticks,
    )

    if label is not None:
        cb1.set_label(label)

    plt.savefig(f"{fn_save}_cmap.pdf", bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    os.makedirs(PATH_QUALITYMAPS_OUTPUT, exist_ok=True)

    bgmap = mplimg.imread(os.path.join(PATH_QUALITYMAPS_INPUT, "bg_ATNT.png"))
    fgmap = mplimg.imread(os.path.join(PATH_QUALITYMAPS_INPUT, "fg_ATNT_radars.png"))

    # Iterate over all .txt files in PATH_QUALITYMAPS_INPUT
    for txt_path in glob.glob(os.path.join(PATH_QUALITYMAPS_INPUT, "*.txt")):
        print(f"Processing {txt_path}", flush=True)
        data_map = np.genfromtxt(txt_path, autostrip=True, delimiter=" ", skip_header=2)
        input_filename = os.path.splitext(os.path.basename(txt_path))[0]

        plot_map(data_map, input_filename, PATH_QUALITYMAPS_OUTPUT, FILE_PLOT_SETTINGS, bgmap=bgmap, fgmap=fgmap)
        print("", flush=True)
