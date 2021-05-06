import mido
from .midi.device import get_ports

from_device, to_device = get_ports("nanoKONTROL")
from_editor = mido.open_input("Sniffer", virtual=True)


def callback_from_device(msg):
    if msg.type == "sysex":
        print("2 <-- ", msg)


from_device.callback = callback_from_device

for msg in from_editor:
    if msg.type == "sysex":
        print("1 --> ", msg)
        to_device.send(msg)
