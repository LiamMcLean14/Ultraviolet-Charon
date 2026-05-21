import math

class AudioNote:
    """Defines an individual note played via speaker for a level"""
    # TODO once the speaker system is ready
    time_played: float


class GameplayNote:
    """
    Defines an individual note the player needs to hit.

    Attributes:
        time_played: The time that the note should be played, in seconds since the start of the song.
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
        