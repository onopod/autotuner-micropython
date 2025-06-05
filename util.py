import math

class Note:
    A4 = 440.0
    TARGET_NOTES = [
        ["E2", 82.407],
        ["A2", 110],
        ["D3", 146.832],
        ["G3", 195.998],
        ["B3", 246.942],
        ["E4", 329.628],
    ]
    CENT_MIN_THRESHOLD = 12
    CENT_MAX_THRESHOLD = 130

    
    @classmethod
    def get_cent_diff(cls, target, freq):
        return 1200 * (math.log(freq / target) / math.log(2))

    def __init__(self, freq):
        self.freq = freq
        cents = [[name, value, Note.get_cent_diff(value, freq)] for name, value in Note.TARGET_NOTES]
        self.name, self.value, self.cent =  sorted(cents, key=lambda e: abs(e[2]))[0]
    
    def is_close(self):
        return self.CENT_MIN_THRESHOLD <= abs(self.cent) <= self.CENT_MAX_THRESHOLD
