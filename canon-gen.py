import music21
import copy
import random

# define some readability constants
SINGLE_NOTE = 0
DOUBLE_NOTE = 1
methods = [SINGLE_NOTE, DOUBLE_NOTE]

ODD_UPPER = True
ODD_LOWER = False

VOICE1 = 0
VOICE2 = 1
VOICE3 = 2
VOICE4 = 3
VOICE5 = 4

def pairwise(iterable):
  """
  takes a list and returns a new list containing the elements pairwise
  with overlap

  s -> (s[0], s[1]), (s[1], s[2]), (s[2], s[3]), ..., (s[Last], None)
  """
  return zip(iterable, iterable[1:]) + [(iterable[-1], None)]

def median(lst, if_even_length_use_upper_element=False):
  """ return the median of a list """
  length = len(lst)

  if length == 0:
    return None

  if length == 1:
    return lst[0]

  if length % 2 != 0:
    # median of a list with odd lenght is well-defined
    return lst[(length-1)/2]
  else:
    # median of a list with even length is a bit tricky
    if not if_even_length_use_upper_element:
      return lst[(length-1)/2]
    else:
      return lst[(length)/2]

def realize_chord(chordstring, numofpitch=3, baseoctave=4, direction="ascending"):
  """
  given a chordstring like Am7, return a list of numofpitch pitches, starting in octave baseoctave, and ascending
  if direction == "descending", reverse the list of pitches before returning them
  """
  pitches = music21.harmony.ChordSymbol(chordstring).pitches
  num_iter = numofpitch/len(pitches)+1
  octave_correction = baseoctave - pitches[0].octave
  result = []
  actual_pitches = 0
  for i in range(num_iter):
    for p in pitches:
      if actual_pitches < numofpitch:
        newp = copy.deepcopy(p)
        newp.octave = newp.octave + octave_correction
        result.append(newp)
        actual_pitches += 1
      else:
        if direction == "ascending":
          return result
        else:
          result.reverse()
          return result
    octave_correction += 1

  if direction == "ascending":
    return result
  else:
    result.reverse()
    return result

class Identity(object):
  """
  transformation that transforms a note into itself
  when selecting transformations at random, it is 
  useful to have some identity transformations taking 
  place in order not to make the score too busy
  """
  def __init__(self):
    pass

  def transform(self, scale, note, note2=None):
    new_stream = music21.stream.Stream()
    new_stream.append(note)
    return new_stream


class OneToThree(object):
  """
  transformation that randomly transforms one note into three notes
  * total duration is kept
  * first note and last note equal the original note
  * middle note is the neighbour note
  """
  def __init__(self):
    pass

  def transform(self, scale, note):
    new_note = copy.deepcopy(note)
    
    if new_note.isRest:
      new_stream = music21.stream.Stream()
      new_stream.append(new_note)
      return new_stream

    possible_durations = [ #[ 1.0/3, 1.0/3, 1.0/3],
                           [ 0.5, 0.25, 0.25    ],
                           [ 0.25, 0.5, 0.25    ],
                           [ 0.25, 0.25, 0.5    ]
                         ]

    possible_steps = [
                        "ascending", 
                        "descending"
                     ]

    chosen_dur = random.choice(possible_durations)
    chosen_step = random.choice(possible_steps)

    new_note.quarterLength = chosen_dur[0]*note.quarterLength 
    new_stream = music21.stream.Stream()

    new_stream.append(new_note)

    new_note2 = music21.note.Note()
    next_pitch = scale.next(new_note.pitch, direction=chosen_step)
    new_note2.pitch = next_pitch
    new_note2.quarterLength = chosen_dur[1]*note.quarterLength
    new_stream.append(new_note2)

    new_note3 = copy.deepcopy(new_note)
    new_note3.quarterLength = chosen_dur[2]*note.quarterLength
    new_stream.append(new_note3)
    return new_stream


