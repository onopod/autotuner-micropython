import math

def frequency_to_note(freq):
    A4 = 440.0
    if freq <= 0:
        return None, 0

    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    semitones = round(12 * math.log(freq / A4, 2))
    nearest_freq = A4 * 2 ** (semitones / 12)
    cents = 1200 * math.log(freq / nearest_freq, 2)

    octave = 4 + (semitones + 9) // 12
    note_index = (semitones + 9) % 12

    return "{}{}".format(note_names[note_index], octave), round(cents)