import logging
from typing import List

from cassandra.cluster import Session
import matplotlib
# See http://matplotlib.org/faq/usage_faq.html#what-is-a-backend for details
# TODO: use this: https://stackoverflow.com/a/37605654/7851470
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from alcor.models.star import Star
from alcor.services.data_access.reading import fetch


logger = logging.getLogger(__name__)


UV_FILENAME = 'heatmap_uv.ps'
UW_FILENAME = 'heatmap_uw.ps'
VW_FILENAME = 'heatmap_vw.ps'

FIGURE_SIZE = (8, 8)
DESIRED_DIMENSIONS_RATIO = 10 / 13
SUBPLOTS_SPACING = 0.25
FIGURE_GRID_HEIGHT_RATIOS = [0.05, 1]

COLORMAP = cm.get_cmap('jet')
COLORMAP.set_under('w')

U_LABEL = '$U(km/s)$'
V_LABEL = '$V(km/s)$'
W_LABEL = '$W(km/s)$'
VELOCITIES_BINS_COUNT = 150

# TODO: find out the meaning of this
VMIN = 0.01

# TODO: in what reference frame?
PECULIAR_SOLAR_VELOCITY_U = -11
PECULIAR_SOLAR_VELOCITY_V = 12
PECULIAR_SOLAR_VELOCITY_W = 7


def plot(*,
         session: Session,
         axes: str) -> None:
    # TODO: Figure out what stars I should fetch (all/last group by time/last N
    # groups by time/selected by ID/marked by some flag(series of simulations))
    stars = fetch_all_stars(session=session)

    # TODO: add coordinates
    if axes == 'velocities':
        # TODO: add choosing frame: relative to Sun/LSR. Now it's rel. to LSR
        # TODO: how to work with Decimal type? If I leave it I get:
        # TypeError: Cannot cast array data from dtype('O') to dtype('float64')
        # according to the rule 'safe'
        velocities_u = [float(star.velocity_u) + PECULIAR_SOLAR_VELOCITY_U
                        for star in stars]
        velocities_v = [float(star.velocity_v) + PECULIAR_SOLAR_VELOCITY_V
                        for star in stars]
        velocities_w = [float(star.velocity_w) + PECULIAR_SOLAR_VELOCITY_W
                        for star in stars]

        # TODO: add option of plotting 3 heatmaps in one fig. at the same time
        draw_plot(xlabel=U_LABEL,
                  ylabel=V_LABEL,
                  xdata=velocities_u,
                  ydata=velocities_v,
                  filename=UV_FILENAME)
        draw_plot(xlabel=U_LABEL,
                  ylabel=W_LABEL,
                  xdata=velocities_u,
                  ydata=velocities_w,
                  filename=UW_FILENAME)
        draw_plot(xlabel=V_LABEL,
                  ylabel=W_LABEL,
                  xdata=velocities_v,
                  ydata=velocities_w,
                  filename=VW_FILENAME)


def fetch_all_stars(*,
                    session: Session):
    query = (Star.objects.all().limit(None))
    records = fetch(query=query,
                    session=session)
    return [Star(**record)
            for record in records]


def draw_plot(*,
              xlabel: str,
              ylabel: str,
              xdata: List[float],
              ydata: List[float],
              filename: str) -> None:
    figure, (colorbar, subplot) = plt.subplots(
        nrows=2,
        figsize=FIGURE_SIZE,
        gridspec_kw={"height_ratios": FIGURE_GRID_HEIGHT_RATIOS})

    # TODO: add sliders
    subplot.set(xlabel=xlabel,
                ylabel=ylabel)

    heatmap, xedges, yedges = np.histogram2d(x=xdata,
                                             y=ydata,
                                             bins=VELOCITIES_BINS_COUNT)
    extent = [xedges[0], xedges[-1],
              yedges[0], yedges[-1]]

    colorbar_src = subplot.imshow(X=heatmap.T,
                                  cmap=COLORMAP,
                                  vmin=VMIN,
                                  extent=extent,
                                  origin='lower')

    plt.minorticks_on()

    subplot.xaxis.set_ticks_position('both')
    subplot.yaxis.set_ticks_position('both')

    figure.colorbar(mappable=colorbar_src,
                    cax=colorbar,
                    orientation="horizontal")

    subplot.set_aspect(DESIRED_DIMENSIONS_RATIO
                       / subplot.get_data_ratio())

    figure.subplots_adjust(hspace=SUBPLOTS_SPACING)

    plt.savefig(filename)