
from utils import todo


def synth_factory(name, sampling_rate, duration):
    match name:
        case "sine":
            from synth.sine_synth import SineSynthesizer
            return SineSynthesizer(sampling_rate, duration)
        case "double_sine":
            from synth.double_sine_synth import DoubleSineSynthesizer
            return DoubleSineSynthesizer(sampling_rate, duration)
        case _:
            todo(f"Synth '{name}' not implemented")
    

class Synthesizer:
    """
    A base class for synthesizers. Takes the duration of each note, 
    and stores frequency and volume.
    """
    def __init__(self, sampling_rate, duration):
        self.fs = sampling_rate
        self.duration = duration
        self.previous_frequency = None
        self.previous_volume = None
    
    def get_volume(self, volume):
        """
        Caches the volume so that if this volume is none, it returns the cached value.
        """
        if volume is None and self.previous_volume is not None:
            volume = self.previous_volume
        else :
            self.previous_volume = volume
        return volume
    
    def get_frequency(self, frequency):
        """
        Caches the frequency so that if this frequency is none, it returns the cached value.
        """
        if frequency is None and self.previous_frequency is not None:
            frequency = self.previous_frequency
        else :
            self.previous_frequency = frequency
        return frequency