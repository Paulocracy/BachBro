#!/usr/bin/env python
#
# menu.py
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

"""menu.py - BachBro main window's menu.

This module consists of helper widget classes and the Menu instance.
"""


import json
import os
import tkinter
import tkinter.scrolledtext
import sys
import webbrowser


class AboutSubwindow(tkinter.Toplevel):
    """Helper subwindow for showing of license information.
    
    The window shows copyright information in a label, followed by the
    license text in a textbox.
    """
    def __init__(self, title, info, license_filepath=None):
        """Constructor of license information subwindow.
        
        Arguments:
        >title: The subwindow's title.
        >info: The subwindow label's info text.
        >license_filepath: The file path to the shown license.
        """
        super().__init__()
        self.title(title)
        label_info = tkinter.Label(self, text=info)
        label_info.pack()
        if license_filepath is not None:
            with open(license_filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            license_text = ""
            for line in lines:
                license_text += line
                label_license = tkinter.Label(self, text="License:")
            text_license = tkinter.scrolledtext.ScrolledText(self,
                                                             width=75)
            text_license.insert("end", license_text)
            label_license.pack()
            text_license.pack(fill="both", expand=True)
        self.mainloop()


class ChangeSubwindow(tkinter.Toplevel):
    """A subwindow contqaining an entry which allows to change a given setting.
    
    The settings were loaded vie BachBroData first.
    """
    def __init__(self, parent, title, setting):
        """Constructor of string change subwindow.
        
        Arguments:
        >parent: The parent tkinter window instance.
        >title: The subwindow's title.
        >setting: The name of the setting that shall be changed.
        """
        super().__init__()
        self.parent = parent
        self.title(title)
        self.setting = setting
        
        frame_change = tkinter.Frame(self)
        self.entry = tkinter.Entry(frame_change, width=50)
        button_change = tkinter.Button(frame_change, text="Change",
                                       command=self.change)
        self.entry.insert("end", self.parent.data.settings[self.setting])
        frame_change.pack()
        self.entry.pack(side="left")
        button_change.pack(side="left")
        self.mainloop()

    def change(self, *e):
        """The given value will be changed in the surrent settings instance and the settings file."""
        self.parent.data.settings[self.setting] = self.entry.get()

        with open(self.parent.data.settings_path, "w") as f:
            f.write(json.dumps(self.parent.data.settings))
        self.destroy()


class Menu(tkinter.Menu):
    """tkinter.Menu instance of BachBro's GUI menu.
    
    It consists of a "File", an "Edit" and an "About" cascade.
    """
    def __init__(self, parent):
        """Constructor of BachBro main window's menu.
        
        Arguments:
        >parent: The used BachBro instance.
        """
        super().__init__()
        self.parent = parent

        # "File" cascade.
        menu_file = tkinter.Menu(self)
        menu_file["tearoff"] = 0
        menu_file.add_command(label="End", command=self._file_end)
        self.add_cascade(label="File", menu=menu_file)

        # "Edit" cascade.
        menu_edit = tkinter.Menu(self)
        menu_edit["tearoff"] = 0
        menu_edit.add_command(label="Set scorewriter command...",
                              command=self._edit_set_sheet_editor_command)
        menu_edit.add_command(label="Set aubionotes command...",
                              command=self._edit_set_aubio_command)
        self.add_cascade(label="Edit", menu=menu_edit)

        # "Help" cascade.
        menu_help = tkinter.Menu(self)
        menu_help["tearoff"] = 0
        menu_help.add_command(label="Manual (in web browser)",
                              command=self._help_manual)
        menu_help.add_command(label="About aubio...",
                              command=self._help_about_aubio)
        menu_help.add_command(label="About MIDI...",
                              command=self._help_about_midi)
        menu_help.add_command(label="About MusicXML...",
                              command=self._help_about_musicxml)
        menu_help.add_command(label="About PyAudio...",
                              command=self._help_about_pyaudio)
        menu_help.add_command(label="About BachBro...",
                              command=\
                               self._help_about_musician_assistant)
        self.add_cascade(label="Help", menu=menu_help)
    
    def _edit_set_aubio_command(self):
        """Text entry to set the sheet editor command.
        
        BachBro will open its generated MusicXML files
        with the defined sheet editor. The MusicXML files will be given
        as separated arguments.
        """
        ChangeSubwindow(self.parent,
                        "aubio command",
                        "aubio command")
    
    def _edit_set_sheet_editor_command(self):
        """Text entry to set the sheet editor command.
        
        BachBro will open its generated MusicXML files
        with the defined sheet editor. The MusicXML files will be given
        as separated arguments.
        """
        ChangeSubwindow(self.parent,
                        "Sheet editor command",
                        "sheet editor command")

    def _file_end(self):
        """Closes BachBro. Returns 0."""
        sys.exit(0)

    def _help_about_aubio(self):
        """Shows license information of aubio.
        
        aubio's license is included as "LICENSE_aubio.txt" in the "docs"
        folder.
        aubio's source code can be found in the archive
        "aubio-0.4.2_source.tar.bz2" in the subfolder "submodules/aubio"
        of BachBro.
        Windows binaries of aubio are included in the subfolders
        "submodules/aubio/win32" and "submodules/aubio/win64".
        """
        info = "aubio (c) Paul Brossier\n"\
               "Website: https://www.aubio.org (Accessed in November 2016)\n"\
               "Github site: https://github.com/aubio/aubio (Accessed in November 2016)"
        license_filepath = os.getcwd().replace("\\", "/")+\
                           "/docs/LICENSE_aubio.txt"
        AboutSubwindow(title="About aubio...", info=info,
                       license_filepath=license_filepath)

    def _help_manual(self):
        """Opens BachBro's manual with the standard browser."""
        webbrowser.open(os.getcwd().replace("\\", "/")+
                        "/docs/manual.html")

    def _help_about_midi(self):
        """Shows license information of the MIDI standard.
        
        BachBro uses the 'General MIDI Level 1 Instrument
        Patch Map'.
        """
        info = "         MIDI (c) The MIDI Association         \n"\
               "Website: https://www.midi.org/ (Accessed in November 2016)\n"
        AboutSubwindow(title="About MIDI...", info=info,)
        
    def _help_about_musician_assistant(self):
        """Shows license information of BachBro."""
        info = "BachBro 0.1 BETA (c) Paulocracy, 2018\n"\
               "Github site: Not yet\n"
        license_filepath = os.getcwd().replace("\\", "/")+"/LICENSE.txt"
        AboutSubwindow(title="About BachBro...", info=info,
                       license_filepath=license_filepath)

    def _help_about_musicxml(self):
        """Shows license information of MusicXML."""
        info = "MusicXML (c) MakeMusic, Inc.\n"\
               "Website: https://www.musicxml.com/ (Accessed in November 2016)"
        license_filepath = os.getcwd().replace("\\", "/")+\
                           "/docs/LICENSE_MusicXML.txt"
        AboutSubwindow(title="About MusicXML...", info=info,
                       license_filepath=license_filepath)

    def _help_about_pyaudio(self):
        """Shows license information of pyaudio."""
        info = "PyAudio (c) 2006 Hubert Pham\n"\
               "Website: https://people.csail.mit.edu/hubert/pyaudio/ (Accessed in November 2016)"
        license_filepath = os.getcwd().replace("\\", "/")+\
                           "/docs/LICENSE_pyaudio.txt"
        AboutSubwindow(title="About PyAudio...", info=info,
                       license_filepath=license_filepath)
