tests = [
    # each cell is a 16th note (1/4 beat)

    # passing frequently
    'c---c---c---c---c---c---c---c---c---c---c---c---c',
    'c---c---c---c---c---e-d-c---e-d-c---c--de-c-d-e-c',
    'c---c---c---c---c---c---c---c---c---c---c---c---c---c---c---c---c-d-e-f-e-d-c-d-c-d-e-f-e-d-c-d-c-d-e-f-g-e-f-e-d--ef--ed--ef--ed---d---d-----e-c',

    # passes sometimes, fails a lot
    'c---c---c---c---c---c---c---c---c-----g-e---d---c---d---e---c---d-----------e---c---------g-c---c---c---c---c---c---------g-e---d---c---d---e---c---------g-e---d---c---d---e-----c-------g-e---d---c---d---e---a-e---e-d-c-d---c',
    'c---c---c---c---c---c---c---c---c---------g-e---d',

    # fails all the time
]
