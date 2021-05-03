Nanook
======

This is a command line tool for managing scenes on the KORG nanoKONTROL Studio MIDI controller.

Features
--------

- select a scene, pretty-print scene data
- write scene data files (*.nktrl_st_data) to and from the device
- written in Python using Click, Mido and asyncio


How to use
----------

CAVEAT: As of now, the tool is very developer oriented. Ideally, at some point it should be packaged and distributed as a standalone executable.

```bash
# Install dependencies, get in virtual env
poetry install
poetry shell
python -m nanook --help

# select a scene
python -m nanook set SCENE_NUMBER  

# pretty-print the scene data
python -m nanook get SCENE_NUMBER

# load and write a scene data file to a given scene
python -m nanook write SCENE_NUMBER NKTRL_ST_DATA_FILE

# save a given scene to a file
python -m nanook save SCENE_NUMBER FILENAME
```

Bugs & missing stuff
--------------------

Yes.
