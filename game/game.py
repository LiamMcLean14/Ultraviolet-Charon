DEBUGFLAG = False

import pygame
import random
from level_system import GameplayNote, Level, load_level, get_level_names
from enum import Enum
if DEBUGFLAG == False:
    from ImageDetection import *
import serial
import json
import time
import queue

import asyncio
import wave
import threading
from queue import Queue
import numpy as np
import time
from bleak import BleakClient, BleakScanner


DEVICE_NAME = "Zephyr"
DEBUGFLAG = True
UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

SAMPLE_RATE = 12000
PACKET_MS = 20
CHUNK_SIZE = SAMPLE_RATE * PACKET_MS // 1000

soundEffectQueue = Queue()
startMusic = False
musicStop = False
playEffect = False

async def find_device():
    print("Scanning")

    devices = await BleakScanner.discover()

    for i in devices:
        #print(i.name, i.address)
        if i.name == DEVICE_NAME:
            return i

    return None


class GameState(Enum):
    LEVEL_SELECT = 0
    PLAYING = 1
    RESULTS = 2


def verifyWav(wav):
    channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    sample_rate = wav.getframerate()

    #print("Channels:", channels)
    #print("Sample width:", sample_width)
    #print("Sample rate:", sample_rate)

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
  
musicStop = False

async def stream_wav(client, filename):
    #ONLY NOW DO WE START THE EFFECTS LOADING THREAD
    thread2.start()
    global startMusic
    while(True):
        print("startMusic is ", startMusic)
        while not startMusic:
            await asyncio.sleep(0.001)
            startMusic = False;
        with wave.open(filename, "rb") as wav:
            if (verifyWav(wav) == -1):
                return None

            print("Streaming audio...")
            
            #Once an effect has stopped playing, load the next
            finishedEffect = 1
            currentEffect = 0

            interval = CHUNK_SIZE / SAMPLE_RATE
            next_time = time.perf_counter()


            while True:
                global musicStop
                if musicStop == True:
                    musicStop = False
                    break
                start = time.perf_counter()
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
                        dataSampled = np.frombuffer(data, dtype=np.uint8).astype(np.int16)
                        additionalSampled = np.frombuffer(additionalData, dtype = np.uint8).astype(np.int16)

                        mainTrackLength = len(dataSampled)
                        soundeffectLength = len(additionalSampled)

                        dataSampled -= 128
                        additionalSampled -= 128

                        #Yes I am aware that in theory a sound effect could play with the same remaining length as the main track and 
                        #maybe cause a crash on the board because it sends less than it expects but that is astronomically unlikely
                        if(mainTrackLength<soundeffectLength):
                            dataSampled = np.pad(dataSampled, (0, soundeffectLength - mainTrackLength), mode='constant', constant_values=0)                        
                        if(soundeffectLength<mainTrackLength):
                            additionalSampled = np.pad(additionalSampled, (0, mainTrackLength - soundeffectLength), mode='constant', constant_values=0)
                        
                        MUSIC_VOLUME = 1
                        SFX_VOLUME = 1.2

                        combined = (
                            dataSampled.astype(np.int16) * MUSIC_VOLUME +
                            additionalSampled.astype(np.int16) * SFX_VOLUME
                        )
        
                        combined = np.clip(combined, -128, 127)
                        
                        combined = (combined+128).astype(np.uint8)
                        data = combined.tobytes()
                                            
                #Once the music finishes this closes. 
                if not data:
                    print("EOF")
                    break
                
                await client.write_gatt_char(UUID, data, response=False)
                
                next_time += interval
                delay = next_time - time.perf_counter() 
                
                if delay > 0:
                    await asyncio.sleep(delay)
                
                end = time.perf_counter()
                elapsed = (end - start) * 1_000_000  # Convert to microseconds
                print(f'Time taken: {elapsed:.2f} microseconds')



            print("Finished Audio Transmission")

playEffect = False
def queueSoundEffect():
    print("queueSoundEffects thread created")
    time.sleep(2)
    while(1):
        global playEffect
        while(1):
            if (playEffect == True):
            #        request = input("Enter a sound effects filePath to play (defaults to sounds/quietquickboom.wav if empty): ")
            #        if (request == ""):
                request = "sounds/score.wav"
            
                with wave.open(request, "rb") as wav:
                    if (verifyWav(wav) == 0):
                        soundEffectQueue.put(request)
                
                playEffect = False
                break    
    return;

