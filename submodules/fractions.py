#!/usr/bin/env python
#
# fractions.py
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

"""fractions.py

This is a fraction number summation calculator for BachBro. It may be
used to determine rhythms of heard music.
"""

import tkinter


class Fractions(tkinter.Frame):
    """All widgets and methods for the fraction number calculator."""
    def __init__(self, parent):
        """Sets and displays all fraction calculator widgets."""
        # Startup.
        super().__init__()
        self.parent = parent  # For communication with other widgets and data.
        self.result = 0.0     # The summation result.

        # Setting of note lengths for the calculator from JSON note length data.
        # The variable elements include the note length value as a float and
        # the displayed name of the note length.
        self.note_lengths = []
        whole_note_length = float(self.parent.data.note_lengths["whole"]["divisions"])
        for key in self.parent.data.note_lengths:
            note_length_float = float(self.parent.data.note_lengths[key]["divisions"])
            note_length_float /= whole_note_length
            note_length_name = self.parent.data.note_lengths[key]["calculatorSymbol"]
            note_length_tuple = (note_length_float, note_length_name)
            self.note_lengths.append(note_length_tuple)
        
        # Setting of widgets.
        # Button widgets.
        label_buttons = tkinter.Label(self, text="Add note length "
                                                 "value to addition:")

        frame_buttons = tkinter.Frame(self)
        _reset = tkinter.Button(frame_buttons, text="Reset to 0",
                                command=self._reset)
        label_buttons.pack()
        _reset.pack(side="left")
        for note_length in self.note_lengths:
            value = note_length[0]
            text = note_length[1]
            command = lambda value=value, text=text: self._add(value, text)
            button = tkinter.Button(frame_buttons, text=text, command=command)
            button.pack(side="left")

        # Input and result widgets.
        label_input = tkinter.Label(self, text="Current input:")
        # Widget to show all lengths of summation.
        self.text_input = tkinter.Entry(self, width=50)
        # Widget to show the summation result divided to the given note
        # lengths.
        self.text_result = tkinter.Label(self)

        # Rest of packing of widgets.
        frame_buttons.pack()
        label_input.pack()
        self.text_input.pack(fill="x")
        self.text_result.pack()
        self._update_text()

    def _add(self, value, text):
        """Adds the value to the current resulting sum.

        It also displays the text to the output text field."""
        self.text_input.insert("end", text+"  ")
        self.result += value
        self._update_text()

    def _reset(self):
        """Resets all results and text to a current resulting sum of 0."""
        self.text_input.delete("0", "end")
        self.result = 0
        self._update_text()

    def _update_text(self):
        """Updates the result text label to the current summation result."""
        # Creates list of tuples with note length display text and the current
        # sum result divided to the specific note length.
        results = [(i[1], self.result/i[0]) for i in self.note_lengths]

        # Text label filling.
        result_string = "Result (* = natural number):\n"
        for value in results:
            result_string += value[0]+" "
            result_string += str(round(value[1], 5))
            if (value[1] % 1.0 == 0) and (value[1] > 0):
                result_string += "*"
            result_string += "\n"

        self.text_result["text"] = result_string
