import midi, random
from time import sleep

#todo - make web interface with pretty lilypads and frogs and leaves and stuff
        # frogs could turn other colors as student masters levels

#todo - add ear training games
#-----------------------------
# go through cycle of 4ths/5ths, have student name chord as it's played
# go chromatically through major triads, have student spell out each chord
# randomly choose a chord and a scale step say e.g. "What's the 3rd of F?"
    # play the chord and the note, and have the student say the note
    # gradually add minor, 7ths, sus chords, diminished, augmented, etc
# relationships of chords to one another
    # 1 4 5?
        # show simple songs like Mary Had A Little Lamb
            # and explain where the chord goes from I to V etc
        # or Happy Birthday now that it's not copyrighted!
            # has a 4 in it
    # dominant - tonic relationship?
    # 2-5-1?
    # go thru the whole major scale using triads? I ii iii IV V vi vii(dim)
    # play snippets of popular tunes and analyze chord progression?

#todo - after each step, ask student if that made sense
    # the "Wait a minute" / "Hold on a sec" button

def play_chord_for_awhile(chord):
    midi.chordname_on(chord)
    sleep(5)
    midi.chordname_off(chord)

if __name__ == '__main__':
    while True:
        chord = random.choice(('C','F','G'))
        play_chord_for_awhile(chord)

