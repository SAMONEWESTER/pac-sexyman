"""The game's own exception classes.

All of them inherit from ``PacManError``, so one ``except PacManError``
catches every error the game raises on purpose. When wrapping a lower
level error, raise with ``from`` so the report can show the cause::

    except OSError as err:
        raise AssetError("cannot load image 'x.png'") from err
"""


class PacManError(Exception):
    """Base class for every error the game raises on purpose.

    Attributes:
        show_trace: Whether the error report lists where in the code the
            error happened. Turned off for errors caused by user input,
            where a code location would not help anyone.
    """

    show_trace: bool = True


class UsageError(PacManError):
    """The program was started with the wrong command-line arguments."""

    show_trace = False


class ConfigError(PacManError):
    """The config file is missing, unreadable or not valid JSON."""

    show_trace = False


class AssetError(PacManError):
    """An image or font is missing or unusable."""


class DisplayError(PacManError):
    """The game window could not be created."""


class MazeError(PacManError):
    """The external maze generator failed."""
