# import os
# import wave
# import pyaudio
# from faster_whisper import WhisperModel

# # Define constants
# NEON_GREEN = '\033[32m'
# RESET_COLOR = '\033[0m'

# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# def record_chunk(p, stream, file_path, chunk_length=10, frames_per_buffer=2048):
#     """
#     Writes an audio fragment to a file.

#     Args:
#         p (pyaudio.PyAudio): PyAudio object.
#         stream (pyaudio.Stream): PyAudio stream.
#         file_path (str): Path to the file where the audio fragment will be recorded.
#         chunk_length (int): Length of the audio chunk in seconds.
#         frames_per_buffer (int): Number of frames per buffer for recording.

#     Returns:
#         None
#     """
#     frames = []

#     total_frames = int(16000 / frames_per_buffer * chunk_length)

#     for _ in range(total_frames):
#         data = stream.read(frames_per_buffer)
#         frames.append(data)

#     wf = wave.open(file_path, 'wb')
#     wf.setnchannels(1)
#     wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
#     wf.setframerate(16000)
#     wf.writeframes(b''.join(frames))
#     wf.close()

# def transcribe_chunk(model, file_path):
#     segments, info = model.transcribe(file_path, beam_size=7)
#     transcription = ''.join(segment.text for segment in segments)
#     return transcription

# def main3():
#     """
#     The main function of the program.
#     """

#     # Select the Whisper model
#     model = WhisperModel("medium.en", device="cpu", compute_type="int8")

#     # Initialize PyAudio
#     p = pyaudio.PyAudio()

#     # Open the recording stream
#     frames_per_buffer = 2048
#     chunk_length = 5  # Adjusted for optimal performance

#     stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=frames_per_buffer)

#     # Initialize an empty string to accumulate transcriptions
#     accumulated_transcription = ""

#     try:
#         while True:
#             # Record an audio fragment
#             chunk_file = "temp_chunk.wav"
#             record_chunk(p, stream, chunk_file, chunk_length=chunk_length, frames_per_buffer=frames_per_buffer)

#             # Transcribe the audio fragment
#             transcription = transcribe_chunk(model, chunk_file)
#             print(NEON_GREEN + transcription + RESET_COLOR)

#             # Delete the temporary file
#             os.remove(chunk_file)

#             # Add a new transcription to the accumulated transcription
#             accumulated_transcription += transcription + " "

#     except KeyboardInterrupt:
#         print("Stopping...")

#         # Write the accumulated transcription to a log file
#         with open("log.txt", "w") as log_file:
#             log_file.write(accumulated_transcription)

#     finally:
#         print("LOG" + accumulated_transcription)
#         # Close the recording stream
#         stream.stop_stream()
#         stream.close()

#         # Stop PyAudio
#         p.terminate()

# if __name__ == "__main__":
#     main3()

import os
import wave
import pyaudio
from faster_whisper import WhisperModel
import time

# Define constants
NEON_GREEN = '\033[32m'
RESET_COLOR = '\033[0m'

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def record_chunk(p, stream, file_path, chunk_length=15, frames_per_buffer=2048):
    """
    Writes an audio fragment to a file.

    Args:
        p (pyaudio.PyAudio): PyAudio object.
        stream (pyaudio.Stream): PyAudio stream.
        file_path (str): Path to the file where the audio fragment will be recorded.
        chunk_length (int): Length of the audio chunk in seconds.
        frames_per_buffer (int): Number of frames per buffer for recording.

    Returns:
        None
    """
    frames = []

    total_frames = int(16000 / frames_per_buffer * chunk_length)

    for _ in range(total_frames):
        data = stream.read(frames_per_buffer)
        frames.append(data)

    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_chunk(model, file_path):
    segments, info = model.transcribe(file_path, beam_size=5)
    transcription = ''.join(segment.text for segment in segments)
    return transcription

def main3():
    """
    The main function of the program.
    """

    # Select the Whisper model
    model = WhisperModel("medium", device="cpu", compute_type="int8")

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open the recording stream
    frames_per_buffer = 2048
    chunk_length = 15  # Record for 15 seconds

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=frames_per_buffer)

    try:
        # Record an audio fragment
        chunk_file = "temp_chunk.wav"
        record_chunk(p, stream, chunk_file, chunk_length=chunk_length, frames_per_buffer=frames_per_buffer)

        # Transcribe the audio fragment
        st = time.time()
        transcription = transcribe_chunk(model, chunk_file)
        end = time.time()
        print("Time taken to transcribe: ", end-st)
        print(NEON_GREEN + transcription + RESET_COLOR)

        # Delete the temporary file
        # os.remove(chunk_file)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        # Close the recording stream
        stream.stop_stream()
        stream.close()

        # Stop PyAudio
        p.terminate()

if __name__ == "__main__":
    main3()


# Choosing frames_per_buffer:
# Frames per Buffer: This parameter determines how much audio data is read from the input stream (stream.read()) in each iteration. Larger buffers can reduce the frequency of I/O operations (which can be computationally expensive), but they can also introduce latency.

# Optimal Range: A common value for frames_per_buffer is in the range of 1024 to 4096 samples. This range balances efficient I/O operations with manageable latency.


# Choosing chunk_length:
# Chunk Length: This parameter determines the duration of each recorded segment. It affects how often you process or analyze the recorded audio.

# Optimal Duration: The optimal duration (chunk_length) depends on your application:
# For speech recognition and transcription, shorter chunks (e.g., 1 to 10 seconds) are often preferable because they allow for more frequent updates and real-time processing.
# Longer chunks (e.g., 10 to 30 seconds) can reduce the overhead of file operations and might be suitable if processing efficiency is critical and real-time updates are less important.