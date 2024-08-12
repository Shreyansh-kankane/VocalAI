import asyncio
import socket
import sounddevice as sd
import soundfile as sf
import io
import os

server_ip = os.getenv('SERVER_IP')
server_port = 8000

async def capture_audio(duration=10, fs=16000):
    print("Start speaking your prompt.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    await asyncio.sleep(duration)
    return recording

def send_audio_to_server(audio_data, server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        with io.BytesIO() as audio_file:
            sf.write(audio_file, audio_data, 16000, format='WAV')
            audio_file.seek(0)
            packet_size = 1024  # Adjust as necessary
            while True:
                packet = audio_file.read(packet_size)
                if not packet:
                    break
                s.sendto(packet, server_address)

        # Signal end of transmission
        s.sendto(b'', server_address)
        
        response_audio = b''
        while True:
            packet, _ = s.recvfrom(4096)
            if not packet:
                break
            response_audio += packet
    return response_audio

def play_audio(response_audio):
    with open('response.wav', 'wb') as f:
        f.write(response_audio)
    data, fs = sf.read('response.wav', dtype='int16')
    sd.play(data, fs)
    sd.wait()

async def recognize_audio_async():
    server_address = (server_ip, server_port)
    while True:
        audio_data = await capture_audio()
        response_audio = send_audio_to_server(audio_data, server_address)
        play_audio(response_audio)

if __name__== "__main__":
    asyncio.run(recognize_audio_async())