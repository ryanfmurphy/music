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

    def __init__(self, prev_beat=None, avg_beat_time=None):
        self.time = time.time()
        self.prev_beat = prev_beat
        # the actual time from the last beat
        self.delta = self - self.prev_beat
        # the guess of the "musical" duration since the last beat
        self.delta_len_guess = self.guess_delta_len(avg_beat_time)
        self.which_beat_guess = self.current_beat_placement()

    def __repr__(self):
        return str(self.time) + ' (' + str(self.which_beat_guess) + ')'

    def __sub__(self, prev_beat):
        if isinstance(prev_beat, Beat):
            return self.time - prev_beat.time
        else:
            return None

    def prev_beat_placement(self):
        if self.prev_beat and hasattr(self.prev_beat, 'which_beat_guess'):
            return self.prev_beat.which_beat_guess
        else:
            return 0

    def current_beat_placement(self):
        if self.prev_beat and hasattr(self.prev_beat, 'which_beat_guess'):
            which_beat_guess = self.prev_beat.which_beat_guess + self.delta_len_guess
            which_beat_guess %= 4
            return which_beat_guess
        else:
            print("no prev_beat with placement, using 0 for which_beat_guess")
            return 0

    def guess_delta_len(self, avg_beat_time):
        'try to infer what the intended beat placement of the user beat is'
        prior_beat = self.prev_beat_placement()
        if avg_beat_time:
            # go through all these possible ratios and decide which is the closest match
            possible_ratios = [
                Fraction(1,4), Fraction(1,2), Fraction(3,4),
                # Fraction(1,3),
                Fraction(1), Fraction(3,2),
                    # Fraction(5,4), Fraction(7,4), 
                Fraction(2), Fraction(3,1),
                    Fraction(5,2),
                Fraction(4),
                Fraction(8),
                Fraction(16)
            ]
            # add the ratios that would bring us back to the next couple whole numbers
            next_beats = (int(prior_beat)+1, int(prior_beat)+2)
            for future_beat in next_beats:
                diff = future_beat - prior_beat
                if diff not in possible_ratios: #todo use a set for better #performance
                    #print('adding possible ratio', diff, 'to get to future_beat', future_beat)
                    possible_ratios.append(diff)

            best_ratio, best_distance_from_1 = Fraction(1), 1000000000 # large distance
            for possible_ratio in possible_ratios:
                multiple_of_this_ratio = self.delta / (possible_ratio * avg_beat_time)
                distance_from_1 = abs(multiple_of_this_ratio - 1)
                # if it's an oddball rhythm they better be super close or it's probably wrong
                # favor the simpler stronger beats
                target_beat = prior_beat + possible_ratio
                oddballness = Fraction(target_beat.denominator, 16)
                distance_from_1 *= oddballness
                # pit the new ratio against the current winner
                if distance_from_1 < best_distance_from_1:
                    best_ratio, best_distance_from_1 = possible_ratio, distance_from_1
            return best_ratio
        else:
            return Fraction(1)

    def print_which_beat(self):
        beat = self.which_beat_guess + 1
        if beat == 1:
            print('-'*20)
        print_fraction_as_mixed_number(beat)


def fraction_as_mixed_number(frac):
    whole_num = int(frac)
    leftover_frac = frac - whole_num
    return whole_num, leftover_frac

def print_fraction_as_mixed_number(frac):
    whole_num, leftover_frac = fraction_as_mixed_number(frac)
    if leftover_frac:
        print(whole_num, leftover_frac)
    else:
        print(whole_num)


def beats_sum_time_len(beats):
    return sum(beat.delta for beat in beats if beat.delta is not None)

def beats_sum_musical_len(beats):
    # delta_len_guess = 1 for quarter note, .5 for eighth note, etc
    return sum(beat.delta_len_guess for beat in beats)

def rolling_avg_beat_len(beats):
    'take list of Beats and avg their deltas'
    beats = tuple(beat for beat in beats if beat.time is not None) #todo do we need this None condition?
    if len(beats) == 0:
        return None # avoid div by 0
    else:
        return beats_sum_time_len(beats) / beats_sum_musical_len(beats)


def listen():
    'listen to beat (keystrokes for now) from user, learn beats / timing'
    beats = []
    beat = None
    which_beat_guess, beats_per_measure = 0, 4
    rolling_beat_len_guess = None
    prev_note = None

    adjusted_pitches = midi.close_big_intervals_interactive()
    adjusted_pitches.next() # prime the coroutine
    note_chars = []

    while True:
        prev_beat = beat

        # waits for user tap
        ch = getch()
        if ch == 'q':
            print('Quitting...')
            note_strn = ''.join(note_chars)
            return (beats, note_strn)

        # timing
        if len(beats) > 5: # only feed it the rolling avg once we're confident in it
            beat = Beat(prev_beat, rolling_beat_len_guess)
        else:
            beat = Beat(prev_beat)

        # record the space before the note if any
        if prev_beat and beat.delta_len_guess:
            subdivision_factor = 2
            remaining_time_slots = int(beat.delta_len_guess * subdivision_factor) - 1
            note_chars.append('-' * remaining_time_slots)
        # record the note itself
        note_chars.append(ch)

        # play music
        midi.note_off(prev_note)
        if ch in midi.note_numbers:
            raw_pitch = midi.note_numbers[ch]
            # get next adjusted pitch from coroutine
            note = adjusted_pitches.send(raw_pitch)
        else:
            note = None
            print("No note for key", ch)
        midi.note_on(note)
        prev_note = note

        # add to beat log
        beats.append(beat)
        # rolling avg beat length guess
        deltas = beats[-10:]
        rolling_beat_len_guess = rolling_avg_beat_len(deltas)

        # display
        #print(beat.delta, '-', beat)
        #print('delta len guess:', beat.delta_len_guess)
        #print('rolling beat len guess:', rolling_beat_len_guess)
        beat.print_which_beat()
        

if __name__ == '__main__':
    beats, note_strn = listen()
    print(note_strn)


