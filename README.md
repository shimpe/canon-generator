canon-generator
===============

Canon-generator: algorithmic composition using music21, scamp, abjad and python
* Written by Stefaan Himpe - 2013
* Revised to use python 3.8 and music21 6.3.0 - 2020 **NOTE: canon-generator now also depends on the scamp library to generate the final notation**

Code available under GPLv3. 

Simple tonal canon generator.
The main function contains some parameters that can be edited by
the user (for now, no UI/command line options available).

  *chords = "C F Am Dm G C"*
  * You can insert a new chord progression here.

  *scale = music21.scale.MajorScale("C")*
  * You can define a new scale in which the notes of the chords should be interpreted here

  *voices = 5*
  * Define the number of voices in your canon here

  *quarterLength = 2*
  * Define the length of the notes used to realize the chord progression (don't choose them too short, since the automatic spicing-up will make them shorter)

  *spice_depth = 1*
  * Define how many times a stream (recursively) should be spiced up, e.g. setting 2 will first spice up the chords, then again spice up the already spiced chords. Scores very quickly become rhytmically very complex for settings > 2

  *stacking = 1*
  * the code can generate multiple versions of the spiced up chord progression, and use those versions to create extra voices. E.g. setting stacking = 2 will turn a 3-voice canon into a 3\*2 = 6-voice canon

  *voice_transpositions =  { VOICE1 : +12, VOICE2 : 0, VOICE3 : -12, VOICE4: -24, VOICE5: 0 }*
  * allow extra octave jumps between voices

