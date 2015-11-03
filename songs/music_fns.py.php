<?php
    $notes = array('a','b','c','d','e','f','g');
    #$note = $notes[array_rand($notes)];

    foreach ($notes as $note) {
?>

@f.start_chord(lambda: f.options('F','G','C','D7','Am','Em','E7'))
def aaaabb<?= $note ?>bCCCC():
    return 'bbbbaa<?= $note ?>agggg'

<?php
    }
?>
