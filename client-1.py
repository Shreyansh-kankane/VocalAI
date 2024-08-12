import socket
import pyaudio
import time
import wave
import os

server_ip = os.getenv('SERVER_IP')
server_port = 8000
max_datagram_size = 1400  # Reduce size for UDP safety
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100
record_seconds = 5
output_filename = "output.wav"

# Initialize PyAudio
p = pyaudio.PyAudio()

stream = p.open(format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk)



print("Recording...")

frames = []

for i in range(0, int(rate / chunk * record_seconds)):
    data = stream.read(chunk)
    frames.append(data)

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
p.terminate()

# Save the recorded data as a WAV file
wf = wave.open(output_filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(format))
wf.setframerate(rate)
wf.writeframes(b''.join(frames))
wf.close()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

with open(output_filename, 'rb') as f:
    data = f.read()
    while data:
        if len(data) > max_datagram_size:
            client_socket.sendto(data[:max_datagram_size], (server_ip, server_port))
            data = data[max_datagram_size:]
        else:
            client_socket.sendto(data, (server_ip, server_port))
            data = b''

        time.sleep(0.01)  # Small delay to avoid overwhelming the network

client_socket.sendto(b'END', (server_ip, server_port))

# Receive response from server
response, _ = client_socket.recvfrom(65536)
print(response.decode())

client_socket.close()


