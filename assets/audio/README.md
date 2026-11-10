# Audio

| Folder   | What goes here                              |
|----------|---------------------------------------------|
| `music/` | One looping track per level (`level_01.ogg` ...) |
| `sfx/`   | Short sound effects (`dot_eaten.ogg` ...)   |

File names and volumes are set in `src/audio/sounds.py`.
To swap a sound, drop the file in the right folder and change its name there.

Use `.ogg` where possible: it is small and loops without a gap.
`.wav` also works for sound effects, `.mp3` for music.

A missing file is skipped with a warning, the game still runs.
The full list of missing files is in `pac-man.log`.
