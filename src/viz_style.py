import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from config import FIGURES

PALETTE = ["#6C4CF1", "#B24CF1", "#F14CB2", "#F1786C", "#F1B24C"]
PRIMARY = "#6C4CF1"
HIGHLIGHT = "#F14CB2"
NEUTRAL_GRAYS = ["#9B9BAB", "#B7B7C4", "#D0D0DA", "#E2E2E9", "#F0F0F4"]
TEXT = "#2B2B33"
GRID = "#E5E5EC"
BACKGROUND = "#FFFFFF"
FONT_STACK = ["Inter", "Helvetica Neue", "Segoe UI", "DejaVu Sans"]


def configure_matplotlib():
    matplotlib.rcParams.update({
        "figure.facecolor": BACKGROUND,
        "axes.facecolor": BACKGROUND,
        "savefig.facecolor": BACKGROUND,
        "axes.edgecolor": TEXT,
        "axes.labelcolor": TEXT,
        "text.color": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "font.family": "sans-serif",
        "font.sans-serif": FONT_STACK,
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "savefig.dpi": 300,
    })


def palette_colormap():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("lima_gradient", PALETTE)


def save_fig(fig, name):
    path = FIGURES / name
    fig.savefig(str(path), dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  {path}")
    return path


def style_ax(ax, xlabel=None, ylabel=None, title=None, subtitle=None):
    ax.set_facecolor(BACKGROUND)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if subtitle:
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes,
                fontsize=10, color=GRID, va="bottom", ha="left")