class TwoToThree(object):
  """
  transformation that looks at current and next note,
  and interpolates a note in between (a generalization of the concept
  of a "passing" note)

  total duration doesn't change: duration of current note is 
  spread over a copy of the current note and an interpolated note
  """
  def __init__(self):
    pass

  def transform(self, scale, note1, note2):
    new_note = copy.deepcopy(note1)
    
    if note2 is None:
      stream = music21.stream.Stream()
      stream.insert(0, new_note)
      return stream


    if new_note.isRest:
      new_stream = music21.stream.Stream()
      new_stream.append(new_note)
      return new_stream

    pitches = scale.getPitches(new_note.pitch, note2.pitch)
    rounding_strategy = random.choice([ODD_UPPER, ODD_LOWER])

    possible_durations = [ #[ 1.0/3, 2.0/3],
                           #[ 2.0/3, 1.0/3],
                           [ 0.5, 0.5    ],
                           [ 0.75, 0.25  ],
                           #[ 0.25, 0.75  ]
                         ]

    chosen_dur = random.choice(possible_durations)

    new_note.quarterLength = chosen_dur[0]*note1.quarterLength
    new_stream = music21.stream.Stream()
    new_stream.append(new_note)

    new_note2 = copy.deepcopy(new_note)
    new_note2.pitch = median(pitches, rounding_strategy)
    new_note2.quarterLength = chosen_dur[1]*note1.quarterLength
    new_stream.append(new_note2)
    
    return new_stream


class TwoToFour(object):
  """
  transformation that looks at next note,
  creates notes oscillates a single scale degree
  above and below the next note, and uses those
  notes in the current beat (kind of cambiata?)
  """
  def __init__(self):
    pass

  def transform(self, scale, note1, note2):
    new_note = copy.deepcopy(note1)
    
    if note2 is None:
      stream = music21.stream.Stream()
      stream.insert(0, new_note)
      return stream


    if new_note.isRest:
      new_stream = music21.stream.Stream()
      new_stream.append(new_note)
      return new_stream

    possible_durations = [ 
                            [ 0.5, 0.25, 0.25 ],
                            [ 0.25, 0.5, 0.25 ]
                         ]
    chosen_dur = random.choice(possible_durations)

    possible_directions = [ 
                            "ascending", 
                            "descending" 
                          ]
    chosen_direction = random.choice(possible_directions)
    other_direction = list(set(possible_directions) - set([chosen_direction]))[0]

    new_note.quarterLength = chosen_dur[0]*note1.quarterLength
    new_stream = music21.stream.Stream()
    new_stream.append(new_note)

    new_note2 = copy.deepcopy(note2)
    new_note2.pitch = scale.next(note2.pitch, direction=chosen_direction) 
    new_note2.quarterLength = chosen_dur[1]*note1.quarterLength
    new_stream.append(new_note2)

    new_note3 = copy.deepcopy(note2)
    new_note3.pitch = scale.next(note2.pitch, direction=other_direction)
    new_note3.quarterLength = chosen_dur[2]*note1.quarterLength
    new_stream.append(new_note3)
    
    return new_stream

# list of transformations that transform a single note to a series of new notes 
# identity is listed more than once to increase the chance of it getting chosen
single_note_transformers = [Identity,
                            Identity,
                            OneToThree
                           ]

# list of transformations that transform a single note based on both current and next note
# idenity is listed more than once to give it more chance of being chosen
double_note_transformers = [Identity,
                            Identity,
                            TwoToThree,
                            TwoToFour,
                           ]

def spiceup_streams(streams, scale, repetitions=1):  
  """
  function that takes a stream of parts
  and spices up every part using the
  Identity, OneToThree, TwoToThree, TwoToFour, ... 
  transformations

  * it requires a scale in which to interpret the streams
  * it can create "repetitions" spiced sequences of the given stream
  """
  newtotalstream = music21.stream.Stream()
  for i, part in enumerate(streams):
    newstream = music21.stream.Stream()
    for x in range(repetitions):
      for note, nextnote in pairwise(part.notesAndRests):
        new_note = copy.deepcopy(note)
        new_nextnote = copy.deepcopy(nextnote)
        method = random.choice(methods)
        if method == SINGLE_NOTE:
          trafo = random.choice(single_note_transformers)()
          newstream.append(trafo.transform(scale, new_note).flat.elements)
        elif method == DOUBLE_NOTE:
          trafo = random.choice(double_note_transformers)()
          newstream.append(trafo.transform(scale, new_note, new_nextnote).flat.elements)
    newtotalstream.insert(0, newstream)
  return newtotalstream

