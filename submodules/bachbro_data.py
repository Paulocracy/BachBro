#!/usr/bin/env python
#
# musician_assistant_data.py
# Copyright (C) 2018 Paulocracy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""musician_assistant_data.py - Loading and analysing of music theory data.

This module contains all methods for the loading of the music theory data
from the JSON files as well as for their analysis. It can be used
independently from BachBro's GUI classes.
"""

import collections
import json
import os
import random
import subprocess
import sys
import tkinter.messagebox
import xml.etree.ElementTree as et


class Note:
    """Class representing a musical note. Is used for MusicXML export."""
    def __init__(self, name, octave, alter, accidental, duration, type_=None, in_chord=False):
        """Sets all Note instances.
        
        Arguments:
        >name: The note's note name (e.g. 'C').
        >octave: The note's octave as an integer.
        >alter: The MusicXML alter value, i.e. '1' for a sharp and '-1'
                for a flat.
        >accidental: The note's accidental that shall be shown, e.g. a
                     'quarter flat'.
        >duration: The note's length as an integer. The interpretation
                   of this value is dependent on the MusicXML where the
                   Note is written to.
        >type_=None: Shows if the note is e.g. a 'quarter' or a 'half' note.
        >in_chord=False: True, if the Note is part of a chord. False, if
                         not.
        """
        self.name = name
        self.octave = octave
        self.alter = alter
        self.accidental = accidental
        self.type_ = type_
        self.duration = duration
        self.in_chord = in_chord


class MidiNote:
    """Class for a MIDI note as it is represented in an aubio output.
    
    In this kind of outut, the note hat a MIDI number and a start and
    end time.
    """
    def __init__(self, midi_number, start, end):
        """Sets all MidiNote member variables.
        
        Arguments:
        >midi_number: The MIDI note's midi number.
        >start: The MIDI note's start time.
        >end: The MIDI note's end time. It will be stored as 'length' after
              the variable 'start' is substracted of it.
        """
        self.midi_number = int(float(midi_number))
        self.length = float(end) - float(start)


class BachBroData:
    """Main class for storage and processing of music theory data."""
    def __init__(self, datapath):
        """Constructor. Loads JSON data into Python variables.
        
        Most defined member variables are ordered dictionaries containing
        the JSON data.
        
        Arguments:
        >datapath: The path of the music theory data's JSON files.
        """
        self.clefs = self._get_json_file_data(datapath+"clefs.json")
        self.genres = self._get_json_file_data(datapath+"genres.json")
        self.instruments = self._get_json_file_data(datapath+"instruments.json")
        self.intervals = self._get_json_file_data(datapath+"intervals.json")
        self.midi_instruments = self._get_json_file_data(datapath+"midi_instruments.json")
        self.modes = self._get_json_file_data(datapath+"modes.json")
        self.note_lengths = self._get_json_file_data(datapath+"note_lengths.json")
        self.notes = self._get_json_file_data(datapath+"notes.json")
        self.scales = self._get_json_file_data(datapath+"scales.json")
        self.settings_path = datapath+"settings.json" # Used by ChangeSubwindow.
        self.settings = self._get_json_file_data(self.settings_path)
    
    def _get_json_file_data(self, filepath):
        """Returns an ordered dict containing the JSON fiel data.
        
        Arguments:
        >filepath: The JSON file's path
        """
        with open(filepath, encoding='utf-8') as json_file:
            json_data = json.loads(json_file.read(),
                                   object_pairs_hook=collections.OrderedDict)
        return json_data
    
    def create_musicxml(self, filepath, title, clef, mode, instrument,
                        notes):
        """Creates and writes a MusicXML file containing the selected scale sample.
        
        Arguments:
        >filepath: The absolute filepath of the generated MusicXML file.
        >title: The sheet's title.
        >clef: The sheet's clef.
        >mode: The flats/sharps at the beginning of the sheet.
        >instrument: The MIDI instrument of the sheet.
        """
        # "score" includes all MusicXML file elements.
        score = et.Element("score-partwise", version="3.0")
        
        # General score information without notes.
        work = et.SubElement(score, "work")
        et.SubElement(work, "work-title").text = str(title)
       
        score_part = et.SubElement(score, "part-list")
        part_list = et.SubElement(score_part,
                                  "score-part",
                                  id="P1")
        et.SubElement(part_list, "part-name").text = str(instrument)
        
        score_instrument = et.SubElement(part_list,
                                         "score-instrument",
                                         id="P1-I3")
        et.SubElement(score_instrument, "instrument-name").text = str(instrument)
        
        midi_instrument = et.SubElement(part_list,
                                        "midi-instrument",
                                        id="P1-I3")
        et.SubElement(midi_instrument, "midi-channel").text = "1"
        et.SubElement(midi_instrument, "midi-program").text =\
         str(self.midi_instruments[instrument]["midiNumber"])
        et.SubElement(midi_instrument, "volume").text = "100"
        et.SubElement(midi_instrument, "pan").text = "0"
        
        # Score notes.
        part = et.SubElement(score, "part", id="P1")
        measure = et.SubElement(part, "measure", number="1")
        attributes = et.SubElement(measure, "attributes")
        et.SubElement(attributes, "divisions").text =\
         str(self.note_lengths["quarter"]["divisions"])
        key = et.SubElement(attributes, "key")
        mode_data = self.modes[mode]
        et.SubElement(key, "fifths").text = str(mode_data["numberSharps"])
        clef_data = self.clefs[clef]
        clef = et.SubElement(attributes, "clef")
        et.SubElement(clef, "sign").text = str(clef_data["sign"])
        et.SubElement(clef, "line").text = str(clef_data["line"])
        et.SubElement(clef, "clef-octave-change").text = str(clef_data["octave_change"])
        
        max_notes_per_measure = 25 # More than possible for a scale sample
        note_num = 0
        measure_num = 1
        for note_data in notes:
            if (note_num%max_notes_per_measure == 0) and (note_num > 0):
                measure = et.SubElement(part, "measure", number=str(measure_num))
                measure_num += 1
            note = et.SubElement(measure, "note")
            
            if note_data.in_chord:
                et.SubElement(note, "chord")
            pitch = et.SubElement(note, "pitch")
            et.SubElement(pitch, "step").text = str(note_data.name[0])
            if note_data.alter != "":
                et.SubElement(pitch, "alter").text = str(note_data.alter)
            et.SubElement(pitch, "octave").text = str(note_data.octave)
            
            et.SubElement(note, "duration").text = str(self.note_lengths[note_data.duration]["divisions"])
            et.SubElement(note, "type").text = self.note_lengths[note_data.duration]["musicXMLType"]
            if self.note_lengths[note_data.duration]["musicXMLAddition"] != "":
                et.SubElement(note, self.note_lengths[note_data.duration]["musicXMLAddition"])
            
            if note_data.accidental != "":
                et.SubElement(note, "accidental").text = str(note_data.accidental)
            else:
                note_num += 1
        
        # Add XML document type information.
        xml_tree =  '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_tree += '<!DOCTYPE score-partwise PUBLIC '\
                    '"-//Recordare//DTD MusicXML 3.0 Partwise//EN" '\
                    '"http://www.musicxml.org/dtds/partwise.dtd">'
        xml_tree += et.tostring(score, encoding="unicode") #et.ElementTree(score)       
        xml_tree = xml_tree.replace("><", ">\n<")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_tree)
    
    def get_fitting_scales(self, notes_list):
        """Returns scale names whiof scales containing the given notes.
        
        Arguments:
        >notes_list: The given notes.
        """
        notes_cents = [self.notes[i]["centsToC"] for i in notes_list]
        scale_names = []
        for scale_key in list(self.scales.keys()):
            scale_cents = self.scales[scale_key]["notesInCentsToKeynote"]
            
            for keynote_name in list(self.notes.keys()):
                keynote_cents = self.notes[keynote_name]["centsToC"]
                scale_cents_plus_keynote = [(i+keynote_cents)%1200 for i in scale_cents]
                fitting = True
                for note_cents in notes_cents:
                    if note_cents not in scale_cents_plus_keynote:
                        fitting = False
                        break
                if fitting and ("chromatic" not in scale_key):
                    scale_names.append(keynote_name+" - "+scale_key)
        return scale_names
    
    def _get_note_name_from_midi_number(self, midi_number):
        """Returns the note name of the given integer MIDI number.
        
        Quarter tones are not regarded currently.
        
        Arguments:
        >midi_numer: The MIDI number as integer.
        """
        names = list(self.notes.keys()) #["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]
        midi_number *= (len(names)/12)
        return names[(int(midi_number)%len(names))]
    
    def get_scale_sample(self, keynote, name, start_octave, chord=False, randomized=False):
        """Returns a list of Note instances representing a scale or chord sample.
        
        A 'scale' sample contains all notes of the scale in its ascending
        order, folowed by its descending order. The order starts with the
        keynote. The keynote is repeated in its next higher octave at the
        end of the ascending part and the beginning of the descending
        part.
        Example - A 'C major scale' scale sample, starting from octave 4:
        C4, D4, E4, F4, G4, A4, B4, C5, C5, B4, A4, G4, D4, E4, D4, C4
        
        A 'chord' sample conatins all notes of the chord in its ascending
        order. The order starts with the keynote. The ascending order is
        followed by an accord containing all notes of the chord.
        Example - A 'C major chord' chord sample, starting from octave 4,
        with all notes played at the same time written in brackets:
        C4, E4, G4, {C4, E4, G4}
        
        Note that every scale can be returned as a chord sample, and every
        chord as a scale sample, as scales and chords use the same data
        format and the same JSON data file.
        
        Arguments:
        >keynote: The keynote if the sample's scale or chord.
        >name: The name (key from scale JSON data file) of the sample's
               scale or chord.
        >start_octave: The start octave of the returned sample.
        >chord=False: False, if a scale sample shall be returned. True,
                      if a chord sample shall be returned.
        >randomized=False: False, if no randomized score made of the scale
                           shall be returned. True, if it shall be returned.
                           Should not be True if chard is also True.
        """
        keynote_in_cents = self.notes[keynote]["centsToC"]
        scale_in_cents = self.scales[name]["notesInCentsToKeynote"]
        scale_in_cents = [(i + keynote_in_cents)%1200 for i in scale_in_cents]
        scale_in_cents += [keynote_in_cents]
        
        scale_in_names = []
        for cents in scale_in_cents:
            for note in list(self.notes.keys()):
                if self.notes[note]["centsToC"] == cents:
                    scale_in_names.append(note)
                    break
        
        octaves = []
        current_octave = start_octave
        i = 0
        for cents in scale_in_cents:
            if (cents < scale_in_cents[i-1]) and (i > 0):
                current_octave += 1
            octaves.append(current_octave)
            i += 1
        
        if chord:
            scale_in_cents.pop()
            octaves.pop()
        scale_in_cents += scale_in_cents[::-1]
        octaves += octaves[::-1]
        
        scale_in_names = []
        for cents in scale_in_cents:
            for note in list(self.notes.keys()):
                if self.notes[note]["centsToC"] == cents:
                    scale_in_names.append(note)
                    break
        
        notes = []
        i = 0
        while i < len(scale_in_names):
            if chord and (i > len(scale_in_names)/2):
                in_chord = True
            else:
                in_chord = False
            
            notes.append(Note(name=scale_in_names[i][0],
                              octave=octaves[i],
                              alter=self.notes[scale_in_names[i]]["musicXMLAlter"],
                              accidental=self.notes[scale_in_names[i]]["musicXMLAccidental"],
                              type_="quarter",
                              duration="quarter",
                              in_chord=in_chord))
            i += 1
        
        if randomized:
            notes = [random.choice(notes) for _ in range(25)]
            
            # Randomize note lengths.
            note_length_keys = list(self.note_lengths.keys())
            for i in range(len(notes)):
                random_length_key = random.choice(note_length_keys)
                random_length = self.note_lengths[random_length_key]
                notes[i].type_ = random_length["musicXMLType"]
                notes[i].duration = random_length_key
        
        return notes

    def get_sharp_or_flat_number_text(self, mode_name):
        """Returns a text string with the number of flats/sharps of the mode."""
        value = int(self.modes[mode_name]["numberSharps"])
        sharp_or_flat_number_text = ""
        if value < 0:
            sharp_or_flat_number_text = str(value)+" sharps"
        elif value > 0:
            sharp_or_flat_number_text = str(value)+" flats"
        else:
            sharp_or_flat_number_text = "No sharps or flats"
        return sharp_or_flat_number_text
    
    def open_with_sheet_editor(self, filepath):
        """Opens the given file with the sheet editor that was set in the settings file.
        
        Arguments:
        >filepath: The score's file path.
        """
        try:
            subprocess.Popen([self.settings["sheet editor command"],
                              filepath])
        except:
            tkinter.messagebox.showerror("BachBro - Error",
                                         "Scorewriter command not found!\n"\
                                         "Possible solutions:\n"\
                                         ">Set the correct scorewriter command via 'Edit->Set aubio command...'\n"\
                                         ">Install and set up a scorewriter on your system, see INSTALL.txt\n"\
                                         ">Put the scorewriter's binary to your system's PATH\n"\
                                         ">Permit the scorewriter to be executed on your system")
    
    def read_notes_from_wav(self, filepath, disallowed_note_lengths,
                            min_note, min_octave, max_note, max_octave,
                            error_threshold):
        """Using aubio, a list of Note instances is returned from the given file.
        
        Arguments:
        >filepath: The .wav file's path.
        >disallowed_note_lengths: Note lengths that shall not be interpreted.
                                  If aubio finds a disallowed note length,
                                  the nearest allowed note length is returned.
        >min_note: The name of the lowest allowed note.
        >min_octave: The octave of the lowest allowed note. If aubio finds
                     this note or a note below of it, the note will be
                     ignored.
        >max_note: The name of the highest allowed note.
        >max_octave: The octave of the highest allowed note
        >error_threshold: If aubio detects a lower error probability than
                          given (as a string), the recognized note will
                          be ignored by aubio.
        """
        notes = []

        # Create allowed note lengths dictionary.
        allowed_lengths = collections.OrderedDict()
        i = 0
        for key in list(self.note_lengths.keys()):
            if i not in disallowed_note_lengths:
                allowed_lengths[key] = self.note_lengths[key]
            i += 1
        
        # Execute the aubio command.
        command = [self.settings["aubio command"],
                   "-i", filepath,
                   "-l", error_threshold]
        try:
            out = subprocess.check_output(command,
                                          universal_newlines=True)
        except:
            tkinter.messagebox.showerror("BachBro - Error",
                                         "aubionotes command not found!\n"\
                                         "Possible solutions:\n"\
                                         ">Set the correct aubionotes command via 'Edit->Set aubio command...'\n"\
                                         ">Install and set up aubio on your system, see BachBro's INSTALL.txt\n"\
                                         ">Put aubionotes binary to your system's PATH\n"\
                                         ">Permit aubionotes to be executed on your system")
            return False
        
        # Create temporary MidiNpte instances as aubio returns notes
        # as midi numbers.
        midi_notes = []
        out = out.split("\n")
        for line in out:
            line = line.split("\t")
            if len(line) == 3:
                midi_note = MidiNote(midi_number=line[0],
                                     start=line[1], end=line[2])
                midi_notes.append(midi_note)
       
        # Get eligible note lengths.
        eligible_keys = []
        for key in list(allowed_lengths.keys()):
            eligible_keys.append(self.note_lengths[key]["divisions"])
        min_key = min(eligible_keys)
       
        # Create final Note instances.
        notes = []
        try:
            minimal_midi_length = min([i.length for i in midi_notes])
        except Exception:
            return False
        
        for midi_note in midi_notes:
            # Get best note length
            ratio = midi_note.length / minimal_midi_length
            min_difference = min([abs(ratio-i/min_key) for i in eligible_keys])
            
            # Create note data
            duration = [i for i in list(allowed_lengths.keys())
                        if abs(ratio-(self.note_lengths[i]["divisions"])/min_key) == min_difference][0]
            type_ = allowed_lengths[duration]
            name = self._get_note_name_from_midi_number(midi_note.midi_number)
            octave = midi_note.midi_number//12 - 1
            
            
            # Maximum check
            if (octave > max_octave) or\
               (octave == max_octave and\
                self.notes[name]["centsToC"] >\
                self.notes[name]["centsToC"]):
                octave = max_octave
                name = max_note

            # Minimum check
            if not ((octave < min_octave) or\
                    (octave == min_octave and\
                     self.notes[name]["centsToC"] < \
                     self.notes[name]["centsToC"])):
                notes.append(Note(name=name, octave=octave,
                                  alter=self.notes[name]["musicXMLAlter"],
                                  accidental=self.notes[name]["musicXMLAccidental"],
                                  type_=type_, duration=duration))
        return notes
