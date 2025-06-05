import time
from machine import ADC, Pin
import ulab

from util import Note

class Tone:
    VOLUME_THRESHOLD = 3000;
    
    def __init__(self, pin=0, buffer_size=1024, Fs=2500):
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

        self.real_Fs = self.buffer_size * 1_000_000 / time.ticks_diff(end, start)

        magnitudes = ulab.fft.spectrogram(ulab.array(samparray))
        idx = ulab.numerical.argmax(magnitudes[1:]) + 1
        self.freq = idx * self.real_Fs / self.buffer_size
        self.volume = magnitudes[idx]
       
    def is_audible(self):
        return self.volume >= self.VOLUME_THRESHOLD
    
    def print_status(self):
        note, _, cent = Note.note(self.freq)
        print("{:.2f} Hz vol {} [{}] {} cent".format(
                self.freq,
                self.volume,
                note,
                cent
            ) if self.is_audible() else "."
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
        return self.sw[direction].value() == 0

    def rotate(self, direction):
        self.mo[direction].on()
        time.sleep(0.2)
        self.stop()

    def stop(self):
        self.mo["forward"].off()
        self.mo["reverse"].off()

if __name__ == "__main__":
    t = Tone()
    m = Motor(13, 2, 14, 12)

    while True:
        t.fft()
        n = Note(t.freq)
        if t.is_audible() and n.is_close():
            print("\nNote: {}({}), Freq: {}, Cent: {}, Volume: {}".format(n.name, n.value, t.freq, n.cent, t.volume), end="")
            m.rotate("forward" if n.cent > 0 else "reverse")
        else:
            # print("\nxxxxxNote: {}({}), Freq: {}, Cent: {}, Volume: {}".format(n.name, n.value, t.freq, n.cent, t.volume), end="")
            print(".", end="")
        
        if m.is_pushed("forward"):
            m.rotate("forward")
        elif m.is_pushed("reverse"):
            m.rotate("reverse")
        else:
            m.stop()