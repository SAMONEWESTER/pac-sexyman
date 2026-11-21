import sys
from pathlib import Path


def asset_path(relative_path: str) -> str:
    """Transforms a path to make it relative to the ``assets`` directory.

    Parameters
    ----------
    relative_path : str
        Path within ``assets`` to transform.

    Returns
    -------
    str
        New path that was transformed.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return str(base_path / 'assets' / relative_path)
