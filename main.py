import gc
import uasyncio as asyncio
import time
from machine import ADC, Pin
import ulab

from util import Note, Motor

class Tone:
    VOLUME_THRESHOLD = 2000;
    
    def __init__(self, pin=0, buffer_size=512, Fs=2500):
        self.adc = ADC(pin)
        self.buffer_size = buffer_size
        self.Fs = Fs
        self.freq = 0
        self.volume = 0
        
    def get_sample_interval_us(self):
        return int(1_000_000 / self.Fs)

    async def fft(self):
        samparray = []
        start = time.ticks_us()
        for _ in range(self.buffer_size):
            samparray.append(self.adc.read())
            while time.ticks_diff(time.ticks_us(), start) < self.get_sample_interval_us() * (_ + 1):
                await asyncio.sleep_ms(0)

        end = time.ticks_us()

        self.real_Fs = self.buffer_size * 1_000_000 / time.ticks_diff(end, start)

        magnitudes = ulab.fft.spectrogram(ulab.array(samparray))
        idx = ulab.numerical.argmax(magnitudes[1:]) + 1
        
        self.freq = idx * self.real_Fs / self.buffer_size
        self.volume = magnitudes[idx]

        del samparray
        del magnitudes
        gc.collect()



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

async def fft_task(t):
    while True:
        await t.fft()
        await asyncio.sleep_ms(10)

async def motor_task(m, t):
    while True:
        n = Note(t.freq)
        if t.is_audible() and n.is_close():
            print("\nNote: {}({}), Freq: {}, Cent: {}, Volume: {}".format(n.name, n.value, t.freq, n.cent, t.volume), end="")
            await m.rotate("forward" if n.cent > 0 else "reverse", size=n.cent_per() * 0.3)
        else:
            # print("\nxxxxNote: {}({}), Freq: {}, Cent: {}, Volume: {}".format(n.name, n.value, t.freq, n.cent, t.volume), end="")
            print(".", end="")
        
        if m.is_pushed("forward"):
            await m.rotate("forward")
        elif m.is_pushed("reverse"):
            await m.rotate("reverse")
        else:
            m.stop()
        
        await asyncio.sleep_ms(50)
            
async def main():
    t = Tone()
    m = Motor(13, 2, 14, 12)
    await asyncio.gather(fft_task(t), motor_task(m, t))

asyncio.run(main())