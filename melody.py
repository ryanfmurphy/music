from midi import *
import my_db

def get_db_melody(id=None):
    if id is None: # random - #todo #fixme what if it hits a hole?
        id = random.randint(1,my_db.count_rows('melody'))
    melodyO = my_db.fetch_join_query('''
        select * from melody where id='''+str(id)+'''
    ''').next()[0]
    return melodyO

def play_db_melody(id=None):
    melodyO = get_db_melody(id)
    return play_strn(melodyO.melody)

