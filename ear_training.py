import midi, random
from time import sleep

def play_chord_for_awhile(chord):
    midi.chordname_on(chord)
    sleep(5)
    midi.chordname_off(chord)

if __name__ == '__main__':
    while True:
        chord = random.choice(('C','F','G'))
        play_chord_for_awhile(chord)

