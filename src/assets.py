from pathlib import Path

import pygame


IMG: dict[str, pygame.Surface] = {}


def load_assets(dir: Path) -> None:
    """Load all assets from a directory, including its subdirectories.
    Only loads `.png` files.
    Assets are put into the `IMG` dict, inside the containing module.
    The image key is the filepath, excluding `assets/` and `.png`."""
    for file in dir.iterdir():
        if file.is_dir():
            load_assets(file)
        else:
            if file.suffix not in {'.png', '.jpg', '.jpeg', '.gif'}:
                continue
            IMG.update({
                str(file).removeprefix('assets/').removesuffix(file.suffix):
                    pygame.image.load(file).convert_alpha()})
