import subprocess
from app_logging import logger, LogLevel
from pathlib import Path
import librosa

SAMPLE_RATE = 44100  # Standard sample rate for audio processing
CHANNELS = 2  # Stereo audio


def checkFfmpegInstalled():
    """Check if ffmpeg is installed and accessible."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.sendLog("ffmpeg is not installed or not accessible.", LogLevel.ERROR)
        return False


def convertToWav(inputFile: str, outputFile: str):
    """Convert an audio file to WAV format using ffmpeg."""
    inputFile = Path(inputFile)
    outputPath = Path(outputFile)
    outputPath.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(inputFile),
                "-ar",
                str(SAMPLE_RATE),
                "-ac",
                str(CHANNELS),
                str(outputPath),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        logger.sendLog(f"Extracted audio from {inputFile}.", LogLevel.INFO)
        return
    except subprocess.CalledProcessError as e:
        logger.sendLog(f"Failed to extract audio from {inputFile}: {e}", LogLevel.ERROR)
        return


def detectBpm(inputFile: str) -> float:
    """Detect the BPM of an audio file."""
    inputFile = Path(inputFile)
    y, sr = librosa.load(str(inputFile), sr=SAMPLE_RATE)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


# Just for local debugging
if __name__ == "__main__":
    if not checkFfmpegInstalled():
        print("ffmpeg is not installed")
        exit(1)
    testOutput = "./temp/output.wav"
    testInput = "./Hercules -.mp4"
    convertToWav(testInput, testOutput)
    bpm = detectBpm(testOutput)
    print(f"Detected BPM: {bpm}")
