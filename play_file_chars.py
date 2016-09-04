import music, sys, subprocess as sp

def play_ascii_txt_simple(data):
    return music.play([ord(d)-48 for d in data], dur=.01)

def pause(pitches):
    pitches.append(None)
    pitches.append(None)
    pitches.append(None)

def play_ascii_txt(data):
    lines = data.split('\n')
    pitches = []
    for line in lines:
        for t in range(3):
            for d in line:
                pitches.append(ord(d)-48)
            pause(pitches)
    music.play(pitches, dur=.02)

def play_and_say(data):
    lines = data.split('\n')
    for line in lines:
        words = line.split(' ')
        for word in words:
            sp.call(['sayv','.5',word])
            pitches = []
            for t in range(3):
                for d in word:
                    pitches.append(ord(d)-48)
                pause(pitches)
            music.play(pitches, dur=.1, vel=127)

whitespace = '\t\n '

def play_and_say_lines(data):
    lines = data.split('\n')
    for line in lines:
        sp.call(['sayv','.5',line])
        pitches = []
        for t in range(3):
            for d in line:
                if d not in whitespace:
                    pitches.append(ord(d)-48)
            pause(pitches)
        music.play(pitches, dur=.1, vel=127)
        

if __name__=='__main__':
    filename = sys.argv[1]
    with open(filename) as fh:
        data = fh.read()
        play_and_say_lines(data)
        #play_ascii_txt(data)


