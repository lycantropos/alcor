import logging
from typing import Tuple

import matplotlib

# More info at
# http://matplotlib.org/faq/usage_faq.html#what-is-a-backend for details
# TODO: use this: https://stackoverflow.com/a/37605654/7851470
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import pandas as pd

from alcor.services.common import PECULIAR_SOLAR_VELOCITY_V
logger = logging.getLogger(__name__)


def plot(stars: pd.DataFrame,
         *,
         filename: str = 'toomre_diagram.ps',
         figure_size: Tuple[float, float] = (8, 8),
         ratio: float = 10 / 13,
         xlabel: str = '$V(km/s)$',
         ylabel: str = '$\sqrt{U^2+W^2}(km/s)$',
         thin_disk_color: str = 'r',
         thick_disk_color: str = 'b') -> None:
    # TODO: add choosing frame: relative to Sun/LSR. Now it's rel. to LSR
    # TODO: check how to work with categorical data in pandas
    thin_disk_stars = stars[stars['galactic_disk_type'] == 'thin']
    thick_disk_stars = stars[stars['galactic_disk_type'] == 'thick']

    figure, subplot = plt.subplots(figsize=figure_size)
    plot_stars_by_galactic_disk_type(subplot=subplot,
                                     stars=thin_disk_stars,
                                     color=thin_disk_color)
    plot_stars_by_galactic_disk_type(subplot=subplot,
                                     stars=thick_disk_stars,
                                     color=thick_disk_color)

    # TODO: add sliders
    subplot.set(xlabel=xlabel,
                ylabel=ylabel)

    plt.minorticks_on()

    subplot.xaxis.set_ticks_position('both')
    subplot.yaxis.set_ticks_position('both')

    subplot.set_aspect(ratio / subplot.get_data_ratio())

    plt.savefig(filename)


def plot_stars_by_galactic_disk_type(*,
                                     subplot: Axes,
                                     stars: pd.DataFrame,
                                     color: str,
                                     point_size: float = 0.5) -> None:
    stars['v_velocity'] += PECULIAR_SOLAR_VELOCITY_V
    uw_velocities_magnitudes = np.sqrt(np.power(stars['u_velocity'], 2)
                                       + np.power(stars['w_velocity'], 2))

    subplot.scatter(x=stars['v_velocity'],
                    y=uw_velocities_magnitudes,
                    color=color,
                    s=point_size)
