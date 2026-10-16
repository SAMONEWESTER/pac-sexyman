"""Converting between maze cells and pixel positions."""

from pygame import Vector2

from ..config import HALF_TILE, TILE_SIZE

Cell = tuple[int, int]
"""A maze cell as ``(x, y)``, counted in cells from the top left."""


def cell_center(cell: Cell) -> Vector2:
    """Return the pixel position of the center of a cell.

    Args:
        cell: The cell as ``(x, y)``.
    """
    return Vector2(cell[0] * TILE_SIZE + HALF_TILE,
                   cell[1] * TILE_SIZE + HALF_TILE)
