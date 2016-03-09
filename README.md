Music Fun in Python
===================

This module provides a framework of functionality for working
with MIDI-message-based music in Python, including:

* Functions for playing notes, chords, melodies (see midi.py)
* Functions for storing and playing back a song as a Python program (see fns.py)
* Functions for tracking simple rhythms of a real-time input (see rhythm.py)

Stay tuned for more information about this project.

~ Ryan


Setup
-----

* Clone this repo
* Install fluidsynth (or have a working midi synth running on your computer that you can send midi messages to)
* Install the `rtmidi` library: http://trac.chrisarndt.de/code/wiki/python-rtmidi/install%20
	* Python Dev Headers and Libraries
	* On Linux, Jack Server and Dev Packages - `jackd2` and `jackd2-dev`


Environment / Dependencies
--------------------------

You need:

* python (I'm using python 2.7)
* rtmidi for sending midi messages - https://pypi.python.org/pypi/python-rtmidi
* a MIDI device capable of receiving MIDI messages and coverting them to sound

For example, my Mac couldn't play the MIDI file directly (at least I couldn't
figure out how), so I had to install a Synth / MIDI server called fluidsynth,
and start it up via e.g.:

    fluidsynth -d "/path/to/GeneralUser GS FluidSynth v1.44.sf2"

    in my case it's 
        fluidsynth -d "~/dev/GeneralUser GS 1.44 FluidSynth/GeneralUser GS FluidSynth v1.44.sf2"


Let's make some noise!

