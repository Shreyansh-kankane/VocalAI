import os
import wave
import sounddevice as sd
import pyaudio
from faster_whisper import WhisperModel
import soundfile as sf

NEON_GREEN = '\033[32m'
RESET_COLOR = '\033[0m'

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Function for recording an audio fragment

def record_chunk(p, stream, file_path, chunk_length=1):
    """
    Writes an audio fragment to a file.

    Args:
        p(pyaudio.PyAudio): PyAudio object.
        stream(pyaudio.Stream): PyAudio stream.
        file_path (str): Path to the file where the audio fragment will be recorded.
        chunk_length (int): Length of the audio chunk in seconds.

    Returns:
        None
    """

    frames = []

    for _ in range(0, int(16000 / 4096 * chunk_length)):  # Adjusted buffer size
        try:
            data = stream.read(4096, exception_on_overflow=False)  # Adjusted buffer size
            frames.append(data)
        except IOError as e:
            print(f"Input overflowed: {e}")
            return False

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()
    return True

def transcribe_chunk(model, file_path):
    print(f"Transcribing file: {file_path}")
    segments, info = model.transcribe(file_path, beam_size=7)
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    transcription = ''.join(segment.text for segment in segments)
    return transcription

def play_audio(file_path):
    # Play back the recorded audio to verify it
    data, fs = sf.read(file_path, dtype='float32')
    sd.play(data, fs)
    sd.wait()

def main2():
    """
    The main function of the program.
    """
    model_size = "medium.en"
    # Select the Whisper model
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open the recording stream
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)  # Adjusted buffer size

    # Initialize an empty string to accumulate transcriptions
    accumulated_transcription = ""

    try:
        while True:
            # Record an audio fragment
            chunk_file = "temp_chunk.wav"
            if record_chunk(p, stream, chunk_file):
                print(f"Recorded chunk to {chunk_file}")

                # Play back the recorded audio for verification
                play_audio(chunk_file)

                # Transcribe the audio fragment
                transcription = transcribe_chunk(model, chunk_file)
                print(NEON_GREEN + transcription + RESET_COLOR)

                # Add a new transcription to the accumulated transcription
                accumulated_transcription += transcription + " "

                # Delete the temporary file
                os.remove(chunk_file)
            else:
                print("Recording failed due to overflow.")

    except KeyboardInterrupt:
        print("Stopping...")

        # Write the accumulated transcription to a log file
        with open("log.txt", "w") as log_file:
            log_file.write(accumulated_transcription)

    finally:
        print("LOG" + accumulated_transcription)
        # Close the recording stream
        stream.stop_stream()
        stream.close()

        # Stop PyAudio
        p.terminate()


if __name__ == "__main__":
    main2()