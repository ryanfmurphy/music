import music, sys, subprocess as sp

def play_ascii_txt_simple(data):
    return music.play(
        [   ord(d)-48
            for d in data
        ],
        dur=.01
    )

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

def say_it(chars):
    chars = chars.replace("'", ' single quote ') \
                 .replace('"', ' double quote ') \
                 .replace('(', ' open paren ') \
                 .replace(')', ' close paren ') \
                 .replace('[', ' open bracket ') \
                 .replace(']', ' close bracket ') \
                 .replace('{', ' open brace ') \
                 .replace('}', ' close brace ') \
                 .replace('\\', ' backslash ') \
                 .replace('/', ' slash ') \
                 .replace('|', ' pipe ') \
                 .replace('&', ' amp ') \
                 .replace(';', ' semicolon ')
    return sp.call(['sayv','.5',chars])

def play_it(chars):
    pitches = []
    for t in range(3):
        for d in chars:
            pitches.append(
                    None
                if d in whitespace else
                    ord(d)-48
            )
        pause(pitches)
    music.play(pitches, dur=.1, vel=127)

def play_and_say_words(data):
    lines = data.split('\n')
    for line in lines:
        words = [word for word in line.split(' ') if len(word)>0]
        for word in words:
            say_it(word)
            play_it(word)
        # now the whole line
        if len(words) > 1:
            say_it('whole line: ' + line)
            play_it(line)

whitespace = '\t\n '

def play_and_say_lines(data):
    lines = data.split('\n')
    for line in lines:
        say_it(line)
        pitches = []
        for t in range(2):
            for d in line:
                if d not in whitespace:
                    pitches.append(ord(d)-48)
            pause(pitches)
        music.play(pitches, dur=.1, vel=127)
        
def get_file_handle(file_or_name):
    if isinstance(file_or_name, file):
        return file_or_name
    else:
        return open(filename_or_stream)

if __name__=='__main__':
    file_or_name = sys.argv[1] \
        if len(sys.argv) > 1 \
        else sys.stdin
    
    with get_file_handle(file_or_name) as fh:
        data = fh.read()
        play_and_say_words(data)
        #play_and_say_lines(data)
        #play_ascii_txt(data)


