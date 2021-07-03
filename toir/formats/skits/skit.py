import struct
from ...text import decode_text_fixed, remove_redundant_cc, decode_text

class SkitText:
    pass

class SkitLine(SkitText):
    def __init__(self, speakers, text, speakerName=None):
        self.speakers = speakers
        self.text = text
        self.speakerName = speakerName

class SkitChoices(SkitText):
    def __init__(self, choices):
        self.choices = choices

class Skit:
    def __init__(self, skit_dat):
        self.dat = skit_dat

    def extract_text(self):
        self.speakers = self._extract_speakers()
        lines = self._extract_lines()
        return self.speakers, lines

    def _extract_speakers(self):
        speaker_count = self.dat[4]
        speaker_base, = struct.unpack_from('<L', self.dat, 8)
        speakers = []
        for i in range(speaker_count):
            length, offset = struct.unpack_from('<HL', self.dat, speaker_base + i * 0x10 + 10)
            text = decode_text_fixed(self.dat, offset, length - 1)
            speakers.append(text)
        return speakers

    def _extract_lines(self):
        base, = struct.unpack_from('<L', self.dat, 12)
        count, = struct.unpack_from('<B', self.dat, 6)
        i = 0
        texts = []
        while i < count:
            offset, = struct.unpack_from('<L', self.dat, base + i * 4)
            opcode = self.dat[offset]
            if opcode == 0x17:
                texts.append(self._extract_line(offset))
            elif opcode == 0x1F:
                texts.append(self._extract_choices(offset))
            elif opcode == 0x22:
                i += 1
            i += 1
        return texts

    def _extract_line(self, offset):
        speaker, flag, length, speakerOffset, line_offset = struct.unpack_from('<H3xB2xH4xLL', self.dat, offset + 2)
        tempSpeaker = None
        if flag != 0:
            tempSpeaker = decode_text(self.dat, speakerOffset)
        text = decode_text_fixed(self.dat, line_offset, length)
        return SkitLine(speaker, remove_redundant_cc(text), tempSpeaker)

    def _extract_choices(self, offset):
        count, = struct.unpack_from('B', self.dat, offset + 1)
        choices = []
        for i in range(count):
            choice_offset, = struct.unpack_from('<L', self.dat, offset + 4 + i * 4)
            text = decode_text(self.dat, choice_offset)
            choices.append(remove_redundant_cc(text))
        return SkitChoices(choices)


def skit_extract_text(skit_dat):
    return Skit(skit_dat).extract_text()