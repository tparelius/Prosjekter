import math
import wave
import numpy as np


def ensure_mono(f):
    if f.getnchannels() != 1:
        raise Exception("One of the audio files is stereo. Use only mono. Problem: " + path)


def ensure_8_bit(f):
    if f.getsampwidth() != 1:
        raise Exception("All the files must have sample width=1. If not, the call to frombuffer must be modified.")


def check_framerate(f, frame_rate):
    fr = f.getframerate()
    if frame_rate is None or fr == frame_rate:
        return fr
    elif fr != frame_rate:
        raise Exception("All the files must have same frame rate (sampling frequancy).")


def find_least_length(f, min_num_samples):
    n = f.getnframes()
    if min_num_samples is None:
        return n
    else:
        return min(n, min_num_samples)


def investigate_file(path, frame_rate, min_num_samples):
    with wave.open(path, mode='rb') as f:
        ensure_mono(f)
        ensure_8_bit(f)
        frame_rate = check_framerate(f, frame_rate)
        min_num_samples = find_least_length(f, min_num_samples)
    return frame_rate, min_num_samples


def investigate_files(paths):
    """Check that the files are suitable."""
    min_num_samples = None
    frame_rate = None
    for path in paths:
        frame_rate, min_num_samples = investigate_file(path, frame_rate, min_num_samples)
    return frame_rate, min_num_samples


def read_wave_file(path, num_samples):
    with wave.open(path, mode='rb') as f:
        n = f.getnframes()
        # Read the middle of the file.
        num_samples_to_discard = math.floor((n - num_samples)/2)
        f.setpos(num_samples_to_discard)
        data = f.readframes(num_samples)
    return data


def read_wavefiles(paths):
    frame_rate, min_num_samples = investigate_files(paths)
    result = np.empty((len(paths), min_num_samples))
    for i, path in enumerate(paths):
        data = read_wave_file(path, min_num_samples)
        signal = np.frombuffer(data, dtype=np.uint8)
        result[i, :] = signal
    # Transform from [0,255] to [-1, 1].
    result = (2. * result) / 255. - 1.
    return result, frame_rate

## And the other way around:
def write_wavefiles(data, frame_rate, paths):
    data = np.array(np.round(((data + 1) * 255) / 2), dtype="uint8")
    for i, path in enumerate(paths):
        sound = data[i,:]
        write_wave_file(sound, frame_rate, path)

def write_wave_file(sound, frame_rate, path):
    with wave.open(path, mode='wb') as f:
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(frame_rate)
        f.setcomptype('NONE', 'not compressed')
        f.writeframes(sound)
