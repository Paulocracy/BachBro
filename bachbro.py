#!/usr/bin/env python
#
# bachbro.py
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

"""bachbro.py - Main module.

BachBro provides some functions for music researches which lack
in many common music programs. Read the README for more information about
BachBro's functions.

Soure code structure:
BachBro is written in Python 3, and uses tkinter as its GUI
toolkit, pyaudio for microphone functions, and aubio for note recognition.
 The music theory data used by BachBro is composed from external
music theory publications. Together with the sources, this data is provided
in JSON files in BachBro's "docs" subfolder.
 The main class is BachBro, written in this module. All GUI tabs
are written in separate submodules. All GUI-independent methods (such as
the JSON data loading; only tkinter error messages are included) are written
in the submodule bachbro_data.
"""

import os
import sys
import tkinter
import tkinter.ttk

import submodules.find_scales
import submodules.fractions
import submodules.menu
import submodules.record_instrument
import submodules.view_scales
import submodules.bachbro_data


class BachBro(tkinter.Tk):
    """BachBro's main class

    tkinter window which includes all frames. Every frame represents one of
    MusicianAssisant's subprograms.
    """
    def __init__(self):
        """All frames are added, and the majpr variable data is set."""
        # Startup the window.
        super().__init__()
        
        # Set the main variables used by most tabs.
        # self.data provides all music theory data from the JSON files.
        self.data = submodules.bachbro_data.\
                    BachBroData(
                     os.getcwd().replace("\\", "/")+"/data/")
        self.current_file_number = 0
        
        # Add menu submodule.
        menu = submodules.menu.Menu(self)
        self["menu"] = menu

        # General options frame. Is located under the notebook.
        frame_general_options1 = tkinter.Frame(self)
        
        frame_instrument = tkinter.Frame(frame_general_options1)
        label_instrument = tkinter.Label(frame_instrument,
                                       text="Instrument for "
                                            "scale viewing or finding:")
        self.var_instrument = tkinter.StringVar()
        self.var_instrument.set(list(self.data.instruments.keys())[0])
        instrument = tkinter.ttk.Combobox(frame_instrument, width=50,
                                          textvariable=self.var_instrument)
        instrument.bind('<<ComboboxSelected>>', self._show_selected_instrument)
        instrument["values"] = list(self.data.instruments.keys())

        frame_midi_instrument = tkinter.Frame(frame_general_options1)
        label_midi_instrument = tkinter.Label(frame_midi_instrument,
                                              text="   MIDI "
                                                   "instrument for "
                                                   "MusicXML output:")
        self.var_midi_instrument = tkinter.StringVar()
        self.var_midi_instrument.set(list(self.data.midi_instruments.keys())[0])
        midi_instrument = tkinter.ttk.Combobox(frame_midi_instrument,
                                               width=50,
                                               textvariable=\
                                                self.var_midi_instrument)
        midi_instrument["values"] = list(self.data.midi_instruments.keys())
        
        frame_general_options2 = tkinter.Frame(self)
        frame_clef = tkinter.Frame(frame_general_options2)
        label_clef = tkinter.Label(frame_clef,
                                   text="Clef for MusicXML output:")
        self.var_clef = tkinter.StringVar()
        self.var_clef.set(list(self.data.clefs.keys())[0])
        clef = tkinter.ttk.Combobox(frame_clef, width=50,
                                    textvariable=self.var_clef)
        clef["values"] = list(self.data.clefs.keys())

        frame_mode = tkinter.Frame(frame_general_options2)
        label_mode = tkinter.Label(frame_mode,
                                   text="   Mode for MusicXML output:")
        self.var_mode = tkinter.StringVar()
        mode = tkinter.ttk.Combobox(frame_mode, width=50,
                                    textvariable=self.var_mode)
        values = list(self.data.modes.keys())
        values = [i+" ("+self.data.get_sharp_or_flat_number_text(i)+")" for i in values]
        self.var_mode.set(values[0])
        mode["values"] = values
        
        # Notebook instance for every frame.
        self.notebook = tkinter.ttk.Notebook(self)

        # Add frames.
        self.tab_fractions = submodules.fractions.Fractions(self)
        self.tab_view_scales = submodules.view_scales.ViewScales(self)
        self.tab_find_scales = submodules.find_scales.FindScales(self)
        self.tab_record_instrument = submodules.record_instrument.RecordInstrument(self)

        # Add tabs to notebook.
        self.notebook.add(self.tab_view_scales, text="View Scales/Chords")
        self.notebook.add(self.tab_find_scales, text="Find Scales/Chords")
        self.notebook.add(self.tab_fractions, text="Fractions calculator")
        self.notebook.add(self.tab_record_instrument, text="Get notes from .wav or microphone")
        self.notebook.pack()

        # Packaging of every frame.
        frame_general_options1.pack(side="top")
        frame_instrument.pack(side="left")
        label_instrument.pack(side="left")
        instrument.pack(side="left")
        frame_midi_instrument.pack(side="left")
        label_midi_instrument.pack(side="left")
        midi_instrument.pack(side="left")
        frame_general_options2.pack(side="top")
        frame_clef.pack(side="left")
        label_clef.pack(side="left")
        clef.pack(side="left")
        frame_mode.pack(side="left")
        label_mode.pack(side="left")
        mode.pack(side="left")

        # Run window.
        self.title("BachBro 0.1 BETA")
        self.mainloop()

    def _show_selected_instrument(self, *e):
        """Startup of instrument canvas and instrument notes checkboxes.
        
        Fired if the user selects an instrument via the instrument combobox.
        """
        self.tab_view_scales._make_instrument_canvas()
        self.tab_find_scales._make_instrument_checkboxes()


def main(args):
    """Starts BachBro."""
    BachBro()
    return 0

# Check if BachBro is already running in the same session.
if __name__ == '__main__':
    sys.exit(main(sys.argv))
