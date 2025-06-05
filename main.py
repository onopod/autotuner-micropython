import time
from machine import ADC
import ulab

from util import frequency_to_note

adc = ADC(0)
buffer_size = 1024
Fs = 8000  # 目標サンプリング周波数 [Hz]
sample_interval_us = int(1_000_000 / Fs)  # マイクロ秒単位のサンプリング間隔

while True:
    samparray = []
    start = time.ticks_us()
    for _ in range(buffer_size):
        samparray.append(adc.read())
        while time.ticks_diff(time.ticks_us(), start) < sample_interval_us * (_ + 1):
            pass
    end = time.ticks_us()
    actual_sample_time_us = time.ticks_diff(end, start)
    Fs = buffer_size * 1_000_000 / actual_sample_time_us  # 実測Fs

    samparray = ulab.array(samparray)
    magnitudes = ulab.fft.spectrogram(samparray)
    idx = ulab.numerical.argmax(magnitudes[1:]) + 1
    freq = idx * Fs / buffer_size
    
    if 4000 <= magnitudes[idx]:
        note, cents = frequency_to_note(freq)
        sign = "+" if cents >= 0 else ""
        print("\nFrequency: {:.2f} Hz power {} [{}] {}{} cent".format(freq, magnitudes[idx], note, sign, cents), end="")
    else:
        print(".", end="")

    # print("Index {}: Frequency {:.1f} Hz power {:.1f} (Fs {:.1f} Hz)".format(idx, freq, magnitudes[idx], Fs))
