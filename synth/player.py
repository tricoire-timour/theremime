import pyaudio

from synth.synths import synth_factory


class Player:
    """
    Plays audio, based on the synth set in __init__
    """
    def __init__(self, type="sine", duration=0.19):
        self.p = pyaudio.PyAudio()
        self.fs = 44100  # sampling rate, Hz, must be integer
        self.synth = synth_factory(type, self.fs, duration)
        self.duration = duration
        self.stream = self.p.open(format=pyaudio.paFloat32,
                                channels=1,
                                rate=self.fs,
                                output=True)


    def play_note(self, frequency, volume):
        """
        Plays a single note.
        """
        waveform = self.synth.get_waveform(frequency, volume)
        if waveform is None:
            return
        output_bytes = (waveform).tobytes() 
        self.stream.write(output_bytes)

    def __del__(self):
        """
        take care of everything when killing the object.
        """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()