# File: local_transcribe_whisper.py
# Developer: Craig and ChatGPT 4o
# Version: 2.6.2
# Date: 2025-07-30
# Purpose: Parallel Whisper transcription with adaptive chunking, robust error handling, and preflight readiness.
# Last Change Summary: Removed legacy chunk prompts, added runtime self-check, preserved all advanced features.

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from multiprocessing import Pool, Manager, cpu_count
import tempfile
import argparse
import whisper

CONFIG_FILE = "transcribe_config.json"
LOG_FILE = "transcribe_session.log"
SUPPORTED_MODELS = ["tiny", "small", "base", "medium", "large"]


# ============== Runtime Self-Check ==============
def runtime_self_check():
    """Log which file and version is executing to avoid running outdated copies."""
    current_file = os.path.abspath(__file__)
    log_event("INFO", f"Executing {current_file} | Version 2.6.2")
    print(f"[INFO] Running {os.path.basename(current_file)} (Version 2.6.2)")


# ============== Logging ==============
def log_event(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(f"[{timestamp}] [{level}] {message}\n")
    print(f"[{level}] {message}")


def start_log():
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write("\n" + "=" * 60 + "\n")
        logf.write(f"New Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        logf.write("=" * 60 + "\n")


# ============== Config ==============
def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            log_event("WARN", "Config corrupted. Resetting to defaults.")
            save_config({})
            return {}
    return {}


def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception:
        log_event("WARN", "Failed to save configuration")


# ============== Preflight Check ==============
def check_ready():
    """Check readiness for preflight integration."""
    return {
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "whisper": True if shutil.which("python") else False,
        "config": os.path.isfile(CONFIG_FILE),
    }


# ============== FFmpeg Utils ==============
def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        log_event("ERROR", "FFmpeg not found in PATH")
        raise RuntimeError("FFmpeg not found in PATH")
    log_event("INFO", "FFmpeg check passed.")


def get_audio_duration(file_path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def convert_to_wav(input_file):
    output_file = os.path.splitext(input_file)[0] + ".wav"
    cmd = ["ffmpeg", "-y", "-i", input_file, output_file]
    subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
    )
    log_event("INFO", f"Conversion complete: {output_file}")
    return output_file


# ============== Progress Bar ==============
def print_progress_bar(iteration, total, prefix="", suffix="", length=40):
    percent = (
        ("{0:.1f}").format(100 * (iteration / float(total))) if total > 0 else "0.0"
    )
    filled_length = int(length * iteration // total) if total > 0 else 0
    bar = "#" * filled_length + "-" * (length - filled_length)
    sys.stdout.write(f"\r{prefix} |{bar}| {percent}% {suffix}")
    sys.stdout.flush()
    if iteration >= total:
        print()


# ============== Worker ==============
def worker_transcribe(args):
    (
        part_path,
        offset,
        model_choice,
        gpu_flag,
        total_duration,
        progress_counter,
        lock,
    ) = args
    try_count = 0
    while try_count < 2:
        try:
            model = whisper.load_model(
                model_choice, device="cuda" if gpu_flag else "cpu"
            )
            result = model.transcribe(part_path)
            segments = result.get("segments", [])
            adjusted_segments = []
            for seg in segments:
                start = seg["start"] + offset
                end = seg["end"] + offset
                text = seg["text"]
                adjusted_segments.append((start, end, text))
                with lock:
                    progress_counter.value = min(
                        progress_counter.value + (end - start), total_duration
                    )
            return {"status": "success", "segments": adjusted_segments}
        except Exception as e:
            try_count += 1
            log_event(
                "ERROR", f"Worker failed (attempt {try_count}) for {part_path}: {e}"
            )
    return {"status": "failed", "segments": []}


# ============== Sequential Fallback ==============
def sequential_fallback(failed_parts, model_choice, gpu_flag):
    recovered_segments = []
    for path, offset in failed_parts:
        try:
            model = whisper.load_model(
                model_choice, device="cuda" if gpu_flag else "cpu"
            )
            result = model.transcribe(path)
            for seg in result.get("segments", []):
                recovered_segments.append(
                    (seg["start"] + offset, seg["end"] + offset, seg["text"])
                )
            log_event("INFO", f"Sequential fallback succeeded for {path}")
        except Exception as e:
            log_event("ERROR", f"Sequential fallback failed for {path}: {e}")
    return recovered_segments


# ============== Parallel Transcription ==============
def parallel_transcribe(
    file_path, base_dir, model_choice="small", use_memory=False, parts=None
):
    start_time = datetime.now()

    total_duration = get_audio_duration(file_path)
    if total_duration == 0:
        raise RuntimeError("Could not determine audio duration")

    # Adaptive chunking: CPU cores + duration
    available_cores = cpu_count()
    if not parts:
        if total_duration > 3600:
            parts = min(10, max(4, available_cores // 2))
        else:
            parts = min(5, max(2, available_cores // 2))

    log_event(
        "INFO", f"Total audio length: {total_duration:.2f} sec; using {parts} parts."
    )

    part_length = total_duration / parts
    split_files = []
    temp_dir = tempfile.gettempdir() if use_memory else base_dir

    for i in range(parts):
        start = i * part_length
        end = (i + 1) * part_length
        part_path = os.path.join(temp_dir, f"temp_part_{i}.wav")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            file_path,
            "-ss",
            str(start),
            "-to",
            str(end),
            "-c",
            "copy",
            part_path,
        ]
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode != 0 or not os.path.exists(part_path):
            raise RuntimeError(f"Failed to create split part {i}")
        split_files.append((part_path, start))

    # GPU detection
    try:
        import torch

        gpu_available = torch.cuda.is_available()
    except ImportError:
        gpu_available = False
    use_gpu = gpu_available

    manager = Manager()
    progress_counter = manager.Value("d", 0.0)
    lock = manager.Lock()

    args_list = [
        (path, offset, model_choice, use_gpu, total_duration, progress_counter, lock)
        for path, offset in split_files
    ]

    pool = Pool(min(parts, available_cores))
    results = pool.map_async(worker_transcribe, args_list)

    while not results.ready():
        with lock:
            processed = progress_counter.value
        print_progress_bar(
            processed, total_duration, prefix="Transcription", suffix="Processing"
        )
        results.wait(timeout=1)

    results = results.get()
    pool.close()
    pool.join()

    merged_segments = []
    failed_parts = []
    for idx, res in enumerate(results):
        if res["status"] == "success":
            merged_segments.extend(res["segments"])
        else:
            failed_parts.append(split_files[idx])

    # Sequential fallback for failed parts
    if failed_parts:
        log_event("WARN", f"Retrying failed parts sequentially: {failed_parts}")
        merged_segments.extend(sequential_fallback(failed_parts, model_choice, use_gpu))

    merged_segments.sort(key=lambda x: x[0])

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ts_output = os.path.join(
        base_dir, f"{base_name}_parallel_transcript_{timestamp}.txt"
    )
    clean_output = os.path.join(base_dir, f"{base_name}_parallel_clean_{timestamp}.txt")

    with (
        open(ts_output, "w", encoding="utf-8") as tsf,
        open(clean_output, "w", encoding="utf-8") as cf,
    ):
        for start, end, text in merged_segments:
            tsf.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")
            cf.write(f"{text.strip()} ")

    # Cleanup
    for path, _ in split_files:
        if os.path.exists(path):
            os.remove(path)

    elapsed = (datetime.now() - start_time).total_seconds()
    log_event("INFO", f"Transcription complete in {elapsed:.2f} seconds.")
    log_event("INFO", f"Outputs saved to: {ts_output} and {clean_output}")

    try:
        if sys.platform == "win32":
            os.startfile(base_dir)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", base_dir])
        else:
            subprocess.Popen(["xdg-open", base_dir])
    except Exception:
        log_event("INFO", f"Please open manually: {base_dir}")

    # Post-run summary
    print(
        f"\nSummary: Duration={total_duration:.2f}s | Parts={parts} | Failed parts retried={len(failed_parts)}"
    )


# ============== Public API Wrapper ==============
def transcribe_file(
    file_path, output_dir=None, model="small", use_memory=False, parts=None
):
    """Public API for programmatic transcription (for integration with preflight or pipelines)."""
    if output_dir is None:
        output_dir = os.getcwd()
    wav_file = convert_to_wav(file_path)
    parallel_transcribe(wav_file, output_dir, model, use_memory, parts)


# ============== Main CLI ==============
def main():
    parser = argparse.ArgumentParser(
        description="Parallel Whisper Transcription Tool (DevAgentZero Standard)"
    )
    parser.add_argument(
        "file", help="Path to input audio file (.m4a, .mp3, .wav, etc.)"
    )
    parser.add_argument(
        "-m", "--model", default="small", help=f"Whisper model size {SUPPORTED_MODELS}"
    )
    parser.add_argument(
        "-d", "--dir", default=os.getcwd(), help="Base directory for output files"
    )
    parser.add_argument(
        "--memory", action="store_true", help="Use in-memory splitting for speed"
    )
    parser.add_argument(
        "--parts", type=int, help="Override auto chunking with specific number of parts"
    )

    args = parser.parse_args()

    start_log()
    runtime_self_check()  # Log current file/version running
    config = load_config()

    base_dir = args.dir or config.get("base_dir", os.getcwd())
    model_choice = (
        args.model.lower()
        if args.model.lower() in SUPPORTED_MODELS
        else config.get("model_choice", "small")
    )
    save_config({"base_dir": base_dir, "model_choice": model_choice})

    try:
        check_ffmpeg()
        transcribe_file(args.file, base_dir, model_choice, args.memory, args.parts)
    except Exception as e:
        log_event("ERROR", f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
