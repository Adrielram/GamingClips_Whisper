import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace

MODEL_SIZE_DEFAULT = "large-v3"


def has_ffmpeg():
    return shutil.which("ffmpeg") is not None


def extract_audio_with_ffmpeg(input_path: str, out_path: str) -> None:
    # Extract audio as 16k mono WAV which works well for ASR models
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        out_path,
    ]
    # Use subprocess and raise if ffmpeg fails
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode('utf-8', errors='ignore')}")


def is_video_file(path: str) -> bool:
    video_exts = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
    return os.path.splitext(path)[1].lower() in video_exts


def is_audio_file(path: str) -> bool:
    audio_exts = {".wav", ".mp3", ".m4a", ".flac", ".aac", ".ogg"}
    return os.path.splitext(path)[1].lower() in audio_exts


def _format_timestamp_srt(seconds: float) -> str:
    # SRT timestamp: HH:MM:SS,mmm
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save_transcription(segments, out_path: str, info=None):
    """Save segments to file. Supports .srt, .txt, .json"""
    ext = os.path.splitext(out_path)[1].lower()
    if ext == ".srt":
        with open(out_path, "w", encoding="utf-8") as f:
            for i, s in enumerate(segments, start=1):
                start = _format_timestamp_srt(s.start)
                end = _format_timestamp_srt(s.end)
                text = s.text.strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
    elif ext == ".json":
        import json

        out = {
            "language": getattr(info, "language", None),
            "language_probability": getattr(info, "language_probability", None),
            "segments": [
                {"start": s.start, "end": s.end, "text": s.text} for s in segments
            ],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    else:
        # plain text
        with open(out_path, "w", encoding="utf-8") as f:
            for s in segments:
                f.write(s.text.strip() + "\n")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio or video files using faster-whisper")
    parser.add_argument("input", help="Path to input audio or video file (.mp4, .mkv, .mp3, .wav, ...)")
    parser.add_argument("--model-size", default=MODEL_SIZE_DEFAULT, help="Whisper model size (default: large-v3)")
    parser.add_argument("--device", default="cuda", help="Device to run on: cuda or cpu (default: cuda)")
    parser.add_argument("--compute-type", default="float16", help="Compute type: float16, int8_float16, int8 (default: float16)")
    parser.add_argument("--beam-size", type=int, default=5, help="Beam size for transcription (default: 5)")
    parser.add_argument("--output", help="Optional output path to save transcription. Supports .srt, .txt, .json")
    parser.add_argument("--no-whisperx", action="store_true", help="Disable whisperx forced-alignment even if installed")
    parser.add_argument("--use-argentine-prompt", action="store_true", help="Use a built-in Argentine/gaming prompt to bias transcription (short, safe)")
    parser.add_argument("--use-argentine-prompt-long", action="store_true", help="Use a long conversational Argentine prompt to bias transcription (risky; may cause literal insertions)")
    parser.add_argument("--vad-split", action="store_true", help="Pre-split audio using ffmpeg silencedetect and transcribe chunks separately (helps capture missed moments)")
    args = parser.parse_args()

    # Built-in Argentine gaming prompt: keywords only (safer, avoids literal insertion)
    ARGENTINE_GAMING_PROMPT = (
        "adriel, che, boludo, pibe, mina, laburo, guita, gg, clutch, lag, headshot, rekt"
    )

    # Long conversational Argentine prompt (user-provided style). This is intentionally
    # verbose and may cause the model to echo prompt text literally; use with care.
    ARGENTINE_GAMING_PROMPT_LONG = (
        """
        Hola, sos un transcriptor experto en Español de Argentina (Rioplatense). Sos muy bueno transcribiendo, con acento neutro	
        y convertís modismos y jerga locales a su forma escrita natural. Prestá atención a expresiones como "che", "boludo", "re",
        "posta", "una mano", "hacer un gank", "clutch", "pibe", y nombres propios o apodos de jugadores. No agregues etiquetas
        adicionales como [música] o [risas] a menos que sean claramente audibles como parte del diálogo. Mantené la ortografía
        coloquial pero entendible: convertí "q" a "que" si está a la mitad de una palabra, pero preservá apodos o nombres tal cual.
        Prioriza la fidelidad al habla: no inventes palabras ni agregues explicaciones; si algo no se entiende, deja una
        transcripción lo más cercana posible y marca ligeramente la ambigüedad con '...' si es necesario.
        """
    )

    def _clean_segments(segments_list, prompt_keywords=None):
        """Remove obvious prompt-insertions and duplicated/repeated short segments.

        - drop segments that contain prompt-control phrases like 'priorizar expresiones'
        - drop exact duplicates in a row
        - drop segments that are extremely short and repeated many times
        """
        if not segments_list:
            return segments_list

        cleaned = []
        # blacklist common prompt-control phrases
        blacklist_patterns = [
            "priorizar expresiones",
            "priorizar expresiones de gg",
            "priorizar expresiones de gaming",
        ]

        # create a small set of prompt keywords for quick matching
        prompt_set = set()
        if prompt_keywords:
            for tok in [p.strip().lower() for p in prompt_keywords.replace(',', ' ').split()]:
                if tok:
                    prompt_set.add(tok)

        prev_text = None

        def is_mostly_prompt_tokens(text):
            toks = [t for t in text.split() if t]
            if not toks:
                return False
            count = sum(1 for t in toks if t in prompt_set)
            return (count / len(toks)) >= 0.6

        def collapse_repeats_in_text(text):
            parts = text.split()
            if not parts:
                return text
            out = []
            last = None
            run = 0
            for p in parts:
                if p == last:
                    run += 1
                else:
                    last = p
                    run = 1
                if run <= 2:
                    out.append(p)
            return ' '.join(out)

        for s in segments_list:
            text = (s.text or "").strip()
            low = text.lower()

            # drop prompt-control phrases
            if any(p in low for p in blacklist_patterns):
                continue

            # collapse obvious repeats inside segment
            collapsed = collapse_repeats_in_text(low)
            low = collapsed

            # drop segments made mostly of prompt keywords (these are likely injected)
            if prompt_set and is_mostly_prompt_tokens(low):
                continue

            # drop consecutive duplicates
            if prev_text is not None and low == prev_text:
                continue

            # drop segments that are extremely long and look like garbage
            if len(low.split()) > 200:
                continue

            # if segment is just punctuation or empty, skip
            if not any(c.isalnum() for c in low):
                continue

            cleaned.append(SimpleNamespace(start=s.start, end=s.end, text=low))
            prev_text = low

        return cleaned


    def _run_ffmpeg_silencedetect_and_split(audio_path: str, out_dir: str, min_silence_len=0.6, silence_thresh_db=-32):
        """Run ffmpeg silencedetect to find non-silent intervals and export short chunk filenames.

        Returns a list of (chunk_path, start_time, end_time).
        Requires ffmpeg on PATH.
        """
        if not has_ffmpeg():
            raise RuntimeError("ffmpeg not found on PATH; cannot perform VAD splitting")

        cmd = [
            "ffmpeg",
            "-i",
            audio_path,
            "-af",
            f"silencedetect=noise={silence_thresh_db}dB:d={min_silence_len}",
            "-f",
            "null",
            "-",
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = proc.stderr

        # parse lines like: "silencedetect @ 00:00:01.234 | silence_start: 1.234"
        import re

        silence_starts = []
        silence_ends = []
        for line in output.splitlines():
            m1 = re.search(r"silence_start:\s*([0-9.]+)", line)
            if m1:
                silence_starts.append(float(m1.group(1)))
            m2 = re.search(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", line)
            if m2:
                silence_ends.append(float(m2.group(1)))

            # build non-silent intervals by inverting silence regions
            intervals = []
            # get audio duration via ffprobe
            try:
                cmd2 = [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    audio_path,
                ]
                dur_proc = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                duration = float(dur_proc.stdout.strip())
            except Exception:
                duration = None

            # merge starts/ends into ranges
            # If no silences found, return the whole file as a single chunk
            if not silence_starts and not silence_ends:
                out_chunk = os.path.join(out_dir, "chunk_0.wav")
                extract_audio_with_ffmpeg(audio_path, out_chunk)
                return [(out_chunk, 0.0, duration if duration else 0.0)]

            # build alternating list
            points = []
            for s in silence_starts:
                points.append((s, "start"))
            for e in silence_ends:
                points.append((e, "end"))
            points.sort()

            # assume audio begins at 0
            cursor = 0.0
            idx = 0
            chunks = []
            for t, kind in points:
                if kind == "start":
                    # non-silent from cursor to t
                    if t - cursor > 0.05:
                        s = max(0.0, cursor)
                        e = t
                        chunks.append((s, e))
                    cursor = t
                elif kind == "end":
                    # silence ended at t -> new non-silent starts at t
                    cursor = t

            # final tail
            final_end = duration if duration else cursor + 0.1
            if final_end - cursor > 0.05:
                chunks.append((cursor, final_end))

            out = []
            for i, (s, e) in enumerate(chunks):
                out_chunk = os.path.join(out_dir, f"chunk_{i}.wav")
                # use ffmpeg to extract the segment (preserve sample rate/mono as earlier)
                cmd3 = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    audio_path,
                    "-ss",
                    f"{s}",
                    "-to",
                    f"{e}",
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    "-vn",
                    out_chunk,
                ]
                proc3 = subprocess.run(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if proc3.returncode == 0 and os.path.exists(out_chunk):
                    out.append((out_chunk, s, e))

            return out

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        sys.exit(2)

    need_cleanup = False
    audio_path = input_path

    try:
        if is_video_file(input_path):
            if not has_ffmpeg():
                print("ffmpeg not found on PATH. Please install ffmpeg to extract audio from video files.")
                sys.exit(3)

            fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            try:
                extract_audio_with_ffmpeg(input_path, tmp_wav)
            except Exception as e:
                # cleanup tmp file
                if os.path.exists(tmp_wav):
                    os.remove(tmp_wav)
                raise
            audio_path = tmp_wav
            need_cleanup = True
        elif not is_audio_file(input_path):
            print("Input does not look like a supported audio or video file. Supported extensions: .mp4 .mkv .mov .avi .webm .mp3 .wav .m4a .flac .aac .ogg")
            sys.exit(4)

        # Lazy import heavier library so --help remains fast and importing the module doesn't instantiate the model
        from faster_whisper import WhisperModel

        # Try to initialize on requested device; if it fails (missing CUDA/cuDNN),
        # fall back to CPU automatically to avoid hard crashes for users.
        try:
            model = WhisperModel(args.model_size, device=args.device, compute_type=args.compute_type)
        except Exception as e:
            # If user requested cuda but it failed (common: missing CUDA/cuDNN DLLs),
            # retry on CPU with a safe compute_type and inform the user.
            if args.device.lower() in ("cuda", "gpu"):
                print("\nWarning: failed to initialize model on CUDA (error below). Falling back to CPU.\n")
                print(str(e))
                print("\nRetrying with --device cpu and compute_type=int8 (may be slower but avoids CUDA/cuDNN issues)...\n")
                try:
                    model = WhisperModel(args.model_size, device="cpu", compute_type="int8")
                except Exception as e2:
                    print("Failed to initialize model on CPU as well:")
                    raise
            else:
                # If device wasn't CUDA, re-raise the exception
                raise

        transcribe_kwargs = dict(beam_size=args.beam_size)
        # Add optional argentine prompt (long takes precedence if both flags set)
        if getattr(args, 'use_argentine_prompt_long', False):
            transcribe_kwargs['initial_prompt'] = ARGENTINE_GAMING_PROMPT_LONG
            transcribe_kwargs['temperature'] = 0.0
            # long prompts are prone to echoing; avoid conditioning on previous text
            transcribe_kwargs['condition_on_previous_text'] = False
        elif getattr(args, 'use_argentine_prompt', False):
            transcribe_kwargs['initial_prompt'] = ARGENTINE_GAMING_PROMPT
            transcribe_kwargs['temperature'] = 0.0
            # avoid conditioning on previous text to reduce literal echoing of the prompt
            transcribe_kwargs['condition_on_previous_text'] = False

        segments, info = model.transcribe(audio_path, **transcribe_kwargs)

        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        # Convert generator to a list to access its length and elements
        segments = list(segments)

        # Debugging: Ensure segments contain valid data
        if not segments:
            print("Warning: No segments were generated. The output file will be empty.")
        else:
            print(f"Debug: {len(segments)} segments generated. First segment: {segments[0].text}")

        # If whisperx is available and not disabled, try to perform forced-alignment
        segments_to_save = segments
        if not args.no_whisperx:
            try:
                import whisperx
                print("Running forced-alignment with whisperx...")

                # Prepare segments as list of dicts
                segs_for_align = [{"start": float(s.start), "end": float(s.end), "text": str(s.text)} for s in segments]

                # load_align_model signature may vary; try different call patterns
                try:
                    align_model, metadata = whisperx.load_align_model(language_code=getattr(info, 'language', None), device=args.device)
                except TypeError:
                    try:
                        align_model, metadata = whisperx.load_align_model(getattr(info, 'language', None), args.device)
                    except Exception:
                        # Fallback to no-arg call if available
                        align_model, metadata = whisperx.load_align_model()

                # perform alignment (handle variations in signature)
                try:
                    result_aligned = whisperx.align(segs_for_align, align_model, metadata, audio_path, device=args.device)
                except TypeError:
                    result_aligned = whisperx.align(segs_for_align, align_model, metadata, audio_path, args.device)

                # Normalize result to a list of segments
                if isinstance(result_aligned, dict):
                    segments_list = result_aligned.get("segments", [])
                else:
                    segments_list = getattr(result_aligned, "segments", [])

                aligned_segments = []
                for seg in segments_list:
                    if isinstance(seg, dict):
                        start = seg.get("start", 0.0)
                        end = seg.get("end", start)
                        text = seg.get("text", "")
                    else:
                        start = getattr(seg, "start", 0.0)
                        end = getattr(seg, "end", start)
                        text = getattr(seg, "text", "")
                    aligned_segments.append(SimpleNamespace(start=float(start), end=float(end), text=str(text)))

                if aligned_segments:
                    segments_to_save = aligned_segments
                    print(f"WhisperX alignment produced {len(aligned_segments)} segments.")
                else:
                    print("WhisperX alignment returned no segments; falling back to original segments.")

            except ImportError:
                # whisperx not installed; skip alignment silently
                pass
            except Exception as e:
                print("Warning: whisperx alignment failed, continuing with original segments. Error:\n", e)

        # Clean possible prompt-inserted or duplicated segments before saving
        try:
            # convert to list in case it's a generator-like structure
            segments_list_to_save = list(segments_to_save)
        except Exception:
            segments_list_to_save = segments_to_save

        # apply cleaning heuristics
        segments_list_to_save = _clean_segments(segments_list_to_save, prompt_keywords=ARGENTINE_GAMING_PROMPT)

        if args.output:
            print(f"Saving transcription to {args.output}...")
            save_transcription(segments_list_to_save, args.output, info)
            print("Transcription saved successfully.")

    finally:
        if need_cleanup and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass


if __name__ == "__main__":
    main()
