from synth.oscillators import SineOscillator
from synth.synths import Synthesizer
from synth.windows import hanning_window


class DoubleSineSynthesizer(Synthesizer):
    """
    Synth overlaying two sine waves, with the second one being a bit quieter and lower.
    Sounds very similar to the single sine one honestly
    """
    def __init__(self, sampling_rate, duration, volume_multiplier=0.5, frequency_multiplier=0.5):
        super().__init__(sampling_rate, duration)
        self.oscillator = SineOscillator(self.fs, self.duration)
        self.oscillator2 = SineOscillator(self.fs, self.duration, volume_multiplier, frequency_multiplier)
        self.window = hanning_window  
    
    def get_waveform(self, frequency, volume):
        """
        Gets the waveform, taking the average of the two oscillators.
        The average is important becaues otherwise it is possible to get louder than 1.0.
        """
        volume = self.get_volume(volume)
        frequency = self.get_frequency(frequency)

        if frequency is None or volume is None:
            return # nothing I can do
        
        samples1 = self.oscillator(frequency)
        samples2 = self.oscillator2(frequency)
        window = self.window(len(samples1), volume)
        return (samples1 + samples2) * window/2
