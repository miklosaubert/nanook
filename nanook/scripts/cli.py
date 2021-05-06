import asyncio
import sys
import click
import uvloop
from aioconsole import ainput, aprint
from nanook import Controller, Scene
from nanook.nktrl_st_file import (
    load_scene_data,
    load_scene_set,
    save_scene_data,
    save_scene_set,
)


async def cli_loop(controller):
    await aprint(
        "Welcome back to the Nanook command line. Send commands to your nanoKONTROL Studio from here"
    )
    while True:
        cmd = await ainput("nanook> ")
        if cmd == "p":
            result = await controller.get_scene(1)
            await aprint(result)
        if cmd.startswith("s "):
            try:
                scene_number = int(cmd.split(" ")[1])
                if scene_number not in [1, 2, 3, 4, 5]:
                    raise Exception("Scene number must be between 1 and 5")
                await controller.select_scene(scene_number)
                await aprint(f"Scene {scene_number} selected.")
            except Exception:
                await aprint(
                    f"Couldn't select scene: {sys.exc_info()[0]}", use_stderr=True
                )


async def dispatch_command(controller, command, scene, filename):
    if command == "select":
        await controller.select_scene(scene)
    elif command == "print":
        result = await controller.get_scene(scene)
        print(Scene(result))
    elif command == "save":
        dump = await controller.get_scene(scene)
        save_scene_data(filename, bytes(dump))
    elif command == "save-set":
        dumps = []
        for scene in range(1, 6):
            dumps.append(bytes(await controller.get_scene(scene)))
        save_scene_set(filename, dumps)
    elif command == "write":
        dump = load_scene_data(filename)
        result = await controller.write_scene(scene, dump)
        print(result)
    elif command == "write-set":
        dumps = load_scene_set(filename)
        for scene in range(1, 6):
            result = await controller.write_scene(scene, dumps[scene - 1])
            print(result)


async def async_main(interactive=False, command=None, scene=None, filename=None):
    try:
        controller = Controller()
    except OSError:
        print(sys.exc_info()[1], file=sys.stderr)
    else:
        if interactive:
            await asyncio.gather(controller.listen(), cli_loop(controller))
        else:
            task = asyncio.create_task(controller.listen())
            await dispatch_command(controller, command, scene, filename)
            task.cancel()


def async_runner(interactive=False, command=None, scene=None, filename=None):
    uvloop.install()
    asyncio.run(async_main(interactive, command, scene, filename))


@click.group(name="nanook")
def main() -> None:
    pass


@main.command("print", help="Print a scene")
@click.argument("scene", required=True, type=click.IntRange(1, 5))
def nanook_print(scene):
    async_runner(command="print", scene=scene)


@main.command("select", help="Select a scene")
@click.argument("scene", required=True, type=click.IntRange(1, 5))
def nanook_select(scene):
    async_runner(command="select", scene=scene)


@main.command("save", help="Save a scene to a file")
@click.argument("scene", required=True, type=click.IntRange(1, 5))
@click.argument("file", required=True, type=click.Path(writable=True))
def nanook_save(scene, file):
    async_runner(command="save", scene=scene, filename=file)


@main.command("save-set", help="Save the complete scene set to a file")
@click.argument("file", required=True, type=click.Path(writable=True))
def nanook_save_set(file):
    async_runner(command="save-set", filename=file)


@main.command("write", help="Write a scene data file to the device")
@click.argument("scene", required=True, type=click.IntRange(1, 5))
@click.argument("file", required=True, type=click.Path(readable=True))
def nanook_write(scene, file):
    async_runner(command="write", scene=scene, filename=file)


@main.command("write-set", help="Write a complete scene set to the device")
@click.argument("file", required=True, type=click.Path(readable=True))
def nanook_write_set(file):
    async_runner(command="write-set", filename=file)


@main.command("shell", help="Open a nanook shell")
def nanook_shell():
    async_runner(interactive=True)


main()
