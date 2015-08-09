# use with python3? nawwww

'''
#todo beat detection
    - the user hits a key repeatedly and the computer figures out how much time is going on between

#todo running avg function

'''

from __future__ import print_function
from getkey import getch
import datetime, time
from fractions import Fraction
import midi


class Beat(object):

    def __init__(self, prev_beat=None, which_beat_guess=None, avg_beat_time=None):
        self.time = time.time()
        self.prev_beat = prev_beat
        # the actual time from the last beat
        self.delta = self - self.prev_beat
        # the guess of the "musical" duration since the last beat
        self.delta_len_guess = self.guess_delta_len(avg_beat_time)
        self.which_beat_guess = which_beat_guess

    def __repr__(self):
        return str(self.time) + ' (' + str(self.which_beat_guess) + ')'

    def __sub__(self, prev_beat):
        if isinstance(prev_beat, Beat):
            return self.time - prev_beat.time
        else:
            return None

    def guess_delta_len(self, avg_beat_time):
        if avg_beat_time:
            possible_ratios = [
                Fraction(1,4), Fraction(1,3), Fraction(1,2),
                Fraction(1), Fraction(2), Fraction(4), Fraction(8), Fraction(16)
            ]
            best_ratio, best_distance_from_1 = Fraction(1), 1000000000 # large distance
            for possible_ratio in possible_ratios:
                multiple_of_this_ratio = self.delta / (possible_ratio * avg_beat_time)
                distance_from_1 = abs(multiple_of_this_ratio - 1)
                if distance_from_1 < best_distance_from_1:
                    best_ratio, best_distance_from_1 = possible_ratio, distance_from_1
            return best_ratio
        else:
            return Fraction(1)


def beats_sum_time_len(beats):
    return sum(beat.delta for beat in beats if beat.delta is not None)

def beats_sum_musical_len(beats):
    return sum(beat.delta_len_guess for beat in beats)

def rolling_avg(L):
    'take list of Beats and avg their deltas'
    L = tuple(beat for beat in L if beat.time is not None)
    if len(L) == 0:
        return None
    else:
        return beats_sum_time_len(L) / beats_sum_musical_len(L)


def listen():
    'listen to beat (keystrokes for now) from user, learn beats / timing'
    beats = []
    beat = None
    which_beat_guess, beats_per_measure = 0, 4
    rolling_beat_len_guess = None
    prev_note = None
    while True:
        prev_beat = beat
        # waits for user tap
        ch = getch()
        if ch == 'q':
            print('Quitting...')
            return beats
        # timing
        if len(beats) > 10: # only feed it the rolling avg once we're confident in it
            beat = Beat(prev_beat, which_beat_guess, rolling_beat_len_guess)
        else:
            beat = Beat(prev_beat, which_beat_guess)
        which_beat_guess += 1
        which_beat_guess %= 4
        # play music
        midi.note_off(prev_note)
        note = midi.note_numbers[ch]
        midi.note_on(note)
        prev_note = note
        # update collections
        beats.append(beat)
        # rolling avg beat length guess
        deltas = beats[-10:]
        rolling_beat_len_guess = rolling_avg(deltas)
        # display
        print(beat.delta, '-', beat)
        print('delta len guess:', beat.delta_len_guess)
        print('rolling beat len guess:', rolling_beat_len_guess)
        

if __name__ == '__main__':
    beats = listen()


