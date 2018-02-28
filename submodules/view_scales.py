#!/usr/bin/env python
#
# view_scales.py
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

"""view_scales.py - View notes of a selected scale.

The scale can be viewed on a piano as well as on a user selected instrument.
In the user selected instrument view, the user may click on a note and
show a range of user selected intervals.
"""

import copy
import math
import os
import tkinter
import tkinter.scrolledtext


class ViewScales(tkinter.Frame):
    """Main class for 'View Scales/Chords'."""
    def __init__(self, parent):
        """All widgets are set here.
        
        Arguments:
        >parent: The BachBroData instance for an instance of
                 this class.
        """
        super().__init__()
        self.parent = parent
        self.clicked_relcents = []
        
        # Rest
        frame_keynote = tkinter.Frame(self)
        frame_keynote.pack()
        label_keynote = tkinter.Label(frame_keynote, text="Keynote:")
        label_keynote.pack(side="left")
        self.var_keynote = tkinter.StringVar()
        all_note_names = list(self.parent.data.notes.keys())
        self.var_keynote.set(all_note_names[0])
        keynote = tkinter.ttk.Combobox(frame_keynote, width=40,
                                       textvariable=self.var_keynote)
        keynote.bind('<<ComboboxSelected>>', self._color_keys)
        keynote["values"] = all_note_names
        keynote.pack(side="left")
        
        frame_scale = tkinter.Frame(self)
        frame_scale.pack()
        label_scale = tkinter.Label(frame_scale, text="Scale:")
        label_scale.pack(side="left")
        self.var_scale = tkinter.StringVar()
        self.var_scale.set(list(self.parent.data.scales.keys())[0])
        scale = tkinter.ttk.Combobox(frame_scale, width=50,
                                     textvariable=self.var_scale)
        scale.bind('<<ComboboxSelected>>', self._color_keys)
        scale["values"] = list(self.parent.data.scales.keys())
        scale.pack(side="left")
        
        frame_information = tkinter.Frame(self)
        
        frame_genre_sources = tkinter.Frame(frame_information) 
        label_genre_sources = tkinter.Label(frame_genre_sources,
                                            text="Genre data sources:")
        self.text_genre_sources = tkinter.scrolledtext.ScrolledText(
                                   frame_genre_sources,
                                   width=30,
                                   height=5)
        frame_genre_sources.pack(side="left")
        label_genre_sources.pack()
        self.text_genre_sources.pack()
        
        frame_scale_info = tkinter.Frame(frame_information) 
        label_scale_info = tkinter.Label(frame_scale_info,
                                            text="Scale information:")
        self.text_scale_info = tkinter.scrolledtext.ScrolledText(
                                   frame_scale_info,
                                   width=30,
                                   height=5)
        frame_scale_info.pack(side="left")
        label_scale_info.pack()
        self.text_scale_info.pack()
        
        frame_scale_sources = tkinter.Frame(frame_information) 
        label_scale_sources = tkinter.Label(frame_scale_sources,
                                            text="Scale data sources:")
        self.text_scale_sources = tkinter.scrolledtext.ScrolledText(
                                   frame_scale_sources,
                                   width=30,
                                   height=5)
        frame_scale_sources.pack(side="left")
        label_scale_sources.pack()
        self.text_scale_sources.pack()
        
        frame_same_intervals = tkinter.Frame(frame_information)
        label_list = tkinter.Label(frame_same_intervals,
                                   text="Scales with identical interval structure:")
        list_frame = tkinter.Frame(frame_same_intervals)
        scrollbar = tkinter.Scrollbar(list_frame, orient="vertical")
        self.list_identical = tkinter.Listbox(list_frame, height=5,
                                           width=40,
                                           yscrollcommand=\
                                            scrollbar.set)
        self.list_identical.pack(side="left")
        self.list_identical.bind("<Double 1>", self._view_identical_scale)
        scrollbar["command"] = self.list_identical.yview
        scrollbar.pack(side="left",fill="y")
        frame_same_intervals.pack(side="left")
        label_list.pack()
        list_frame.pack()
        
        # Piano and user selected instrument view.
        label_piano = tkinter.Label(self, text="Piano/Selected instrument view:")
        
        frame_view_options = tkinter.Frame(self)
        
        self.var_highlight_keynote = tkinter.BooleanVar()
        self.var_highlight_keynote.set(True)
        highlight_key = tkinter.Checkbutton(frame_view_options,
                                            text="Highlight keynote "
                                                 "in yellow",
                                            variable=\
                                             self.var_highlight_keynote,
                                            command=self._color_keys)
        button_quarter_up = tkinter.Button(frame_view_options,
                                           text="Rise note selection by quarter tone",
                                           command=self._add_quarter_tone_to_selection)
        button_quarter_down = tkinter.Button(frame_view_options,
                                             text="Lower note selection by quarter tone",
                                             command=self._substract_quarter_tone_to_selection)
        
        frame_instruments = tkinter.Frame(self)
        
        # Piano keys
        piano_width = 500
        piano_height = 175
        self.piano_canvas = tkinter.Canvas(frame_instruments,
                                           width=piano_width,
                                           height=piano_height)
        
        # White piano keys
        self.white_keys = []
        for i in range(7):
            key = self.piano_canvas.create_rectangle(i*(piano_width/7)+2, 2,
                                          (i+1)*(piano_width/7),
                                          piano_height,
                                          fill="white",
                                          outline="black", width=2)
            self.white_keys.append(key)
        
        # Black piano keys
        self.black_keys = []
        for i in range(5):
            left_x = (i)*(piano_width/7)+(3*piano_width/28)
            
            if i > 1:
                left_x += (piano_width/7)
            
            key = self.piano_canvas.create_rectangle(left_x, 2,
                                               left_x+(piano_width/14),
                                               piano_height*.65,
                                               fill="black",
                                               outline="black",
                                               width=3)
            self.black_keys.append(key)
        
        frame_text = tkinter.Frame(self)
        label_text = tkinter.Label(frame_text, text="Notes in scale:")
        self.text_field = tkinter.Text(frame_text, width=80, height=0)
        
        button_find_note_same = tkinter.Button(frame_text,
                                               text="Find scales with same notes",
                                               command=\
                                                self._find_scales_including_same_notes)
        
        # Genre selection. 
        frame_genre =  tkinter.Frame(self)
        label_genre = tkinter.Label(frame_genre,
                                    text="Genre (for preselected interval types; intervals in cents): ")
        self.var_genre = tkinter.StringVar()
        self.var_genre.set(list(self.parent.data.genres.keys())[0])
        genre = tkinter.ttk.Combobox(frame_genre,
                                     width=25,
                                     textvariable=self.var_genre)
        genre.bind('<<ComboboxSelected>>', self._set_intervals)
        genre["values"] = list(self.parent.data.genres.keys())
        
        self.var_strong_dissonant = tkinter.BooleanVar()
        self.var_strong_dissonant.set(False)
        cb_strong_dissonant = tkinter.Checkbutton(frame_genre,
                                                  text="Strong dissonant",
                                                  variable=self.var_strong_dissonant,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  command=self._set_intervals)
        
        self.var_weak_dissonant = tkinter.BooleanVar()
        self.var_weak_dissonant.set(False)
        cb_weak_dissonant = tkinter.Checkbutton(frame_genre,
                                                text="Weak dissonant",
                                                variable=self.var_weak_dissonant,
                                                onvalue=True,
                                                offvalue=False,
                                                command=self._set_intervals)
        
        self.var_weak_consonant = tkinter.BooleanVar()
        self.var_weak_consonant.set(True)
        cb_weak_consonant = tkinter.Checkbutton(frame_genre,
                                                text="Weak consonant",
                                                variable=self.var_weak_consonant,
                                                onvalue=True,
                                                offvalue=False,
                                                command=self._set_intervals)
        
        self.var_strong_consonant = tkinter.BooleanVar()  
        self.var_strong_consonant.set(True)
        cb_strong_consonant = tkinter.Checkbutton(frame_genre,
                                                  text="Strong consonant",
                                                  variable=self.var_strong_consonant,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  command=self._set_intervals)
        
        self.button_rhythm_file = tkinter.Button(frame_genre,
                                                 text="Open genre rhythms file",
                                                 command=self._open_rhythms_file)
        
        label_genre.pack(side="left")
        genre.pack(side="left")
        cb_strong_dissonant.pack(side="left")
        cb_weak_dissonant.pack(side="left")
        cb_weak_consonant.pack(side="left")
        cb_strong_consonant.pack(side="left")
        self.button_rhythm_file.pack(side="left")
        
        # Interval checkbuttons.
        frame_intervals = tkinter.Frame(self)
        interval_names = list(self.parent.data.intervals.keys())
        self.chosen_intervals = []
        for i in range(len(interval_names)):
            var = tkinter.BooleanVar()
            var.set(False)
            
            text = self.parent.data.intervals[interval_names[i]]["cents"]
            cb = tkinter.Checkbutton(frame_intervals,
                                     text=str(text),
                                     variable=var,
                                     onvalue=True,
                                     offvalue=False,
                                     command=self._click_on_canvas)
            cb.pack(side="left")
            self.chosen_intervals.append(var)
        
        # Other instrument canvas variables.
        instrument_width = 500
        instrument_height = 175
        self.instrument_canvas = tkinter.Canvas(frame_instruments,
                                                width=instrument_width,
                                                height=instrument_height)
        self.instrument_canvas.bind("<ButtonRelease-1>",
                                    self._click_on_canvas)
        
        # Packaging.
        label_text.pack(side="left")
        self.text_field.pack(side="left")
        button_find_note_same.pack(side="left")
        
        frame_text.pack()
        frame_genre.pack()
        frame_intervals.pack()
        
        label_piano.pack()
        frame_view_options.pack()
        highlight_key.pack(side="left")
        button_quarter_up.pack(side="left")
        button_quarter_down.pack(side="left")
        
        frame_instruments.pack()
        self.piano_canvas.pack(side="left")
        self._make_instrument_canvas()
        self.instrument_canvas.pack(side="right")
        
        frame_sample = tkinter.Frame(self)
        label_octave = tkinter.Label(frame_sample, text="Sample "
                                                        "start octave:")
        self.var_start_octave = tkinter.IntVar()
        self.var_start_octave.set(4)
        start_octave = tkinter.ttk.Combobox(frame_sample, width=3,
                                            textvariable=\
                                             self.var_start_octave)
        start_octave["values"] = [2,3,4,5,6]
        label_octave.pack(side="left")
        start_octave.pack(side="left")
        
        button_show_scale_sample = tkinter.Button(frame_sample,
                                           text="Create & Open MusicXML as scale",
                                           command=\
                                            self._show_scale_sample)
        button_show_scale_sample.pack(side="left")
        button_show_chord_sample = tkinter.Button(frame_sample,
                                           text="...as chord",
                                           command=\
                                            self._show_chord_sample)
        button_show_chord_sample.pack(side="left")
        
        button_show_randomized_sample = tkinter.Button(frame_sample,
                                                       text="...as randomized sample",
                                                       command=\
                                                        self._show_randomized_sample)
        button_show_randomized_sample.pack(side="left")
        frame_sample.pack()
        
        frame_information.pack()
        self._set_intervals()
    
    def _add_quarter_tone_to_selection(self, *e):
        """Adds a quarter tone to all selected notes and reloads the canvas."""
        self.clicked_relcents = [i+50 for i in self.clicked_relcents]
        self._color_keys()
    
    def _get_chosen_intervals(self):
        """Returns a list (in cents to next lower C) of user selected intervals."""
        chosen_intervals = []
        i = 0
        for checkbutton in self.chosen_intervals:
            if checkbutton.get():
                key = list(self.parent.data.intervals.keys())[i]
                chosen_intervals.append(self.parent.data.intervals[key]["cents"])
            i += 1
        return chosen_intervals
    
    def _click_on_canvas(self, *e):
        """Fires, if the use clicks on the instrument canvas.
        
        If the user clicks into a rectangle which represents a non-chosen
        tone, the rectangles representing the tone (based on relative cents
        to the next lower C) will be selected. If the note was already chosen, the
        rectangles will be unselected.
        """
        for event in e:
            x = math.floor(event.x/self.cell_width)
            y = math.floor(event.y/self.cell_height)
            
            instrument =\
                self.parent.data.instruments[self.parent.var_instrument.get()]
            instrument_relcents = self._get_relcents_of_instrument(instrument)
            
            try:
                clicked_relcents = instrument_relcents[y][x]
            except:
                return
            
            if clicked_relcents in self.clicked_relcents:
                self.clicked_relcents = [i for i in self.clicked_relcents
                                         if i != clicked_relcents]
            else:
                self.clicked_relcents.append(clicked_relcents)
        self._color_keys()
    
    def _color_keys(self, *e):
        """Colors insturment canvas keys according to the scale and user input."""
        # Reset list of scales with identical interval structure.
        self.list_identical.delete("0", "end")
        
        # Get keynote.
        keynote_name = self.var_keynote.get()
        keynote_in_cents = self.parent.data.notes[keynote_name]["centsToC"]
        
        # Get scale in cents to next lower C.
        scale = self.parent.data.scales[self.var_scale.get()]
        scale_in_cents = self.parent.data.scales[self.var_scale.get()]["notesInCentsToKeynote"]
        scale_in_cents = [(i + keynote_in_cents)%1200 for i in scale_in_cents]
        
        # Set information frame data texts.
        self.text_scale_info.delete("0.0", "end")
        for info in scale["info"]:
            self.text_scale_info.insert("end", "· "+info+"\n")
        
        self.text_scale_sources.delete("0.0", "end")
        for source in scale["sources"]:
            self.text_scale_sources.insert("end", "· "+source+"\n")
        
        # Get notes from cent values
        scale_note_names = []
        for i in range(len(scale_in_cents)):
            for note in list(self.parent.data.notes.keys()):
                if self.parent.data.notes[note]["centsToC"] == scale_in_cents[i]:
                    scale_note_names.append(note)
                    break
        
        # Find identical scales (adjusted to C as keynote).
        adjusted_scale_in_cents = scale_in_cents
        for scale_key in list(self.parent.data.scales.keys()):
            if scale_key != self.var_scale.get():
                other_scale = copy.deepcopy(self.parent.data.scales[scale_key])
                other_scale["notesInCentsToKeynote"] = [(i + keynote_in_cents)%1200
                                                        for i in other_scale["notesInCentsToKeynote"]]
                if other_scale["notesInCentsToKeynote"] == adjusted_scale_in_cents:
                    self.list_identical.insert("end", scale_key)
        
        self.text_field.delete("1.0", "end")
        self.text_field.insert("end", scale_note_names)
        self.scale_note_names = scale_note_names
        
        # Add cents to C of the white and the black piano keys.
        white_values = []
        white_values.append([0])
        white_values.append([200])
        white_values.append([400])
        white_values.append([500])
        white_values.append([700])
        white_values.append([900])
        white_values.append([1100])
        black_values = []
        black_values.append([100])
        black_values.append([300])
        black_values.append([600])
        black_values.append([800])
        black_values.append([1000])
        
        # Creates a list of booleans showing if the tones represented by the
        # black and white piano keys are included in the currently selected
        # scale.
        for white_value in white_values:
            white_value.append(white_value[0] in scale_in_cents)
        for black_value in black_values:
            black_value.append(black_value[0] in scale_in_cents)
        
        # Color keys if they include selected notes.
        keynote_color = "yellow"
        in_scale_color = "cornflower blue"
        for i in range(len(white_values)):
            if white_values[i][0] == keynote_in_cents:
                if self.var_highlight_keynote.get():
                    color = keynote_color
                else:
                    color = in_scale_color
            elif white_values[i][1]:
                color = in_scale_color
            else:
                color = "white"
            self.piano_canvas.itemconfig(self.white_keys[i], fill=color)
        for i in range(len(black_values)):
            if black_values[i][0] == keynote_in_cents:
                if self.var_highlight_keynote.get():
                    color = keynote_color
                else:
                    color = in_scale_color
            elif black_values[i][1]:
                color = in_scale_color
            else:
                color = "black"
            self.piano_canvas.itemconfig(self.black_keys[i], fill=color)
        
        # Instrument canvas coloring.
        instrument =\
         self.parent.data.instruments[self.parent.var_instrument.get()]
        instrument_relcents = self._get_relcents_of_instrument(instrument)
        
        # Determine fitting intervals.
        chosen_intervals = self._get_chosen_intervals()
        
        flat_instrument_relcents = []
        for string_relcents in instrument_relcents:
            flat_instrument_relcents += string_relcents
        
        if len(chosen_intervals) > 0:  
            i = 0
            while len(chosen_intervals) < len(flat_instrument_relcents):
                temp_chosen_intervals = []
                temp_chosen_intervals += [(i*1200)+j for j in chosen_intervals]
                chosen_intervals += temp_chosen_intervals
                i += 1
            chosen_intervals = list(set(chosen_intervals))
        
        # All fitting cents to the next lower C for intervals.
        fitting_relcents_per_cell = []
        for clicked_relcent in self.clicked_relcents:
            fitting_cell_relcents = []
            for chosen_interval in chosen_intervals:
                fitting_cell_relcents.append(clicked_relcent+chosen_interval)
                fitting_cell_relcents.append(clicked_relcent-chosen_interval)
            fitting_relcents_per_cell.append(fitting_cell_relcents)
        
        # Get intersection of fitting cents to next lower C.
        if len(fitting_relcents_per_cell) > 1:
            fitting_interval_relcents = set(fitting_relcents_per_cell[0])
            for fitting_relcents in fitting_relcents_per_cell[1:]:
                fitting_interval_relcents = fitting_interval_relcents & set(fitting_relcents)
            fitting_interval_relcents = list(fitting_interval_relcents)
        elif len(fitting_relcents_per_cell) == 1:
            fitting_interval_relcents = list(fitting_relcents_per_cell[0])
        else:
            fitting_interval_relcents = []
        
        # Color cells appropriately.
        void_color = "white"
        clicked_color = "red"
        fitting_interval_and_in_scale_color = "orange"
        for i in range(len(self.stringed_notes)):
            for j in range(len(self.stringed_notes[i])):
                color = void_color
                cell_cents_in_octave = instrument_relcents[i][j] % 1200
                if cell_cents_in_octave in scale_in_cents:
                    color = in_scale_color
                if cell_cents_in_octave == keynote_in_cents:
                    if self.var_highlight_keynote.get():
                        color = keynote_color
                if instrument_relcents[i][j] in fitting_interval_relcents:
                    if instrument_relcents[i][j]%1200 in scale_in_cents:
                        color = fitting_interval_and_in_scale_color
                if instrument_relcents[i][j] in self.clicked_relcents:
                    color = clicked_color
                
                self.instrument_canvas.itemconfig(self.stringed_notes[i][j],
                                                  fill=color)
    
    def _find_scales_including_same_notes(self, *e):
        """Opens the 'Find Scales/Chords' tab with the selected scale's notes."""
        checkbutton_vars = self.parent.tab_find_scales.checkbutton_vars
        for key in list(checkbutton_vars.keys()):
            if key in self.scale_note_names:
                checkbutton_vars[key].set(1)
            else:
                checkbutton_vars[key].set(0)
        
        self.parent.notebook.select(2)
        self.parent.tab_find_scales._find_scales()
    
    def _get_genre_intervals_in_cents(self, genre_name, category):
        """Returns a list of intervals (in cents) of the genre.
        
        Arguments:
        >genre_name: Name of genre.
        >category: Type of searches intervals (dissonant, co
        """
        interval_names = self.parent.data.genres[genre_name][category]
        for name in interval_names:
            yield self.parent.data.intervals[name]["cents"]
    
    def _get_relcents_of_instrument(self, instrument):
        """Returns a list of lists representing the instrument's tones.
        
        Each sublist represents an instrument string. Each number in a
        sublist shows the relative cents to the next lower C of the tone of
        the string at the given position.
        
        Example:
        An instrument with two strings of the following tones...
        C C# D D#
        D D# E F
        ...results in the following list of lists:
        [[0,   100, 200, 300],
         [100, 200, 300, 400]]
        """
        string_range = int(instrument["stringRangeInCents"])
        fret_distance = int(instrument["fretDistanceInCents"])
        num_frets = string_range // fret_distance
        
        relcents = []
        for string in instrument["stringStartNotes"]:
            temp_string = []
            start_cent = int(string[1])*1200 + self.parent.data.notes[string[0]]["centsToC"]
            for fret_num in range(num_frets):
                temp_string.append(start_cent + fret_num * fret_distance)
            relcents.append(temp_string)
        return relcents
    
    def _make_instrument_canvas(self, *e):
        """Draws elements of the instrument (not the piano) canvas.
        
        The canvas gets its instrument data from a JSON file describing
        the instrument.
        """
        # Get instrument size.
        instrument_width = int(self.instrument_canvas["width"])
        instrument_height = int(self.instrument_canvas["height"])
        self.piano_canvas_width, self.piano_canvas_height = instrument_width, instrument_height
        self.instrument_canvas.delete("all")
        self.stringed_notes = []
        instrument =\
         self.parent.data.instruments[self.parent.var_instrument.get()]
        
        # Get instrument and resulting canvas rectangle sizes.
        num_strings = len(instrument["stringStartNotes"])
        string_range = int(instrument["stringRangeInCents"])
        fret_distance = int(instrument["fretDistanceInCents"])
        num_frets = string_range // fret_distance
        self.cell_height = instrument_height/num_strings
        self.cell_width = instrument_width/num_frets
        
        # Draw white rectangles with black edges.
        for string in range(num_strings):
            temp_string = []
            for note in range(num_frets):
                x0 = note*self.cell_width+2
                y0 = string*self.cell_height+2
                x1 = x0+self.cell_width
                y1 = y0+self.cell_height
                key = self.instrument_canvas.create_rectangle(x0, y0,
                                                              x1, y1,
                                                              fill="white",
                                                              outline="black",
                                                              width=2)
                self.instrument_canvas.create_text((x0+x1)/2,
                                                   (y0+y1)/2,
                                                   text=instrument["labels"][string][note])
                temp_string.append(key)
            self.stringed_notes.append(temp_string)
        
        self._color_keys()
    
    def _open_rhythms_file(self, *e):
        """Opens (if given) a MusicXML file containing rhythms of the selected genre."""
        genre_name = self.var_genre.get()
        genre = self.parent.data.genres[genre_name]
        rhythm_file = genre["rhythmFile"]
        
        if rhythm_file != "":
            filepath = os.getcwd().replace("\\", "/")+"/data/"+rhythm_file
            self.parent.data.open_with_sheet_editor(filepath)
    
    def _set_intervals(self, *e):
        """Sets intervals of selected genre. Can be changed by the user later."""
        genre_name = self.var_genre.get()
        genre = self.parent.data.genres[genre_name]
        
        # Grey out rhythm files button if no rhythms file is set.
        if genre["rhythmFile"] == "":
            self.button_rhythm_file["state"] = "disabled"
        else:
            self.button_rhythm_file["state"] = "active"
        
        # Set information frame data.
        self.text_genre_sources.delete("0.0", "end")
        for source in genre["sources"]:
            self.text_genre_sources.insert("end", "· "+source+"\n")
        
        # Get genre intervals in cents.
        genre_intervals = []
        if self.var_strong_dissonant.get():
            genre_intervals += self._get_genre_intervals_in_cents(genre_name,
                                                                  "strongDissonantIntervals")
        if self.var_weak_dissonant.get():
            genre_intervals += self._get_genre_intervals_in_cents(genre_name,
                                                                  "weakDissonantIntervals")
        if self.var_weak_consonant.get():
            genre_intervals += self._get_genre_intervals_in_cents(genre_name,
                                                                  "weakConsonantIntervals")
        if self.var_strong_consonant.get():
            genre_intervals += self._get_genre_intervals_in_cents(genre_name,
                                                                  "strongConsonantIntervals")
        
        # Go through each checkbutton.
        i = 0
        for checkbutton in self.chosen_intervals:
            key = list(self.parent.data.intervals.keys())[i]
            cents = self.parent.data.intervals[key]["cents"]
            if cents in genre_intervals:
                checkbutton.set(True)
            else:
                checkbutton.set(False)
            i += 1
        
        # Redraw rectangle colors.
        self._color_keys()
    
    def _show_chord_sample(self, *e):
        """Creates and opens a MusicXML file with the selected scale as chord."""
        self._show_scale_sample(chord=True)
    
    def _show_randomized_sample(self, *e):
        """Creates and opens a MusicXML file with the selected scale as a randomized sample."""
        self._show_scale_sample(randomized=True)
    
    def _show_scale_sample(self, chord=False, randomized=False):
        """Creates and opens MusicXML file which shows the selected scale.
        
        The user defined sheet editor is opened to show the MusicXML. There
        are three ways to show a scale:
         1) As a chord: All notes of the scale are played in
            ascending order first, and then played at one time as a chord.  
         2) As a scale wave: All notes of the scale are played in
            ascending order first, and then in descending order.
         3) As a randomized sample: 50 notes in this scales are shown in a random
                                    order and with different note lengths.
        
        Arguments:
        >chord=False: True, if the scale shall be shown as a chord. False, if
                      if the scale shall be shown as a scale wave.
        >random=False: True, if a random sample of the notes shall be shown.
        """
        notes = self.parent.data.get_scale_sample(keynote=\
                                                   self.var_keynote.get(),
                                                  name=self.var_scale.get(),
                                                  start_octave=\
                                                   self.var_start_octave.get(),
                                                  chord=chord,
                                                  randomized=randomized)
        
        title = self.var_keynote.get()+"-"+self.var_scale.get()
        filepath = os.getcwd().replace("\\", "/")+"/data/temp/MA"+\
                   str(self.parent.current_file_number)+".xml"
        mode = self.parent.var_mode.get().split(" (")[0]
        self.parent.data.create_musicxml(filepath,
                                         title, self.parent.var_clef.get(),
                                         mode,
                                         self.parent.var_midi_instrument.get(),
                                         notes)
        self.parent.current_file_number += 1
        self.parent.data.open_with_sheet_editor(filepath)
    
    def _random(self, *e):
        notes = self.parent.data.get_scale_sample(keynote=\
                                                   self.var_keynote.get(),
                                                  name=self.var_scale.get(),
                                                  start_octave=\
                                                   self.var_start_octave.get(),
                                                  chord=chord)
    
    def _substract_quarter_tone_to_selection(self, *e):
        """Substracts a quarter tone to all selected notes and reloads the canvas."""
        self.clicked_relcents = [i-50 for i in self.clicked_relcents]
        self._color_keys()
    
    def _view_identical_scale(self, *e):
        """Switches scale selection to a scale with the same notes.
        
        Is fired if the user double clicks at the selected identical scale
        in the identical scales list widget.
        Only exactly identical scales are shown in this widget.
        """
        curselections = self.list_identical.curselection()
        if len(curselections) == 0:
            return
        index = curselections[0]
        key = self.list_identical.get(index)
        self.var_scale.set(key)
        self._color_keys()
