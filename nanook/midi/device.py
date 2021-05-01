import mido


def get_ports(device_name):
    inputs = mido.get_input_names()
    input_name = next((p for p in inputs if p.find(device_name) > -1), None)
    if not input_name:
        raise IOError("Device not found")
    from_device = mido.open_input(input_name)

    outputs = mido.get_output_names()
    output_name = next((p for p in outputs if p.find(device_name) > -1), None)
    to_device = mido.open_output(output_name)
    to_device.send_sysex = lambda data: to_device.send(mido.Message("sysex", data=data))

    return from_device, to_device
