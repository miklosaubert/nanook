from collections import namedtuple

NUM_KNOBS = 8
NUM_FADERS = 8
NUM_BUTTONS = 44

OFFSET_COMMON = 0
OFFSET_KNOBS = OFFSET_COMMON + 16
OFFSET_FADERS = OFFSET_KNOBS + NUM_KNOBS * 8
OFFSET_BUTTONS = OFFSET_FADERS + NUM_FADERS * 8
OFFSET_JOG_WHEEL = OFFSET_BUTTONS + NUM_BUTTONS * 8 + 16

Common = namedtuple("Common", ["Scene_Name", "LED_Mode"])
Knob = namedtuple(
    "Knob", ["MIDI_Channel", "Enable", "CC_Number", "Left_Value", "Right_Value"]
)
Fader = namedtuple(
    "Fader", ["MIDI_Channel", "Enable", "CC_Number", "Lower_Value", "Upper_Value"]
)
Button = namedtuple(
    "Button",
    [
        "MIDI_Channel",
        "Assign_Type",
        "Note_CC_Number",
        "Off_Value",
        "On_Value",
        "Behaviour",
    ],
)
JogWheel = namedtuple(
    "JogWheel",
    [
        "MIDI_Channel",
        "Type",
        "Acceleration",
        "Sign_Magnitude_CC_Number",
        "Inc_Dec_CW_CC_Number",
        "Inc_Dec_CCW_CC_Number",
        "Continuous_CC_Number",
        "Continuous_Min_Value",
        "Continuous_Max_Value",
    ],
)


class Scene:
    def __init__(self, scene_dump):
        self.common = Common("".join(map(chr, scene_dump[0:12])), scene_dump[12])
        self.knobs = []
        self.faders = []
        self.buttons = []
        for i in range(OFFSET_KNOBS, OFFSET_FADERS, 8):
            self.knobs.append(Knob(*scene_dump[i : i + 5]))
        for i in range(OFFSET_FADERS, OFFSET_BUTTONS, 8):
            self.faders.append(Fader(*scene_dump[i : i + 5]))
        for i in range(OFFSET_BUTTONS, OFFSET_BUTTONS + NUM_BUTTONS * 8, 8):
            self.buttons.append(Button(*scene_dump[i : i + 6]))
        self.jog_wheel = JogWheel(*scene_dump[OFFSET_JOG_WHEEL : OFFSET_JOG_WHEEL + 9])

    def dump(self):
        def pad8(b):
            excess = len(b) % 8
            padding = (8 - excess) % 8
            return b + bytes([255] * padding)

        def dump_controls_array(controls_array):
            return b"".join([pad8(bytes(c)) for c in controls_array])

        return (
            pad8(bytes(self.common.Scene_Name, "ascii") + bytes([self.common.LED_Mode]))
            + dump_controls_array(self.knobs)
            + dump_controls_array(self.faders)
            + dump_controls_array(self.buttons)
            + bytes([255] * 16)
            + pad8(bytes(self.jog_wheel))
            + bytes([255] * 32)
        )

    def __repr__(self):
        return (
            f"\nScene Name: {self.common.Scene_Name}, LED Mode: {'Internal' if self.common.LED_Mode == 0 else 'External'}\n"
            + "\nKnobs:\n"
            + "".join(
                [
                    f"  {i+1}. \tMIDI Channel: {self.knobs[i].MIDI_Channel}, Enable: {self.knobs[i].Enable == 1}, CC Number: {self.knobs[i].CC_Number}, Left Value: {self.knobs[i].Left_Value}, Right Value: {self.knobs[i].Right_Value}\n"
                    for i in range(len(self.knobs))
                ]
            )
            + "\nFaders:\n"
            + "".join(
                [
                    f"  {i+1}. \tMIDI Channel: {self.faders[i].MIDI_Channel}, Enable: {self.faders[i].Enable == 0}, CC Number: {self.faders[i].CC_Number}, Lower Value: {self.faders[i].Lower_Value}, Upper Value: {self.faders[i].Upper_Value}\n"
                    for i in range(len(self.faders))
                ]
            )
            + "\nButtons:\n"
            + "".join(
                [
                    f"  {i+1}. \tMIDI Channel: {self.buttons[i].MIDI_Channel}, Assign Type: {self.buttons[i].Assign_Type}, Note/CC Number: {self.buttons[i].Note_CC_Number}, Off Value: {self.buttons[i].Off_Value}, On Value: {self.buttons[i].On_Value}\n"
                    for i in range(len(self.buttons))
                ]
            )
            + f"\nJog Wheel:\n\tMIDI Channel: {self.jog_wheel.MIDI_Channel}, Type: {self.jog_wheel.Type}, Acceleration: {self.jog_wheel.Acceleration}"
            + f"\n\tSign Magnitude:\n\t\tCC Number: {self.jog_wheel.Sign_Magnitude_CC_Number}"
            + f"\n\tInc/Dec:\n\t\tCW CC Number: {self.jog_wheel.Inc_Dec_CW_CC_Number}, CCW CC Number: {self.jog_wheel.Inc_Dec_CCW_CC_Number}"
            + f"\n\tContinuous:\n\t\tCC Number: {self.jog_wheel.Continuous_CC_Number}, Continuous Min Value: {self.jog_wheel.Continuous_Min_Value}, Continuous Max Value: {self.jog_wheel.Continuous_Max_Value}"
        )
