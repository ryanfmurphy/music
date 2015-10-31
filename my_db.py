# my_db.py

import psycopg2, psycopg2.extras
import wikipedia, socket
from collections import namedtuple
import config

def conn_db(just_try=False):
    #return psycopg2.connect("dbname='murftown' user='murftown' password=''")
    dbname, username, password = config.db_info['dbname'], config.db_info['username'], config.db_info['password']
    if just_try:
        try:
            return psycopg2.connect("dbname='"+dbname+"' user='"+username+"' password='"+password+"'")
        except psycopg2.OperationalError:
            return None
    else:
        return psycopg2.connect("dbname='"+dbname+"' user='"+username+"' password='"+password+"'")

def cur_db(just_try=False):
    conn = conn_db(just_try)
    if conn:
        #cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        #cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cur = conn.cursor()
        return conn, cur
    else:
        return None, None

def table_names():
    conn,cur = cur_db()
    cur.execute('''
        SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
    ''')
    tables = (row[0] for row in cur)
    return tables

def build_tuple_models():
    tables = table_names()
    for table in tables:
        build_tuple_model(table)

def build_tuple_model(table_name):
    conn,cur = cur_db()
    cur.execute('''
        SELECT * FROM '''+table_name+'''
            LIMIT 0
    ''')
    field_names = (field.name for field in cur.description)
    ClassName = table_name.capitalize() + 'Tuple' #todo make a full CamelString fn
    NamedTupleRow = namedtuple(ClassName, field_names)
    globals()[ClassName] = NamedTupleRow
    return NamedTupleRow

def rand_adj():
    conn,cur = cur_db()
    cur.execute('SELECT word FROM random_adj')
    return cur.fetchall()[0][0]

def rand_noun():
    conn,cur = cur_db()
    cur.execute('SELECT word FROM random_noun')
    return cur.fetchall()[0][0]

def rand_noun_phrase():
    return rand_adj() + ' ' + rand_noun()

def get_description(topic):
    description, local = local_description(topic), True
    if not description:
        description, local = wikipedia.summary(topic), False
    return description, local

def save_description(topic, save_as=None):
    db = conn,cur = cur_db()

    summary = wikipedia.summary(topic)
    if save_as:
        topic_in_db = save_as
    else:
        topic_in_db = topic.lower()

    # update word, or add one if it doesn't exist
    rows = lookup_noun(topic_in_db, db=db)
    if rows is not None and len(rows):
        print "found relevant rows, updating..."
        add_description_to_word(word=topic_in_db, part_of_speech="noun", description=summary, db=db)
        return {
            'description': summary,
            'db_operation': 'UPDATE',
        }
    else:
        print "no rows, inserting..."
        add_word(word=topic_in_db, part_of_speech='noun', description=summary, db=db)
        return {
            'description': summary,
            'db_operation': 'INSERT',
        }


def lookup_noun(word, db=None, wheres=""):
    if db: conn,cur = db
    else: conn,cur = cur_db()
    query = """
        SELECT * FROM word
            WHERE word='""" + word + """'
              AND part_of_speech='noun'
              """ + wheres + """
        ORDER BY description
    """
    cur.execute(query)
    return tuple( fetch_tuples(cur, WordTuple) )
    #rows = cur.fetchall()
    #return tuple(WordTuple(*row) for row in rows)


def local_description(topic):
    rows = lookup_noun(topic, wheres="AND description IS NOT NULL")
    if len(rows):
        description = rows[0].description
        description = description.decode('utf-8')
        return description

def add_description_to_word(word, part_of_speech, description, db=None):
    #todo make description optional
    #todo use prepared statements
    if db: conn,cur = db
    else: conn,cur = cur_db()

    query = """
        UPDATE word
            SET description=$desc$""" + description + """$desc$
            WHERE word='""" + word + """'
              AND part_of_speech='""" + part_of_speech + """';
    """
    print query
    cur.execute(query)
    conn.commit()
    replicate_query(query)

    #todo add_description_to_word() - return value

def add_word(word, part_of_speech, description, db=None):
    #todo make description optional
    #todo use prepared statements
    if db: conn,cur = db
    else: conn,cur = cur_db()

    query = """
        INSERT INTO word
            (word, part_of_speech, description)
            VALUES
            (
            '""" + word + """', 'noun',
            $desc$"""+description+"""$desc$
            );
    """

    print query
    cur.execute(query)
    conn.commit()
    replicate_query(query)

    #todo add_word() - return value

def replication_q_name():
    hostname = socket.gethostname()
    return 'replication/replication_q' + '.' + hostname

