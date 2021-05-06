import nanook.midi.constants as MIDI


def has_header(sysex_data, header):
    header_length = len(header)
    return len(sysex_data) > header_length and sysex_data[0:header_length] == header


def extract_payload(sysex_data):
    if has_header(sysex_data, MIDI.INQUIRY_RESPONSE_HEADER):
        return sysex_data[MIDI.INQUIRY_RESPONSE_HEADER_LENGTH :]
    if has_header(sysex_data, MIDI.SYSEX_HEADER):
        return sysex_data[MIDI.SYSEX_HEADER_LENGTH :]


def midi_from_scene_dump(dump):
    midi = []
    for i in range(0, len(dump), 7):
        msbs = sum([(dump[i + j] >> 7) << j for j in range(0, 7)])
        lsbs = [dump[i + j] & 127 for j in range(0, 7)]
        midi.append(msbs)
        midi += lsbs
    return tuple(midi)


def scene_dump_from_midi(midi):
    dump = []
    for i in range(0, len(midi), 8):
        msbs = [1 & (midi[i] >> j) for j in range(0, 7)]
        dump += [128 * msbs[j] + midi[i + j + 1] for j in range(0, 7)]
    return tuple(dump)
