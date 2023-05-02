# Create a script using typer that will find the x, y and z slices with the highest
# fraction of gray mass and plot them into separate files

import typer
import xarray
from pathlib import Path
import matplotlib.pyplot as plt


DENSITIES = {
    "air": (-1000, -900),
    "fat": (-100, -50),
    "fluid": (-50, 20),
    "white": (20, 30),
    "grey": (30, 50),
    "soft": (50, 300),
    "bone": (300, 1900),
    "heavy": (1900, 30000)
}


def find_max_idx(data, axis):
    is_bone = (data > DENSITIES["bone"][0]) & (data < DENSITIES["bone"][1])
    dims = list({"x","y", "z"} - {axis})
    return is_bone.sum(dims).idxmax()


def physio_plot2(data, axis, value, ax):
    slice = data.sel(**{axis: value})
    slice.plot(cmap="gist_gray", vmin=-100, vmax=1000, ax=ax)


def plot_three_planes(data, **kwargs):
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    for i, axis in enumerate(["x", "y", "z"]):
        idx = find_max_idx(data, axis)
        slice = data.sel(**{axis: idx})
        slice.plot(**kwargs, ax=ax[i])
    return fig


def main(
    input_path: Path,
    output_path: Path = Path("plot.png"),
    # Subtask: Define arguments you want the user to be able to specify
    vmin: float = -100,
    vmax: float = 1000,
    cmap: str = "gist_gray",
    segmented: bool = False,
):
    # Load the data
    data = xarray.load_dataarray(input_path) - 1000

    # Bonus: Use the levels argument to separate the various tissue types
    if segmented:
        levels = [
            DENSITIES[k][0] for k in ["air", "fat", "fluid", "white", "grey", "soft", "bone"]
        ] + [DENSITIES["bone"][1]]
    else:
        levels = None

    fig = plot_three_planes(data, vmin=vmin, vmax=vmax, cmap=cmap, levels=levels)
    fig.tight_layout()
    fig.savefig(output_path)


if __name__ == "__main__":
    typer.run(main)