def replicate_query(query):
    query = query.encode('utf8')
    filename = replication_q_name()
    print "opening " + filename + " for replication"
    with open(filename,'a') as fh:
        print "replicating into " + filename
        fh.write(query)

def strip_bom(unicode_str):
    return unicode(unicode_str.strip(codecs.BOM_UTF8), 'utf-8')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

def is_whole_number(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

def is_str(s):
    return isinstance(s, str) or isinstance(s, unicode)

def strn2word_id(strn):
    if is_whole_number(strn):
        return int(strn)
    else:
        word_rows = lookup_noun(strn)
        if word_rows:
            word_row = word_rows[0]
            return word_row.id  #todo #fixme change 'id' to 'word_id'
        else:
            return None
    

def word_has_tag(word_id, tag_word_id, db=None):
    if db: conn,cur = db
    else: conn,cur = cur_db()

    # a word, not a word id?  lookup the word
    if is_str(word_id): word_id = strn2word_id(word_id)
    if is_str(tag_word_id): tag_word_id = strn2word_id(tag_word_id)

    #todo factor validation into function
    #if not isinstance(word_id, int):     raise ValueError, "word_id must be int yet it's " + repr(word_id)
    #if not isinstance(tag_word_id, int): raise ValueError, "tag_word_id must be int yet it's " + repr(tag_word_id)

    query = """
        SELECT * FROM word_tagging
            WHERE tagged_word_id = {word_id}
              AND tag_word_id = {tag_word_id};
    """.format(
            word_id = word_id,
            tag_word_id = tag_word_id,
        )

    print query
    cur.execute(query)
    conn.commit()
    return tuple( fetch_tuples(cur, Word_taggingTuple) ) #todo fix TupleName


def fetch_tuples(cur, TupleClass):
    return (TupleClass(*row) for row in cur)


def taggings4word(word_id, db=None):
    if db: conn,cur = db
    else: conn,cur = cur_db()

    # a word, not a word id?  lookup the word
    if is_str(word_id): word_id = strn2word_id(word_id)
    #if not isinstance(word_id, int):     raise ValueError, "word_id must be int yet it's " + repr(word_id)

    if word_id:
        query = """
            SELECT word_tagging.*, word.word FROM word_tagging
                JOIN word
                    ON word.id = word_tagging.tag_word_id
                WHERE word_tagging.tagged_word_id = {word_id}
        """.format(
                word_id = word_id,
            )
        print query
        cur.execute(query)
        conn.commit()
        return ({ #todo use an Object here so we can add the attributes right on it
            'tagging': Word_taggingTuple(*row[:-1]), #todo fix name
            'tag_word': row[-1],
        } for row in cur)
    else:
        return []


def tags4word(word_id):
    taggings = taggings4word(word_id)
    return tuple(row['tag_word'] for row in taggings)


def tag_word(word_id, tag_word_id, db=None):
    if db: conn,cur = db
    else: conn,cur = cur_db()

    # a word, not a word id?  lookup the word
    if is_str(word_id): word_id = strn2word_id(word_id)
    if is_str(tag_word_id): tag_word_id = strn2word_id(tag_word_id)

    #if not isinstance(word_id, int):     raise ValueError, "word_id must be int yet it's " + repr(word_id)
    #if not isinstance(tag_word_id, int): raise ValueError, "tag_word_id must be int yet it's " + repr(tag_word_id)

    if word_has_tag(word_id, tag_word_id):
        return {
            'success': 1,
            'db_operation': None,
            'note': 'word '+str(word_id)+' already has tag '+str(tag_word_id),
        }

    query = """
        INSERT INTO word_tagging
            (tagged_word_id, tag_word_id)
            VALUES
            (
                {word_id},
                {tag_word_id}
            );
    """.format(
            word_id = word_id,
            tag_word_id = tag_word_id,
        )

    print query
    cur.execute(query)
    conn.commit()
    replicate_query(query)

    return {
        'success': 1,
        'db_operation': 'INSERT',
        'query': query,
    }
    

def get_all_words(db=None, wheres=""):
    if db: conn,cur = db
    else: conn,cur = cur_db()
    query = """
        SELECT * FROM word
        """ + wheres + """
    """
    cur.execute(query)
    #return cur.fetchall()
    return fetch_tuples(cur, WordTuple)
    #return tuple(WordTuple(*row) for row in rows)

try:
    build_tuple_models()
except psycopg2.OperationalError:
    print "Error setting up db: Could not build_tuple_models()"

