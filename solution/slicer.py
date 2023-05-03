from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import typer
import xarray
from matplotlib.figure import Figure
from typing_extensions import Annotated

DENSITIES = {
    "air": (-1000, -900),
    "fat": (-100, -50),
    "fluid": (-50, 20),
    "white": (20, 30),
    "grey": (30, 50),
    "soft": (50, 300),
    "bone": (300, 1900),
    "heavy": (1900, 30000),
}


def find_max_idx(data: xarray.DataArray, axis: Literal["x", "y", "z"]) -> float:
    """Find the index label with highest bone content in the slice."""
    is_bone = (data > DENSITIES["bone"][0]) & (data < DENSITIES["bone"][1])
    dims = list({"x", "y", "z"} - {axis})
    return is_bone.sum(dims).idxmax()


def draw_slices(data: xarray.DataArray, **kwargs) -> Figure:
    """Draw three slices horizontally arranged."""
    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    for i, axis in enumerate(["x", "y", "z"]):
        idx = find_max_idx(data, axis)
        slice = data.sel(**{axis: idx}, method="nearest")
        slice.plot(**kwargs, ax=ax[i])
    return fig


def main(
    # Subtask: Define the input_path and output_path arguments
    input_path: Annotated[Path, typer.Argument(help="File to read from")],
    output_path: Annotated[Path, typer.Argument(help="File to write to")] = Path(
        "plot.png"
    ),
    # Subtask: Define arguments you want the user to be able to specify
    vmin: Annotated[
        float, typer.Option(help="Max HU value to be shown as black")
    ] = -100,
    vmax: Annotated[
        float, typer.Option(help="Min HU value to be shown as white")
    ] = 1000,
    cmap: Annotated[str, typer.Option(help="Colormap to use")] = "gist_gray",
    segmented: Annotated[
        bool,
        typer.Option(help="If true, different tissues will be having solid colors"),
    ] = False,
):
    """Draw three plots with sagittal, coronal and axial slices of CT images.

    It puts them all next to each other and stores them into a file.
    """

    # Load the data
    data = xarray.load_dataarray(input_path) - 1000

    # Use the `levels`` argument to separate the various tissue types
    if segmented:
        levels = [
            DENSITIES[k][0]
            for k in ["air", "fat", "fluid", "white", "grey", "soft", "bone"]
        ] + [DENSITIES["bone"][1]]
    else:
        levels = None

    fig = draw_slices(data, vmin=vmin, vmax=vmax, cmap=cmap, levels=levels)

    # Save the figure
    fig.tight_layout()
    fig.savefig(output_path)


if __name__ == "__main__":
    typer.run(main)
