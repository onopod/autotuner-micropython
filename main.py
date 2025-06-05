import time
from machine import ADC, Pin
import ulab

from util import frequency_to_note

class Tone:
    def __init__(self, pin=0, buffer_size=1024, Fs=8000):
        self.adc = ADC(pin)
        self.buffer_size = buffer_size
        self.Fs = Fs
    
    def get_sample_interval_us(self):
        return int(1_000_000 / self.Fs)

    def fft(self):
        samparray = []
        start = time.ticks_us()
        for _ in range(self.buffer_size):
            samparray.append(self.adc.read())
            while time.ticks_diff(time.ticks_us(), start) < self.get_sample_interval_us() * (_ + 1):
                pass
        end = time.ticks_us()
        actual_sample_time_us = time.ticks_diff(end, start)
        Fs = self.buffer_size * 1_000_000 / actual_sample_time_us  # 実測Fs

        samparray = ulab.array(samparray)
        magnitudes = ulab.fft.spectrogram(samparray)
        idx = ulab.numerical.argmax(magnitudes[1:]) + 1
        freq = idx * Fs / self.buffer_size
        
        note, cents = frequency_to_note(freq)
        sign = "+" if cents >= 0 else ""

        self.values = {
            "freq": freq,
            "power": magnitudes[idx],
            "note": note,
            "sign": sign,
            "cents": cents
        }
        
    def print_status(self):
        print("\nFrequency: {:.2f} Hz power {} [{}] {}{} cent".format(
                self.values["freq"],
                self.values["power"],
                self.values["note"],
                self.values["sign"],
                self.values["cents"]
            ) if self.values["power"] >= 4000 else "."
          , end="")

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
        print(self.sw[direction].value())
        return self.sw[direction].value() == 0

    def rotate(self, direction):
        self.mo[direction].on()

    def stop(self):
        self.mo["forward"].off()
        self.mo["reverse"].off()

if __name__ == "__main__":
    t = Tone()
    m = Motor(13, 2, 14, 12)

    m.rotate("forward")
    time.sleep(0.5)
    m.stop()    
    m.rotate("reverse")
    time.sleep(0.5)
    m.stop()    

    while True:
        t.fft()
        t.print_status()
        
        if m.is_pushed("forward"):
            m.rotate("forward")
        elif m.is_pushed("reverse"):
            m.rotate("reverse")
        else:
            m.stop()