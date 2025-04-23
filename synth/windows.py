import numpy as np


def hanning_window(length, volume):
    """
    A hanning window to prevent popping.
    Vaguely bell shaped
    """
    window = np.hanning(length).astype(np.float32)

    return window * volume

def rect_window(length, volume):
    """
    Rectangular window. Sounds very chiptune-y.
    """
    fade_duration = 0.002
    fade_samples = int(length * fade_duration)
    base = np.ones(length).astype(np.float32) * volume
    base[:fade_samples] = np.linspace(0, volume, fade_samples)
    base[-fade_samples:] = np.linspace(volume, 0, fade_samples)
    return base