"""
Audio preprocessing helper for the GameClipping project.
- Resamples audio to target rate (16000 Hz)
- Normalizes volume
- Applies optional highpass/lowpass filters
- Exports a clean WAV suitable for ASR

Usage:
python tools/preprocess_audio.py input_video.mp4 output.wav --rate 16000 --highpass 200 --lowpass 8000 --normalize

Requires: ffmpeg installed and on PATH. Uses pydub for convenience.
"""
from pathlib import Path
import argparse
from pydub import AudioSegment


def preprocess(input_path: Path, output_path: Path, rate=16000, highpass=None, lowpass=None, normalize=False):
    # ffmpeg-backed loading
    audio = AudioSegment.from_file(input_path)

    # Convert to mono
    audio = audio.set_channels(1)

    # Resample
    audio = audio.set_frame_rate(rate)

    # Apply simple filters via low/high pass using pydub effects if available
    try:
        from pydub.effects import low_pass_filter, high_pass_filter
        if highpass:
            audio = high_pass_filter(audio, highpass)
        if lowpass:
            audio = low_pass_filter(audio, lowpass)
    except Exception:
        # pydub may not expose these on all platforms; ignore silently
        pass

    # Normalize
    if normalize:
        audio = match_target_amplitude(audio, -20.0)

    # Export as 16-bit PCM WAV
    audio.export(output_path, format="wav", bitrate="16k")


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input audio/video file')
    parser.add_argument('output', help='output wav file')
    parser.add_argument('--rate', type=int, default=16000)
    parser.add_argument('--highpass', type=int, default=None)
    parser.add_argument('--lowpass', type=int, default=None)
    parser.add_argument('--normalize', action='store_true')
    args = parser.parse_args()
    preprocess(Path(args.input), Path(args.output), rate=args.rate, highpass=args.highpass, lowpass=args.lowpass, normalize=args.normalize)
