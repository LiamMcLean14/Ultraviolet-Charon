import asyncio
import wave
import threading
from queue import Queue
import numpy as np
import time
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "Zephyr"
UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

SAMPLE_RATE = 12000
PACKET_MS = 20
CHUNK_SIZE = SAMPLE_RATE * PACKET_MS // 1000

async def find_device():
    print("Scanning")

    devices = await BleakScanner.discover()

    for i in devices:
        #print(i.name, i.address)
        if i.name == DEVICE_NAME:
            return i

    return None

def verifyWav(wav):
    channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    sample_rate = wav.getframerate()

    print("Channels:", channels)
    print("Sample width:", sample_width)
    print("Sample rate:", sample_rate)

    if channels != 1:
        print("WAV must be mono")
        return -1

    if sample_width != 1:
        print("WAV must be 8-bit")
        return -1

    if sample_rate != SAMPLE_RATE:
        print(f"WAV must be {SAMPLE_RATE} Hz")
        return -1
    return 0;
  
soundEffectQueue = Queue()

"""
    Okay let me tell you about stream_wav
    So because of bandwidth we are very limited in what we can play. Stuck with 8 bit 12Khz Mono.

    The issue this function works to solve is "What if I want to play a sound effect ontop of the background music?"
    And good news! This technically does that


    So, another thread is constantly hammering the client with "What sound effect do you want?" and adds valid requests to a queue.
    Valid requests are processed, converted into a byte string, merged with the main track, and converted back into the format for the speaker. 

    ISSUES:
        Volume. The sound effects are consistently loud. Probably because I am adding two wav files sample on sample, google says this should work but I am not convinced.
"""
async def stream_wav(client, filename):
    #ONLY NOW DO WE START THE EFFECTS LOADING THREAD
    thread2.start()
    with wave.open(filename, "rb") as wav:
        if (verifyWav(wav) == -1):
            return None

        print("Streaming audio...")
        
        #Once an effect has stopped playing, load the next
        finishedEffect = 1
        currentEffect = 0

        while True:
            data = wav.readframes(CHUNK_SIZE)

            if (finishedEffect == 1):
                if (soundEffectQueue.empty() == False):
                    request = soundEffectQueue.get()
                    print(f"Playing sound effect {request}")
                    currentEffect = wave.open(request, "rb")
                    finishedEffect = 0
            
            if (finishedEffect == 0):
                additionalData = currentEffect.readframes(CHUNK_SIZE)
                if not additionalData:
                    print("End of Sound Effect")
                    finishedEffect = 1
                else:
                    dataSampled = np.frombuffer(data, dtype=np.int8)
                    additionalSampled = np.frombuffer(additionalData, dtype = np.int8)
                    
                    mainTrackLength = len(dataSampled)
                    soundeffectLength = len(additionalSampled)

                    #Yes I am aware that in theory a sound effect could play with the same remaining length as the main track and 
                    #maybe cause a crash on the board because it sends less than it expects but that is astronomically unlikely
                    if(mainTrackLength<soundeffectLength):
                        dataSampled = np.pad(dataSampled, (0, soundeffectLength - mainTrackLength), mode='constant', constant_values=0)                        
                    if(soundeffectLength<mainTrackLength):
                        additionalSampled = np.pad(additionalSampled, (0, mainTrackLength - soundeffectLength), mode='constant', constant_values=0)
                    
                    #We do that padding also so this works
                    combined = dataSampled + additionalSampled
                    combined = np.clip(combined, -128, 127)
                    data = combined.tobytes()
                    
            #Once the music finishes this closes. 
            if not data:
                print("EOF")
                break

            await client.write_gatt_char(UUID, data, response=False)
            await asyncio.sleep(CHUNK_SIZE / SAMPLE_RATE)
        
        print("Finished Audio Transmission")
        while True:
            a = 1

def queueSoundEffect():
    print("queueSoundEffects thread created")
    time.sleep(2)
    while(1):
        request = input("Enter a sound effects filePath to play (defaults to sounds/quietquickboom.wav if empty): ")
        if (request == ""):
            request = "sounds/quietquickboom.wav"
        
        with wave.open(request, "rb") as wav:
            if (verifyWav(wav) == 0):
                soundEffectQueue.put(request)
                
    return;

async def connect():
    board = await find_device()
    if board is None:
        print("nrf52840 not found")
        return
    
    print("Attempting to connect to board")
    async with BleakClient(board.address) as client:
        print("Connected!")        
        sound_name = input("Enter the name of the music file (defaults to sounds/sound.wav if empty): ") 
        if (sound_name == ""):
            sound_name = "sounds/sound.wav"
        print(f"Streaming \"{sound_name}\"")
        await stream_wav(client, sound_name)

def startTransmission():
    asyncio.run(connect())

thread1 = threading.Thread(target=startTransmission) 
thread2 = threading.Thread(target=queueSoundEffect)

thread1.start()
