from synth.oscillators import SineOscillator
from synth.synths import Synthesizer
from synth.windows import hanning_window


class SineSynthesizer(Synthesizer):
    """
    Single sine wave synth.
    """

    def __init__(self, sampling_rate, duration):
        super().__init__(sampling_rate, duration)
        self.oscillator = SineOscillator(self.fs, self.duration)
        self.window = hanning_window  
        
    def get_waveform(self, frequency, volume):
        """
        Returns a waveform using the oscillator and window.
        """

        volume = self.get_volume(volume)
        frequency = self.get_frequency(frequency)

        if frequency is None or volume is None:
            return # nothing I can do
        
        samples = self.oscillator(frequency)
        window = self.window(len(samples), volume)
        return samples * window