import math
import json
from pathlib import Path

class AudioNote:
    """
    Defines an individual note played via speaker for a level
    
    Attributes:
        time_played: The time that the note should be played, in seconds since the start of the level.
        hertz: The tone a note is played (in Hz)
    """
    time_played: float
    hertz: int
    def __init__(self, time_played: float, hertz: int) -> None:
        if time_played < 0:
            raise ValueError(f"Invalid time played: {time_played}. Time played must not be < 0")
        self.time_played = time_played

        # TODO value check tone
        self.hertz = hertz



class GameplayNote:
    """
    Defines an individual note the player needs to hit.

    Attributes:
        time_played: The time that the note should be played, in seconds since the start of the level.
        finger_positions: The finger positions needed to play the note. Represented by 5 integers,
                          With each represnting whether each finger (from left to right) should be held up.
                          1 (or any truthy value) represents it being up, 0 represents down.
    """
    time_played: float
    finger_positions: list[int]

    def __init__(self, time_played: float, finger_positions: list[bool]) -> None:
        if time_played < 0:
            raise ValueError(f"Invalid time played: {time_played}. Time played must not be < 0")
        self.time_played = time_played

        if len(finger_positions) != 5:
            raise ValueError(f"Finger positions must be a list of 5 integers for each finger")
        self.finger_positions = finger_positions



class Level:
    """
    Defines a level for the rhythm game.
    
    Attributes:
        name: The level's name
        length: The level's length, in seconds
        difficulty: An arbitrary value representing the level's difficulty
        audio_notes: A list of Audio notes that will be played via the speaker.
                     If multiple notes have the same time_played, all but 1 will be removed.
                     If a note's time_played > the level's length, it will be removed.
        gameplay_notes: A list of gameplay notes that the player will need to play
                        If multiple notes have the same time_played, all but 1 will be removed.
                        If a note's time_played > the level's length, it will be removed.
    """
    name: str
    length: float
    difficulty: int
    audio_notes: list[AudioNote]
    gameplay_notes: list[GameplayNote]

    def __init__(self, name: str, length: float, difficulty: int,
                    audio_notes: list[AudioNote], gameplay_notes: list[GameplayNote]) -> None:
        self.name = name
        
        if length < 0:
            raise ValueError(f"Invalid length: {length}. Length must not be < 0")
        self.length = length

        self.difficulty = difficulty

        # The notes will be sorted by their time played to play them more easily
        self.audio_notes = []
        sorted_audio_notes = sorted(audio_notes, key=lambda note: note.time_played)

        # Remove notes above the level length or with duplicate timings
        notes_above_length = 0
        duplicate_timings = 0

        for note in sorted_audio_notes:
            if note.time_played < 0:
                # This shouldn't be possible but just in case
                raise ValueError(f"An audio note has in invalid time played: {note.time_played}."
                                  "This should have been caught while initialising the note.")
            elif note.time_played > length:
                notes_above_length += 1
            elif self.audio_notes and math.isclose(note.time_played, self.audio_notes[-1].time_played):
                duplicate_timings += 1
            else:
                self.audio_notes.append(note)
        
        # Notify user if any notes were removed
        if (notes_above_length > 0):
            print(f"Warning: {notes_above_length} audio notes were removed for having a time_played > level length")
        if (duplicate_timings > 0):
            print(f"Warning: {duplicate_timings} audio notes were removed for duplicate timings")


        # Repeat for gameplay notes
        self.gameplay_notes = []
        sorted_gameplay_notes = sorted(gameplay_notes, key=lambda note: note.time_played)

        notes_above_length = 0
        duplicate_timings = 0

        for note in sorted_gameplay_notes:
            if note.time_played < 0:
                # This shouldn't be possible but just in case
                raise ValueError(f"A gameplay note has in invalid time played: {note.time_played}."
                                  "This should have been caught while initialising the note.")
            elif note.time_played > length:
                notes_above_length += 1
            elif self.gameplay_notes and math.isclose(note.time_played, self.gameplay_notes[-1].time_played):
                duplicate_timings += 1
            else:
                self.gameplay_notes.append(note)
        
        if (notes_above_length > 0):
            print(f"Warning: {notes_above_length} gameplay notes were removed for having a time_played > level length")
        if (duplicate_timings > 0):
            print(f"Warning: {duplicate_timings} gameplay notes were removed for duplicate timings")

def load_level(path: str) -> Level:
    """
    Loads a level with the given path, relative to this file
    e.g. load_level("levels/sample.json") will load levels/sample.json
    """
    # Get the directory this Python file is in
    base_dir = Path(__file__).parent

    # Build the path to the levels folder
    level_path = base_dir / path

    # Open the folder and parse it as JSON
    with open(level_path, "r") as file:
        data = json.load(file)

    audio_notes = []
    for note in data["audio_notes"]:
        audio_notes.append(AudioNote(note["time_played"], note["hertz"]))

    gameplay_notes = []
    for note in data["gameplay_notes"]:
        gameplay_notes.append(GameplayNote(note["time_played"], note["finger_positions"]))

    return Level(
        name=data["name"],
        length=data["length"],
        difficulty=data["difficulty"],
        audio_notes=audio_notes,
        gameplay_notes=gameplay_notes
    )


def main():
    #Test loading the sample level
    sample_level = load_level("levels/sample.json")
    print(sample_level)


if __name__ == "__main__":
    main()