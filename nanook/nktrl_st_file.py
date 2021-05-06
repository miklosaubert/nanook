SCENE_SET_MAGIC = bytes("1482ScnS", "ascii")
SCENE_SET_FILE_HEADER = SCENE_SET_MAGIC + bytes(
    (
        32,
        0,
        144,
        11,
        0,
        0,
        0,
        0,
        0,
        0,
        255,
        255,
        5,
        0,
        0,
        0,
        48,
        2,
        0,
        0,
        255,
        255,
        255,
        255,
    )
)
SCENE_SET_FILE_HEADER_SIZE = len(SCENE_SET_FILE_HEADER)
SCENE_DATA_MAGIC = bytes("1482ScnD", "ascii")
SCENE_DATA_FILE_HEADER = SCENE_DATA_MAGIC + bytes(
    (
        32,
        0,
        48,
        2,
        0,
        0,
        0,
        0,
        0,
        0,
        255,
        255,
        1,
        0,
        0,
        0,
        48,
        2,
        0,
        0,
        255,
        255,
        255,
        255,
    )
)
SCENE_DATA_FILE_HEADER_SIZE = len(SCENE_DATA_FILE_HEADER)
SCENE_DATA_SIZE = 560


def load_scene_set(filename):
    with open(filename, "rb") as file:
        if file.read(8) != SCENE_SET_MAGIC:
            raise Exception("Not a scene set file")
        # Skip over the scene set header
        file.seek(SCENE_SET_FILE_HEADER_SIZE)
        scene_set = []
        for i in range(5):
            # Skip over the scene data header
            file.read(SCENE_DATA_FILE_HEADER_SIZE)
            scene_set.append(file.read(SCENE_DATA_SIZE))
        return scene_set


def save_scene_set(filename, scene_set):
    with open(filename, "wb") as file:
        file.write(SCENE_SET_FILE_HEADER)
        for i in range(len(scene_set)):
            file.write(SCENE_DATA_FILE_HEADER)
            file.write(scene_set[i])


def load_scene_data(filename):
    with open(filename, "rb") as file:
        if file.read(8) != SCENE_DATA_MAGIC:
            raise Exception("Not a scene data file")
        file.seek(SCENE_DATA_FILE_HEADER_SIZE)
        scene_data = file.read(SCENE_DATA_SIZE)
        return scene_data


def save_scene_data(filename, data):
    with open(filename, "wb") as file:
        file.write(SCENE_DATA_FILE_HEADER)
        file.write(data)
