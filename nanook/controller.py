import asyncio
import sys
from .midi.device import get_ports
from .midi.constants import *
from .midi.utils import *


class Controller:
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
