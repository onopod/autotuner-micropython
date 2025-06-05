import uasyncio as asyncio
import math
from machine import ADC, Pin

class Motor:
    def __init__(self, sw_f, sw_r, mo_f, mo_r):
        self.sw = {
            "forward": Pin(sw_f, Pin.IN, Pin.PULL_UP),
            "reverse": Pin(sw_r, Pin.IN, Pin.PULL_UP)
        }
        self.mo = {
            "forward": Pin(mo_f, Pin.OUT),
            "reverse": Pin(mo_r, Pin.OUT)
        }
    
    def is_pushed(self, direction):
        return self.sw[direction].value() == 0

    async def rotate(self, direction, size=0.1):
        self.mo[direction].on()
        await asyncio.sleep(size)
        self.stop()

    def stop(self):
        self.mo["forward"].off()
        self.mo["reverse"].off()

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
    CENT_MIN_THRESHOLD = 30
    CENT_MAX_THRESHOLD = 130

    def cent_per(self):
        return (abs(self.cent) - self.CENT_MIN_THRESHOLD) / (self.CENT_MAX_THRESHOLD - self.CENT_MIN_THRESHOLD)
    
    @classmethod
    def get_cent_diff(cls, target, freq):
        return 1200 * (math.log(freq / target) / math.log(2))

    def __init__(self, freq):
        self.freq = freq
        cents = [[name, value, Note.get_cent_diff(value, freq)] for name, value in Note.TARGET_NOTES]
        self.name, self.value, self.cent =  sorted(cents, key=lambda e: abs(e[2]))[0]
    
    def is_close(self):
        return self.CENT_MIN_THRESHOLD <= abs(self.cent) <= self.CENT_MAX_THRESHOLD
