import numpy as np
import pyaudio


class SineOscillator:
    def __init__(self, sample_rate, duration, frequency_factor=1, volume_factor=1):
        self.fs = sample_rate  
        self.duration = duration
        self.frequency_factor = frequency_factor
        self.volume_factor = volume_factor

    def __call__(self, frequency):
        return (np.sin(2 * np.pi * np.arange(self.fs * self.duration) * frequency * self.frequency_factor / self.fs)).astype(np.float32) * self.volume_factor
    
def hanning_window(length, volume):
    window = np.hanning(length).astype(np.float32)

    return window * volume

def rect_window(length, volume):
    fade_duration = 0.002
    fade_samples = int(length * fade_duration)
    base = np.ones(length).astype(np.float32) * volume
    base[:fade_samples] = np.linspace(0, volume, fade_samples)
    base[-fade_samples:] = np.linspace(volume, 0, fade_samples)
    return base

class Synthesizer:
    def __init__(self, sampling_rate, duration):
        self.fs = sampling_rate
        self.duration = duration
        self.previous_frequency = None
        self.previous_volume = None
    
    def get_volume(self, volume):
        if volume is None and self.previous_volume is not None:
            volume = self.previous_volume
        else :
            self.previous_volume = volume
        return volume
    
    def get_frequency(self, frequency):
        if frequency is None and self.previous_frequency is not None:
            frequency = self.previous_frequency
        else :
            self.previous_frequency = frequency
        return frequency

class SineSynthesizer(Synthesizer):
    def __init__(self, sampling_rate, duration):
        super().__init__(sampling_rate, duration)
        self.oscillator = SineOscillator(self.fs, self.duration)
        self.window = hanning_window  
        
    def get_waveform(self, frequency, volume):
        volume = self.get_volume(volume)
        frequency = self.get_frequency(frequency)

        if frequency is None or volume is None:
            return # nothing I can do
        
        samples = self.oscillator(frequency)
        window = self.window(len(samples), volume)
        return samples * window

class DoubleSineSynthesizer(Synthesizer):
    def __init__(self, sampling_rate, duration):
        super().__init__(sampling_rate, duration)
        self.oscillator = SineOscillator(self.fs, self.duration)
        self.oscillator2 = SineOscillator(self.fs, self.duration, 0.5, 0.5)
        self.window = hanning_window  
    
    def get_waveform(self, frequency, volume):
        volume = self.get_volume(volume)
        frequency = self.get_frequency(frequency)

        if frequency is None or volume is None:
            return # nothing I can do
        
        samples1 = self.oscillator(frequency)
        samples2 = self.oscillator2(frequency)
        window = self.window(len(samples1), volume)
        return (samples1 + samples2) * window/2

class Player:
    def __init__(self, duration=0.19):
        self.p = pyaudio.PyAudio()
        self.fs = 44100  # sampling rate, Hz, must be integer
        self.synth = DoubleSineSynthesizer(self.fs, duration)
        self.duration = duration
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                channels=1,
                                rate=self.fs,
                                output=True)


    def play_note(self, frequency, volume):
        waveform = self.synth.get_waveform(frequency, volume)
        if waveform is None:
            return
        output_bytes = (waveform).tobytes() 
        self.stream.write(output_bytes)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()