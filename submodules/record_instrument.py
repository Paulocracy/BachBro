#!/usr/bin/env python
#
# record_instrument.py
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

"""record_instrument.py - Module for getting notes from microphone or .wav record.

The microphone is accessed with pyaudio. The note recognition is done by
calling aubio.
"""


import pyaudio
import threading
import time
import tkinter
import tkinter.messagebox
import tkinter.ttk
import tkinter.filedialog
import wave


class RecordInstrument(tkinter.Frame):
    """Main class for note recognition from an .wav file."""
    def __init__(self, parent):
        """All iwdgets and member variables are set here.
        
        Arguments:
        >parent: The BachBro instance.
        """
        super().__init__()
        self.parent = parent
        
        frame_lowest_note_name = tkinter.Frame(self)
        frame_highest_note_name = tkinter.Frame(self)
        frame_lowest_note_octave = tkinter.Frame(self)
        frame_highest_note_octave = tkinter.Frame(self)
        
        # Octave comboboxes.
        octaves = [2,3,4,5,6]
        self.var_min_octave = tkinter.IntVar()
        self.var_min_octave.set(3)
        min_octave = tkinter.ttk.Combobox(frame_lowest_note_octave,
                                          width=15,
                                          textvariable=\
                                          self.var_min_octave)
        min_octave["values"] = octaves

        self.var_max_octave = tkinter.IntVar()
        self.var_max_octave.set(6)
        max_octave = tkinter.ttk.Combobox(frame_highest_note_octave, width=15,
                                          textvariable=\
                                          self.var_max_octave)
        max_octave["values"] = octaves
        
        # Note name comboboxes.
        self.var_min_note = tkinter.StringVar()
        self.var_min_note.set("F#")
        min_note = tkinter.ttk.Combobox(frame_lowest_note_name, width=15,
                                        textvariable=\
                                        self.var_min_note)
        min_note["values"] = list(self.parent.data.notes.keys())

        self.var_max_note = tkinter.StringVar()
        self.var_max_note.set("G")
        max_note = tkinter.ttk.Combobox(frame_highest_note_name, width=15,
                                        textvariable=\
                                        self.var_max_note)
        max_note["values"] = list(self.parent.data.notes.keys())


        self.note_lengths = tkinter.Listbox(self,
                                            selectmode="multiple",
                                            width=20,
                                            height=10)
        for key in (self.parent.data.note_lengths.keys()):
            note_length = key
            self.note_lengths.insert("end", note_length)
        
        # Labels and packing.
        label_min = tkinter.Label(self, text="Lowest note (this note and all lower recognized ones will be ignored):")
        label_min_name = tkinter.Label(frame_lowest_note_name, text="Name:")
        label_min.pack()
        frame_lowest_note_name.pack()
        label_min_name.pack(side="left")
        min_note.pack(side="left")
        
        frame_lowest_note_octave.pack()
        label_min_octave = tkinter.Label(frame_lowest_note_octave, text="Octave:")
        label_min_octave.pack(side="left")
        min_octave.pack(side="left")

        label_max = tkinter.Label(self, text="\nHighest note (all higher recognized notes will be ignored):")
        label_max.pack()
        frame_highest_note_name.pack()
        label_max_name = tkinter.Label(frame_highest_note_name, text="Name:")
        label_max_name.pack(side="left")
        max_note.pack(side="left")
        label_max_octave = tkinter.Label(frame_highest_note_octave, text="Octave:")
        frame_highest_note_octave.pack()
        label_max_octave.pack(side="left")
        max_octave.pack(side="left")

        label_exclude = tkinter.Label(self, text="\nExclude note lengths:")
        label_exclude.pack()
        self.note_lengths.pack()
        
        label_space = tkinter.Label(self, text="")
        label_space.pack()
        
        # Confidence threshold entry.
        frame_threshold = tkinter.Frame(self)
        label_threshold = tkinter.Label(frame_threshold,
                                        text="aubio confidence threshold "
                                             "(notes with lower recognition confidence will be ignored):")
        self.entry_threshold = tkinter.Entry(frame_threshold, width=20)
        self.entry_threshold.insert("end", ".8")
        label_threshold.pack(side="left")
        self.entry_threshold.pack(side="left")
        frame_threshold.pack()
        
        label_space = tkinter.Label(self, text="")
        label_space.pack()
        
        # Buttons.
        set_wav = tkinter.Button(self, text="Read and show notes from .wav (using aubio)", command=self._set_wav)
        set_wav.pack()
        
        self.record_text = "Record from microphone and show read notes (using PyAudio and aubio) "\
                           "[Menu key or Scroll Lock]"
        self.button_record_and_show = tkinter.Button(self,
                                                     text=self.record_text,
                                                          command=self._set_recording)
        self.button_record_and_show.pack()
        
        # Key bindings.
        self.parent.bind("<App>", self._set_recording)
        self.parent.bind("<Scroll_Lock>", self._set_recording)
        
        # .wav settings for aubio.
        self.chunk = 1024
        self.format_ = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

        self.is_recording = False
        self.record_wav_number = 0
        self.wav_path = ""

    def _create_musicxml(self, xml_path, title):
        """Cretes the MusicXML containing all notes recognized by aubio.
        
        Arguments:
        >xml_path: The MusicXML's file path.
        >title: The MusicXML's score title.
        """
        notes = self.parent.data.read_notes_from_wav(
                     filepath=self.wav_path,
                     disallowed_note_lengths=\
                      self.note_lengths.curselection(),
                     min_note=self.var_min_note.get(),
                     min_octave=self.var_min_octave.get(),
                     max_note=self.var_max_note.get(),
                     max_octave=self.var_max_octave.get(),
                     error_threshold=self.entry_threshold.get())
        if notes is False:
            tkinter.messagebox.showinfo("BachBro - No notes detected",
                                        "Aubio could not detect any note."\
                                        "You could try to use a lower confidence threshold.")
        
        mode = self.parent.var_mode.get().split(" (")[0]
        self.parent.data.create_musicxml(xml_path,
                                         "From wav",
                                         self.parent.var_clef.get(),
                                         mode,
                                         self.parent.var_midi_instrument.get(),
                                         notes)
        self.parent.data.open_with_sheet_editor(xml_path)

    def _record(self):
        """Threaded method for recording from microphone."""
        self.audio = pyaudio.PyAudio()
        
        try:
            stream = self.audio.open(format=self.format_,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.chunk)
        except:
            self.button_record_and_show["text"] =  self.record_text
            self.is_recording = False
            tkinter.messagebox.showerror("BachBro - Error",
                                         "No audio input device could be detected by pyaudio.\n"\
                                         "Check if the microphone is activated or properly"\
                                         " connected with the computer.")
            return
            
        self.frames = []
        while self.is_recording: # Is set via self._set_recording outside of this method's thread.
            data = stream.read(self.chunk)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        self.audio.terminate()

    def _set_recording(self, *e):
        """Starts microphone recording and saving of it into a .wav file."""
        if not self.is_recording:
            self.is_recording = True
            self.button_record_and_show["text"] = "RECORDING..."
            self.record_thread = threading.Thread(target=self._record)
            self.record_thread.start()
        else:
            self.is_recording = False
            self.button_record_and_show["text"] =  self.record_text
            while self.record_thread.is_alive():
                time.sleep(.01)
            wav_name = "./data/temp/"+str(self.record_wav_number)+".wav"
            wf = wave.open(wav_name, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format_))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            self.wav_path = wav_name
            self._create_musicxml("./data/temp/MA" +
                                  str(self.parent.current_file_number)+".xml",
                                  "Recognized notes (by aubio) from microphone recording")
            self.parent.current_file_number += 1
    
    def _set_wav(self, *e):
        """Selection of the .wav file from which notes shall be recognized."""
        wav_path = tkinter.filedialog.askopenfilename(filetypes=
                                                      (("WAVE files", ".wav"),
                                                       ("All files", "*.*"),))
        if wav_path:
            self.wav_path = wav_path
            self._create_musicxml("./data/temp/MA" +
                                  str(self.parent.current_file_number)+".xml",
                                  "Recognized notes (by aubio) from .wav file")
            self.parent.current_file_number += 1
