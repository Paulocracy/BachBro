#!/usr/bin/env python
#
# find_scales.py
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

"""find_scales.py - Finding of music scales by selecting notes.

All scales which include the selected notes will be shown in a list.
"""

import copy
import collections
import tkinter


class FindScales(tkinter.Frame):
    """Frame and methods for finding scales by selecting included notes."""
    def __init__(self, parent):
        """All widgets are set here."""
        super().__init__()
        self.parent = parent  # For communication with other widgets and data.
        
        label_frame = tkinter.Frame(self)
        label_frame.pack()
        label_piano = tkinter.Label(label_frame, text="Notes included in "
                                                      "scale:")
        label_piano.pack(side="left")

        button_mark_all = tkinter.Button(label_frame, text="Mark all",
                                         command=self._mark_all)
        button_mark_all.pack(side="left")

        button_reset = tkinter.Button(label_frame, text="Reset",
                                      command=self._reset)
        button_reset.pack(side="left")

        tones_frame = tkinter.Frame(self)
        tones_frame.pack()

        self.checkbutton_vars = collections.OrderedDict()
        for tone in list(self.parent.data.notes.keys()):
            self.checkbutton_vars[tone] = tkinter.BooleanVar()
            self.checkbutton_vars[tone].set(0)
            checkbutton = tkinter.Checkbutton(tones_frame,
                                              text=tone,
                                              variable=\
                                               self.checkbutton_vars[tone],
                                              onvalue=True,
                                              offvalue=False,
                                              font="Courier 10",
                                              command=self._find_scales)
            checkbutton.pack(side="left")
 
        label_stringed = tkinter.Label(self, text="Notes in string "
                                                  "instrument order:")
        label_stringed.pack()
        self.stringed_frame = tkinter.Frame(self)
        self.stringed_frames = []
        self._make_instrument_checkboxes()
        self.stringed_frame.pack()
        
        label_list = tkinter.Label(self, text="Scales including selected notes "
                                              "(double click on a scale"
                                              " in list to view it):")
        label_list.pack()
        list_frame = tkinter.Frame(self)
        scrollbar = tkinter.Scrollbar(list_frame, orient="vertical")
        self.list_result = tkinter.Listbox(list_frame, height=9,
                                           width=80,
                                           yscrollcommand=
                                           scrollbar.set)
        self.list_result.pack(side="left")
        self.list_result.bind("<Double 1>", self._view_selected_scale)
        scrollbar["command"] = self.list_result.yview
        scrollbar.pack(side="left", fill="y")
        list_frame.pack()

    def _find_scales(self, *e):
        """Main function. Finds all fitting scales.
        
        A scale is 'fitting', if it contains the user selected notes or
        a subset of it.
        """
        is_note_clicked = [self.checkbutton_vars[i].get()
                           for i in list(self.checkbutton_vars.keys())]
        all_note_names = list(self.parent.data.notes.keys())
        note_list = []
        i = 0
        for clicked in is_note_clicked:
            if clicked:
                note_list.append(all_note_names[i])
            i += 1
        self.fitting_scales = self.parent.data.get_fitting_scales(note_list)

        self.list_result.delete("0", "end")
        num_all_scales = len(list(self.parent.data.scales.keys()))
        num_all_scales *= len(all_note_names)
        if len(self.fitting_scales) != num_all_scales:
            for fitting_scale in self.fitting_scales:
                self.list_result.insert("end", fitting_scale)

    def _get_keynote_scale(self, keynote_addend, scale_list):
        """Returns the scale list ordered to the keynote.
        
        Arguments:
        >keynote_addend: The order number of the keynote in the scale.
        >scale_list: The list of the scale's notes.
        """
        scale_list = scale_list[len(scale_list) -
                                keynote_addend:len(scale_list)] + \
                     scale_list[0:len(scale_list)-keynote_addend]
        return scale_list

    def _get_note_names_of_instrument(self, instrument):
        """Returns a list of string lists containing the intrument's notes in order."""
        string_range = int(instrument["stringRangeInCents"])
        fret_distance = int(instrument["fretDistanceInCents"])
        num_frets = string_range // fret_distance
        
        note_names = []
        for string in instrument["stringStartNotes"]:
            temp_string = []
            start_cent = int(string[1])*1200 + self.parent.data.notes[string[0]]["centsToC"]
            for fret_num in range(num_frets):
                cents = start_cent + fret_num * fret_distance
                for note_key in list(self.parent.data.notes.keys()):
                    if (cents % 1200) == self.parent.data.notes[note_key]["centsToC"]:
                        temp_string.append(note_key)
                        break
            note_names.append(temp_string)
        return note_names

    def _mark_all(self, *e):
        """Selects all note selection setboxes."""
        self._set_all_checkbuttons(True)

    def _make_instrument_checkboxes(self, *e):
        """Creates the user selected instrument note checkboxes in the instrument's order."""
        if len(self.stringed_frames) > 0:
            for i in self.stringed_frames:
                i.destroy()
            del(self.stringed_frames)
            self.stringed_frames = []

        instrument =\
         self.parent.data.instruments[self.parent.var_instrument.get()]
        self.stringed_frames = [tkinter.Frame(self.stringed_frame)
                                for i in range(len(instrument["stringStartNotes"]))]
        
        string_range = int(instrument["stringRangeInCents"])
        fret_distance = int(instrument["fretDistanceInCents"])
        num_frets = string_range // fret_distance
        
        instrument_note_names = self._get_note_names_of_instrument(instrument)
        for y in range(len(instrument["stringStartNotes"])):
            for x in range(num_frets):
                tone = instrument_note_names[y][x]
                variable = self.checkbutton_vars[tone]
                if len(tone) < 2:
                    tone += " "
                if len(tone) < 3:
                    tone += " "
                checkbutton = tkinter.Checkbutton(self.stringed_frames[y],
                                                  text=tone,
                                                  variable=variable,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  font="Courier 10",
                                                  command=self._find_scales)
                checkbutton.pack(side="left")
            self.stringed_frames[y].pack()

    def _reset(self, *e):
        """Unselects all note selection setboxes."""
        self._set_all_checkbuttons(False)

    def _set_all_checkbuttons(self, value):
        """Switches all note checkboxes to the given value.
        
        Arguments:
        >value: The given value. It should be a boolean.
        """
        for variable_name in list(self.checkbutton_vars.keys()):
            self.checkbutton_vars[variable_name].set(value)
        self._find_scales()

    def _view_selected_scale(self, *e):
        """If the user double clicks on a scale in the fitting scales, the scale is shown.
        
        It is done by switching to the 'View Scales/Chords' tab and the
        selection of the user selected scale.
        """
        curselection = self.list_result.curselection()[0]
        selected_scale = self.fitting_scales[curselection]
        selected_scale = selected_scale.split(" - ")
        keynote = selected_scale[0]
        scale = selected_scale[1]
            
        self.parent.notebook.select(0)
        self.parent.tab_view_scales.var_keynote.set(keynote)
        self.parent.tab_view_scales.var_scale.set(scale)
        self.parent.tab_view_scales._color_keys()