async def connect():
    board = await find_device()
    if board is None:
        print("nrf52840 not found")
        return
    
    print("Attempting to connect to board")
    async with BleakClient(board.address) as client:
        print("Connected!")        
        #sound_name = input("Enter the name of the music file (defaults to sounds/sound.wav if empty): ") 
        #if (sound_name == ""):
        sound_name = "sounds/sound.wav"
        print(f"Streaming \"{sound_name}\"")
        await stream_wav(client, sound_name)


# -----------------------------
# Initialization
# -----------------------------
pygame.init()
WIDTHOFFSET = 600
WIDTH = 600 + WIDTHOFFSET
HEIGHT = 800
FPS = 30
PRE_LEVEL_SECONDS = 3
RESULTS_SCREEN_SECONDS = 3
ACTIVATE_DIST = 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Basic Rhythm Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 24)

# -----------------------------
# Colors
# -----------------------------
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
GREEN = (50, 220, 100)
RED = (220, 70, 70)
BLUE = (80, 140, 255)
YELLOW = (255, 220, 50)
ORANGE = (255, 165, 20)

LANE_COLORS = [RED, YELLOW, GREEN, BLUE, ORANGE]

# -----------------------------
# Lanes
# -----------------------------
LANE_COUNT = 5
LANE_WIDTH = (WIDTH - WIDTHOFFSET) // LANE_COUNT

KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
KEY_LABELS = ["1", "2", "3", "4", "5"]

# -----------------------------
# Gameplay settings
# -----------------------------
NOTE_WIDTH = LANE_WIDTH - 20
NOTE_HEIGHT = 25
HIT_LINE_Y = HEIGHT - 120
HIT_WINDOW = 40

rangeQueue = queue.Queue(maxsize=1)
fingerQueue = queue.Queue(maxsize=1)
imageQueue = queue.Queue(maxsize=1)

if DEBUGFLAG == False:
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=115200,
        timeout=1
)

class NoteObject:
    """
    An in-game object representing a GameplayNote on screen.
    Contains a GameplayNote object, and info required to display it
    (e.g. a y coordinate, and a method to draw it on-screen)
    """
    def __init__(self, gameplay_note: GameplayNote, starting_y, speed: int):
        self.note = gameplay_note
        self.y = starting_y
        self.speed = speed


    def update(self):
        self.y += self.speed

    def draw(self, surface):
        """Draws a line for all lanes in the note"""
        for i, finger_up in enumerate(self.note.finger_positions):
            x = i * LANE_WIDTH + 10
            if finger_up:
                pygame.draw.rect(
                surface,
                LANE_COLORS[i],
                (x, self.y, NOTE_WIDTH, NOTE_HEIGHT),
                border_radius=8,
        )

    def is_hittable(self):
        return abs(self.y - HIT_LINE_Y) <= HIT_WINDOW


