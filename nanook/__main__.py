#! /usr/bin/env python

import asyncio
import sys
from .midi.device import get_ports
from .midi.constants import *
from .midi.utils import *
from .scene import Scene


class Nanook:
    def __init__(self):
        loop = asyncio.get_event_loop()
        msg_queue = asyncio.Queue(maxsize=1)
        from_nano, to_nano = get_ports("nanoKONTROL Studio")
        sysex_future: asyncio.Future = None

        def midi_callback(message):
            nonlocal loop, msg_queue
            if message.type == "sysex":
                loop.call_soon_threadsafe(msg_queue.put_nowait, message)

        from_nano.callback = midi_callback

        async def send_sysex(data):
            nonlocal sysex_future, loop, to_nano
            if sysex_future != None and not sysex_future.done():
                raise Exception("A SYSEX message is already in flight")
            # Create a new Future to sync our message with its answer
            sysex_future = loop.create_future()
            to_nano.send_sysex(data)
            return await sysex_future

        async def listen():
            nonlocal msg_queue, sysex_future
            while True:
                msg = await msg_queue.get()
                payload = extract_payload(msg.data)
                if sysex_future != None and not sysex_future.done():
                    if payload == NAK:
                        sysex_future.set_exception(
                            Exception("Received NAK from device")
                        )
                    else:
                        sysex_future.set_result(payload)
                else:
                    if payload[:-1] == SCENE_CHANGED_EVENT:
                        scene_number = payload[-1] + 1
                        print(f"Scene was changed to {scene_number} on device.")
                    else:
                        print(
                            "Received an unexpected SYSEX message", msg, file=sys.stderr
                        )

        self.__send_sysex = send_sysex
        self.listen = listen

    async def _send_command(self, command):
        await self.__send_sysex(UNIVERSAL_SYSEX_INQUIRY)
        return await self.__send_sysex(SYSEX_HEADER + command)

    async def get_scene(self, scene_number):
        await self.select_scene(scene_number)
        midi = await self._send_command(CMD_GET_CURRENT_SCENE_DATA)
        dump = scene_dump_from_midi(midi[4:])
        return dump

    async def select_scene(self, scene_number):
        await self._send_command(CMD_UNKNOWN_1)
        return await self._send_command(CMD_SELECT_SCENE(scene_number))

    async def write_scene(self, scene_number, scene_dump):
        await self._send_command(CMD_UNKNOWN_1)
        await self._send_command(
            CMD_SCENE_DATA_TRANSFER + midi_from_scene_dump(scene_dump)
        )
        if ACK_WRITE != await self._send_command(
            CMD_STORE_EDIT_BUFFER_TO_SCENE(scene_number)
        ):
            raise Exception("Failed to write scene data.")
        return f"Scene data successfully written to scene {scene_number}"


if __name__ == "__main__":
    import click
    import uvloop
    from aioconsole import ainput, aprint
    from .nktrl_st_file import *

    async def cli_loop(nano):
        await aprint(
            "Welcome back to the Nanook command line. Send commands to your nanoKONTROL Studio from here"
        )
        while True:
            cmd = await ainput("nanook> ")
            if cmd == "p":
                result = await nano.get_scene(1)
                await aprint(result)
            if cmd.startswith("s "):
                try:
                    scene_number = int(cmd.split(" ")[1])
                    if scene_number not in [1, 2, 3, 4, 5]:
                        raise Exception("Scene number must be between 1 and 5")
                    await nano.select_scene(scene_number)
                    await aprint(f"Scene {scene_number} selected.")
                except:
                    await aprint(
                        f"Couldn't select scene: {sys.exc_info()[0]}", use_stderr=True
                    )

    async def dispatch_command(nano, command, scene, filename):
        if command == "select":
            await nano.select_scene(scene)
        elif command == "print":
            result = await nano.get_scene(scene)
            print(Scene(result))
        elif command == "write":
            dump = load_scene_data(filename)
            result = await nano.write_scene(scene, dump)
            print(result)
        elif command == "save":
            dump = await nano.get_scene(scene)
            write_scene_data(filename, bytes(dump))

    async def async_main(interactive=False, command=None, scene=None, filename=None):
        try:
            nano = Nanook()
        except OSError:
            print(sys.exc_info()[1], file=sys.stderr)
        else:
            if interactive:
                await asyncio.gather(nano.listen(), cli_loop(nano))
            else:
                task = asyncio.create_task(nano.listen())
                await dispatch_command(nano, command, scene, filename)
                task.cancel()

    def async_runner(interactive=False, command=None, scene=None, filename=None):
        uvloop.install()
        asyncio.run(async_main(interactive, command, scene, filename))

    @click.group()
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

    @main.command("write", help="Write a scene data file to the device")
    @click.argument("scene", required=True, type=click.IntRange(1, 5))
    @click.argument("file", required=True, type=click.Path(readable=True))
    def nanook_write(scene, file):
        async_runner(command="write", scene=scene, filename=file)

    @main.command("shell", help="Open a nanook shell")
    def nanook_shell():
        async_runner(interactive=True)

    main()