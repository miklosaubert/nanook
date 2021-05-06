# Nanook

This is a command line tool for managing scenes on the KORG nanoKONTROL Studio MIDI controller.

## Features

- select a scene, pretty-print scene data
- write scene data files (\*.nktrl_st_data) to and from the device
- written in Python using Click, Mido and asyncio

## Installation

```bash
pip install nanook
```

## Usage

```bash
nanook --help

# select a scene
nanook select SCENE_NUMBER

# pretty-print the scene data
nanook print SCENE_NUMBER

# load and write a scene data file to a given scene
nanook write SCENE_NUMBER NKTRL_ST_DATA_FILE

# save a given scene to a file
nanook save SCENE_NUMBER FILENAME

# load and write a scene set file to the device
nanook write-set NKTRL_ST_SET_FILE

# save the current scene set to a file
nanook save-set FILENAME
```


## Development

Clone this repository and use [poetry](https://python-poetry.org/docs/) to install dependencies.

```bash
# Install dependencies
poetry install

# Get in virtual env. From this shell, you will be running your local copy of nanook
poetry shell
```

## Bugs & missing stuff

Yes.
