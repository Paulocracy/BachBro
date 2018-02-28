# BachBro - Free and open-source tools for musicians and music researchers
(c) 2018 Paulocracy

## 1. Introduction
BachBro is a set of free and open-source tools for musicians
and music researches which lack in most other common music programs. All tools are
provided in a single graphical user interface.

 An additional music data editor, which works in a modern web browser, is also
provided.

 Except of the audio recording, all tools work with non-western quarter-tones.
"b2" stands for a half-flat, "#2" for a half-sharp.

BachBro's tools are:
 1.  "View scales/chords": Viewing of scales and chords (also with non-western quarter tones)
                           on piano and a user selected instrument. The scale can
                           also be shown as a MusicXML file in a user selected sheet
                           editor.<br>
                           This tool is useful to find out how a scale can be played on an instrument
                           and to analyse the scale visually.<br>
                           It is also possible to click on the notes of the user selected
                           instruments to show a user selected range of intervals. The set
                           can intervals can be also chosen from a user selected genre, such
                           as 'classical western' music.
 2. "Find scales/chords": The user can select or deselect notes (in ascending order and in
                           the order of the user selected instrument), and find scales which
                           contain the user selected notes, i.e. all scales which do not
                           have at least one of these notes are not shown.
 3. "Fractions calculator": Calculation of rhytms as a sum of note lengths. It is
                            useful for determining a rhythm from a heard piece of
                            music.
 4.  "Record from .wav or via microphone": This is a GUI interface for 'aubio', an external
                                            note recognition program. If the user has installed
                                            aubio on his system, he can perform an aubio note
                                            recognition from a prerecorded .wav audio file
                                            or by playing music to his microphone.<br>
                                            The note recognition result is shown as a MusicXML,
                                            which is opened in the user selected sheet editor.


## 2. How to install and run BachBro
Read [INSTALL.txt](./INSTALL.txt) for an explanation of how to install and run BachBro.

## 3. How to learn to use BachBro's functions
 The best starting point to learn how to use BachBro is its manual,
which can be found in BachBro's "docs" subfolder. It can be accessed
in BachBro's window menu via "Help->Manual (in web browser)", too.


## 4. How to edit the music theory data
 All music theory data used by BachBro is written in human readable JSON files.
You can find these JSON files in the "data" subfolder. The most convinient way to edit
the data is the "BachBro data editor", another open-source program, which is
provided with BachBro, too. Simply open "data_editor.html" in BachBro's
main folder with a modern web browser (e.g. Mozilla Firefox), allowing JavaScript and
pop-ups for this file.

 BachBro's manual (in the "docs" subfolder) explains and shows the usage of
the data editor in the section "BachBro data editor".


## 5. Licensing
BachBro is free and open-source.
* Read [LICENSE](./LICENSE) for BachBro's program license.
* Read [NOTICE.txt](./NOTICE.txt) for additional license information, i.e. the licensing of the
  external projects which are used by BachBro.
* Read the chapter "Addendum: GNU Free Documentation License" in [BachBro's manual](./docs/manual.html)
  in order to read the license of BachBro's manual.