def serialize_stream(stream, repeats=1):
  """
  function that takes a stream of parallel parts
  and returns a stream with all parts sequenced one after the other
  """
  new_stream = music21.stream.Stream() 
  copies = len(stream)
  for i in range(copies): 
    for part in reversed(stream):
      length = part.duration.quarterLength
      new_stream.append(copy.deepcopy(part.flat.elements))
  return new_stream, length

def canon(serialized_stream, delay, voices, extra_transposition_map={}):
  """
  function that takes serialized stream and sequences it against
  itself voices times with a delay "delay"
  """
  new_stream = music21.stream.Stream()
  total_length = 0
  for i in range(voices):
    import copy
    interval = 0
    if i in extra_transposition_map:
      interval = extra_transposition_map[i]
    new_stream.insert(total_length, copy.deepcopy(serialized_stream).transpose(interval))
    total_length += delay
  return new_stream


if __name__ == "__main__":
  ############################################################################
  #
  # START OF USER EDITABLE CODE
  #
  ############################################################################
  # define a chord progression that serves as basis for the canon (change this!)
  chords = "C F Am Dm G C"
  # scale in which to interpret these chords
  scale = music21.scale.MajorScale("C")
  # realize the chords using the given number of voices (e.g. 4)
  voices = 5
  # realize the chords in octave 4 (e.g. 4)
  octave = 4
  # realize the chords using half notes (e.g. 1 for a whole note)
  quarterLength = 2
  # number of times to spice-up the streams (e.g. 2)
  spice_depth = 1
  # how many instances of the same chords to stack (e.g. 2)
  stacking = 1
  # define extra transpositions for different voices (e.g. +12, -24, ...)
  # note that the currently implemented method only gives good results with multiples of 12
  voice_transpositions = { VOICE1 : +12, VOICE2 : 0, VOICE3 : -12, VOICE4: -24, VOICE5: 0 } 
  ############################################################################
  #
  # END OF USER EDITABLE CODE
  #
  ############################################################################

  # prepare some streams: one per voice
  # all bass notes of each chord form one voice
  # all 2nd notes of each chord form a second voice
  # ...
  # convert chords to notes and stuff into a stream
  streams = {}
  splitted_chords = chords.split(" ")
  for v in range(voices):
    streams[v] = music21.stream.Stream()
  # split each chord into a separate voice
  for c in splitted_chords:
    pitches = realize_chord(c, voices, octave, direction="descending")
    for v in range(voices):
      note = music21.note.Note(pitches[v])
      note.quarterLength = quarterLength
      streams[v].append(note)

  # combine all voices to one big stream
  totalstream = music21.stream.Stream()
  for r in range(stacking):
    for s in streams:
      totalstream.insert(0, copy.deepcopy(streams[s]))

  # add some spice to the boring chords. sugar and spice is always nice
  spiced_streams = [totalstream]
  for s in range(spice_depth):
    # each iteration spices up the stream that was already spiced up in the previous iteration,
    # leading to spicier and spicier streams
    spiced_streams.append(spiceup_streams(spiced_streams[s], scale))
 
  # debug code: visualize the spiced up chords, and allow the user to abort
  # canon generation if the result is too horrible
  spiced_streams[-1].show("musicxml")
  answer = None
  while answer not in ['y','Y','n','N']:
    answer = raw_input("continue to generate canon from this spiced up chord progression? [y/n]: ")

  if answer in [ 'y', 'Y' ]:
    # unfold the final spiced up chord progression into a serialized stream
    ser, delay = serialize_stream(spiced_streams[-1])

    # and turn it into a canon. Add extra transpositions to some voices to create some diversity
    canonized = canon(ser, delay, voices*stacking, voice_transpositions) 

    # show the final product
    canonized.show("musicxml")

