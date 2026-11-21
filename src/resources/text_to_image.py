from pygame import Surface, SRCALPHA

from .assets import ASSETS


def text_to_image(text: str) -> Surface:
    """Render a string of text into a single image.

    Parameters
    ----------
    text: str
        The text to render.

    Returns
    -------
    Surface
        A new surface with the text drawn on it.
    """
    width = sum(ASSETS.font.get(c, ASSETS.font[' ']).get_width() for c in text)
    result = Surface((width, 16), flags=SRCALPHA)
    x = 0
    for c in text:
        char_image = ASSETS.font.get(c, ASSETS.font[' '])
        result.blit(char_image, (x, 0))
        x += char_image.get_width()
    return result