def draw_level_select(level_files: list[str], selected_level: int):
    screen.fill(BLACK)

    title = font.render("Select a Level", True, WHITE)
    screen.blit(title, ((WIDTH - WIDTHOFFSET) // 2 - 120, 100))

    for i, level in enumerate(level_files):
        colour = GREEN if i == selected_level else WHITE

        # This makes sure that '.json' is removed if it exists
        text = small_font.render(level.replace(".json", ""), True, colour)
        screen.blit(text, ((WIDTH - WIDTHOFFSET) // 2 - 80, 220 + i * 50))

    instructions = small_font.render(
        "UP/DOWN to choose, ENTER to play",
        True,
        WHITE,
    )

    screen.blit(instructions, ((WIDTH - WIDTHOFFSET) // 2 - 180, HEIGHT - 120))

def draw_game_background(song_name: str, selected_lanes: list[bool]):
    screen.fill(BLACK)
    
    song_text = small_font.render(song_name, True, WHITE)
    screen.blit(song_text, (WIDTH + 40 - WIDTHOFFSET, 20))
    
    # Drawing lanes
    for i in range(LANE_COUNT):
        x = i * LANE_WIDTH

        if selected_lanes[i]:
            pygame.draw.rect(
                screen,
                (100, 100, 100),
                (x, 0, LANE_WIDTH, HEIGHT),
            )
        pygame.draw.rect(
            screen,
            GRAY,
            (x, 0, LANE_WIDTH, HEIGHT),
            width=2,
        )

        # Key labels
        label = font.render(KEY_LABELS[i], True, WHITE)
        label_rect = label.get_rect(center=(x + LANE_WIDTH // 2, HEIGHT - 50))
        screen.blit(label, label_rect)

    # Draw hit line
    pygame.draw.line(
        screen,
        WHITE,
        (0, HIT_LINE_Y + NOTE_HEIGHT // 2),
        (WIDTH - WIDTHOFFSET, HIT_LINE_Y + NOTE_HEIGHT // 2),
        4,
    )

def draw_score(score, combo, misses):
    score_text = small_font.render(f"Score: {score}", True, WHITE)
    combo_text = small_font.render(f"Combo: {combo}", True, WHITE)
    miss_text = small_font.render(f"Misses: {misses}", True, WHITE)

    screen.blit(score_text, (10, 20))
    screen.blit(combo_text, (10, 55))
    screen.blit(miss_text, (10, 90))

def draw_results_screen(score, max_combo):
    end_text = font.render("Level Complete!", True, WHITE)
    combo_end = small_font.render(
        f"Score: {score}, Max Combo: {max_combo}",
        True,
        WHITE,
    )

    return_text = small_font.render(
        "Returning to level select...",
        True,
        WHITE,
    )

    screen.blit(end_text, ((WIDTH - WIDTHOFFSET) // 2 - 120, HEIGHT // 2 - 50))
    screen.blit(combo_end, ((WIDTH - WIDTHOFFSET) // 2 - 100, HEIGHT // 2))
    screen.blit(return_text, ((WIDTH - WIDTHOFFSET) // 2 - 160, HEIGHT // 2 + 50))

def draw_hand_state(img, range):
    img = img.transpose((1, 0, 2))
    surface = pygame.surfarray.make_surface(img)
    screen.blit(surface, (WIDTH//2 + 50, HEIGHT//2 - 100))
    enabled = range <= ACTIVATE_DIST
    BarWidth = 320
    if range > 120:
        range = 120
    slider_width = BarWidth * (range / 120)
    if range > ACTIVATE_DIST:
        bar_colour = (255,0,0)
    else:
        bar_colour = (0,255,0)
    if range >= 120 or range == False:
        bar_colour = (50,50,50)
    pygame.draw.rect(screen, bar_colour, (WIDTH // 2 + 50, HEIGHT // 2 + 140, BarWidth, 50))
    pygame.draw.rect(screen, (50,50,50), (WIDTH // 2 + 50, HEIGHT // 2 + 140, slider_width, 50))
    pygame.draw.rect(screen, (255,255,255), (WIDTH // 2 + 50 + 78, HEIGHT // 2 + 140, 10, 50))

def correct_lanes(selected_lanes: list[bool], target_lanes: list[int]) -> bool:
    """Determines if the correct lanes are selected to match the target lanes"""
    for i, lane in enumerate(selected_lanes):
        if bool(target_lanes[i]) != lane:
            return False
    return True


# THREAD 1
def startTransmission():
    asyncio.run(connect())

thread1 = threading.Thread(target=startTransmission) 
thread2 = threading.Thread(target=queueSoundEffect)


# -----------------------------
# Main loop
# -----------------------------
def main():
    running = True
    state = GameState.LEVEL_SELECT
    thread1.start()
    notes: list[NoteObject] = []
    level: Level
    note_index: int = 0 # Represents where we are in the level node spawn sequence
    level_names: list[str] = get_level_names()
    print(level_names)
    selected_level_index = 0
    selected_lanes = [False, False, False, False, False]
    frames_elapsed = 1
    score = 0
    combo = 0
    max_combo = 0
    misses = 0
    previousEnter = False

    fingers = [-1]
    img = -1
    enter = False
    range = -1

    # The difference in frames between when a note spawns and should be played
    spawn_play_offset = 0

    while running:
        clock.tick(FPS)
        frames_elapsed += 1

        # Spawning Logic
        if state == GameState.PLAYING:
            if len(level.gameplay_notes) > note_index:
                next_note = level.gameplay_notes[note_index]
                next_play_time = next_note.time_played * FPS * 3
                next_spawn_time = next_play_time - spawn_play_offset
                if frames_elapsed >= next_spawn_time:
                    notes.append(NoteObject(next_note, -NOTE_HEIGHT, level.speed))
                    note_index += 1

            # TODO start playing music if not already playing when frames_elapsed = 0

        if DEBUGFLAG == False:
            # Events
            if not fingerQueue.empty():
                fingers = fingerQueue.get()
            if not imageQueue.empty():
                img = imageQueue.get()
            if not rangeQueue.empty():
                enter = rangeQueue.get()
            print(fingers, enter, previousEnter)

        # Level select controls
        if state == GameState.LEVEL_SELECT:
            print("In level select")
            if DEBUGFLAG or enter:
                if DEBUGFLAG == True:
                    fingers = [1,1,1,1,1]
                
                # if sum(fingers) == 0:
                #     running = False
                if fingers == [0,1,0,0,0]: # Up Arrow
                    selected_level_index = (selected_level_index - 1) % len(level_names)

                elif fingers == [1,0,0,0,0]: # Down arrow
                    selected_level_index = (selected_level_index + 1) % len(level_names)

                # A level has been selected, so load it and start game
             
                elif fingers == [1,1,1,1,1]:
                    print("Loading level")
                    global startMusic 
                    startMusic = True
                    level = load_level("levels/" + level_names[selected_level_index])

                    notes.clear()

                    frames_elapsed = FPS * PRE_LEVEL_SECONDS * -1
                    score = 0
                    combo = 1
                    note_index = 0
                    misses = 0
                    max_combo = 1
                    selected_lanes = [False, False, False, False, False]
                    spawn_play_offset = (HIT_LINE_Y - NOTE_HEIGHT) / level.speed
                    state = GameState.PLAYING

        elif state == GameState.PLAYING:
            # This is currently set to track which of the keys are held, and trigger those keys
            # When enter is pressed. TODO change this to tracking which fingers are held up, and
            # trigger when the player moves their hand forward.
            # This doesn't even work lol because my keyboard can't accept 6 keys pressed at once

            if sum(fingers) > 0:
                for idx, fingerState in enumerate(fingers):
                    selected_lanes[idx] = (fingerState == 1)

            if enter and not previousEnter:
                hit_note = None

                for note in notes:
                    if note.is_hittable():
                        hit_note = note
                        break

                if hit_note and correct_lanes(selected_lanes, note.note.finger_positions):
                    notes.remove(hit_note)
                    score += 100 * combo
                    combo += 1
                    max_combo = max(max_combo, combo)
                else:
                    # Button was pressed with no notes in range or with wrong lanes selected
                    combo = 1
                    misses += 1
        previousEnter = enter
        for idx, fingerState in enumerate(fingers):
            selected_lanes[idx] = (fingerState == 1)

        # Game Logic
        if state == GameState.PLAYING:
            #Update Notes
            for note in notes[:]:
                note.update()

                # Missed note
                if note.y > HEIGHT:
                    notes.remove(note)
                    combo = 1
                    misses += 1
            
            # Level Completed
            if frames_elapsed >= level.length * FPS and not notes:
                state = GameState.RESULTS
                frames_elapsed = 0

        elif state == GameState.RESULTS:
            if frames_elapsed >= FPS * RESULTS_SCREEN_SECONDS:
                state = GameState.LEVEL_SELECT
        

        # Drawing
        if state == GameState.LEVEL_SELECT:
            draw_level_select(level_names, selected_level_index)
        elif state in (GameState.PLAYING, GameState.RESULTS):
            draw_game_background(level.name, selected_lanes)
            
            # Draw notes
            for note in notes:
                note.draw(screen)

            # Draw score
            draw_score(score, combo, misses)

            # Results screen
            if state == GameState.RESULTS:
                draw_results_screen(score, max_combo)
        if type(img) != int:
            draw_hand_state(img, range)
        pygame.display.flip()

    pygame.quit()

def getFingersThread():
    while True:
        try:
            fingers, img = getFingerData()
            fingerQueue.put(fingers)
            imageQueue.put(img)
        except:
            rangeQueue.put([-1])
            imageQueue.put(-1)


def getUltrasonicInputThread():
    while True:
        ser.reset_input_buffer()
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                jsonDict = json.loads(line)
                rangeQueue.put(jsonDict["Predicted"])
        except:
            rangeQueue.put(False)


if __name__ == "__main__":
    if DEBUGFLAG == False:
        reader = threading.Thread(target=getUltrasonicInputThread, daemon=True)
        reader.start()
        fingerReader = threading.Thread(target=getFingersThread, daemon=True)
        fingerReader.start()
    main()
    ser.close()
