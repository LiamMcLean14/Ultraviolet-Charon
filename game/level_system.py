import math
import json
from pathlib import Path
from time import sleep

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
    
    def __str__(self) -> str:
        return f"{self.hertz} Hz at {self.time_played} seconds"



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
    _string_rep: str

    def __init__(self, time_played: float, finger_positions: list[int]) -> None:
        if time_played < 0:
            raise ValueError(f"Invalid time played: {time_played}. Time played must not be < 0")
        self.time_played = time_played

        if len(finger_positions) != 5:
            raise ValueError(f"Finger positions must be a list of 5 integers for each finger")
        self.finger_positions = finger_positions
        
        # Calculating it here prevents having to repeatedly do this
        position_reps = []
        for position in finger_positions:
            position_reps.append("#" if position else "-")
        self._string_rep = "".join(position_reps)

    def __str__(self) -> str:
        return self._string_rep
        



class Level:
    """
    Defines a level for the rhythm game.
    
    Attributes:
        name: The level's name
        length: The level's length, in seconds
        song: The wav that should be played in the sounds/ directory
        difficulty: The level's difficulty out of 5. It is not checked, so can be any number.
        audio_notes: A list of Audio notes that will be played via the speaker.
                     If multiple notes have the same time_played, all but 1 will be removed.
                     If a note's time_played > the level's length, it will be removed.
        gameplay_notes: A list of gameplay notes that the player will need to play
                        If multiple notes have the same time_played, all but 1 will be removed.
                        If a note's time_played > the level's length, it will be removed.
    """
    name: str
    description: str
    song: str
    length: float
    difficulty: float
    speed: int
    audio_notes: list[AudioNote]
    gameplay_notes: list[GameplayNote]

    def __init__(self, name: str, description: str, song: str, length: float, difficulty: float, speed: int,
                    audio_notes: list[AudioNote], gameplay_notes: list[GameplayNote]) -> None:
        self.name = name
        self.description = description
        
        self.song = song
        if length < 0:
            raise ValueError(f"Invalid length: {length}. Length must not be < 0")
        self.length = length

        self.difficulty = difficulty
        self.speed = speed

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
    
    def __str__(self) -> str:
        parts = []
        
        parts.append(f"Level Name: {self.name}")
        parts.append(f"Description: {self.description}")
        parts.append(f"Difficulty: {self.difficulty} / 5")
        
        parts.append(f"Audio Notes:")
        for audio_note in self.audio_notes:
            parts.append(str(audio_note))
        
        parts.append(f"Gameplay Notes:")
        for gameplay_note in self.gameplay_notes:
            parts.append(f"{str(gameplay_note)} at {gameplay_note.time_played} seconds")
        
        return "\n".join(parts)
    
    def detailed_level_view(self, increment: float, empty_row_str: str="-----") -> list[str]:
        """
        Represents the level at the given time as rows representing the gameplay notes 
        (if any) for each increment of time. For example, if the level length is 10 seconds, 
        detailed_level_view(0.5) will return 20 rows representing the gameplay notes
        at each 0.5 second timespan.
        If multiple notes are present in a timespan, only the first will be represented.
        If no notes are present for a row, it will be filled by empty_row_str
        The first rows will be at the start of the list, and last rows at the end.
        Note that this means calling print() on the detailed view will have the first rows
        at the top.
        """
        row_strings: list[str] = []
        index = 0
        time = 0

        # Work through the list of gameplay notes.
        while (time < self.length):
            # If there is a note between time and time + increment,
            # add it to the list and move through the notes list until there isn't
            notes_found: list[str] = []
            while index < len(self.gameplay_notes) and self.gameplay_notes[index].time_played < (time + increment):
                notes_found.append(str(self.gameplay_notes[index]))
                index += 1
            
            # This will look awkward if multiple notes are in a row, but fine otherwise
            row_strings.append(" and ".join(notes_found) if notes_found else empty_row_str)
            time += increment
        
        return row_strings

def view_subsection(view: list[str], rows: int, increment: float, current_time: float) -> str:
    if rows <= 0:
        return ""
    if increment <= 0:
        raise ValueError(f"Increment must be > 0 but was {increment}")
    starting_index = int(current_time // increment)
    if starting_index >= len(view):
        return "Level is finished"
    
    index = starting_index
    subview_rows = []
    while index < starting_index + rows:
        subview_rows.append(view[index] if index < len(view) else "")
        index += 1

    # We want the next row to be printed at the bottom, so reverse the list
    subview_rows.reverse()
    return "\n".join(subview_rows)

def get_level_names(path: str="levels") -> list[str]:
    """
    Gets the name of all json files in the given folder.
    The default path is the levels folder
    """
    # Get the directory this Python file is in
    base_dir = Path(__file__).parent

    # Build the path to the levels folder
    level_path = base_dir / path

    return [f.name for f in level_path.glob("*.json")]


def load_level(path: str) -> Level:
    """
    Loads a level with the given path, relative to this file.
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
    #for note in data["audio_notes"]:
    #    audio_notes.append(AudioNote(note["time_played"], note["hertz"]))

    gameplay_notes = []
    for note in data["gameplay_notes"]:
        gameplay_notes.append(GameplayNote(note["time_played"], note["finger_positions"]))

    return Level(
        name=data["name"],
        description=data["description"],
        song=data["song"],
        length=data["length"],
        difficulty=data["difficulty"],
        speed=data["speed"],
        audio_notes=audio_notes,
        gameplay_notes=gameplay_notes
    )


def main():
    #Test loading the sample level
    sample_level = load_level("levels/sample.json")
    print(sample_level)
    level_view = sample_level.detailed_level_view(0.25)
    current_time = 0
    for i in range(40):
        print(view_subsection(level_view, 10, 0.25, current_time))
        sleep(0.25)
        current_time += 0.25
        # Clears the previous display for the next one
        print("\033[10A\033[J", end="") 



if __name__ == "__main__":
    main()
