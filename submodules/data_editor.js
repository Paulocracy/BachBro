/*
data_editor.js
Copyright (C) 2018 Paulocracy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
/*
 * This is the JavaScript file of the BachBro Data Editor. It is
 * called in "data_editor.html" in BachBro's main folder.
 * 
 * This data editor creates a convienient dynamically generated HTML file
 * of BachBro's JSON data files. The data can be edited, and
 * these edits can be saved.
 * 
 * Each BachBro JSON data file is describing a class of the
 * music theory, such as "instruments". Each class has instances, such as
 * the "guitar". Each instance has attributes, such as the "number of
 * strings".
 * 
 * The data editor shows at top an explanation of the class. Each instance
 * is shown separately. Every instance attribute is shown with an explanation
 * of it.
 * All class and attribute explanations are defined in this JavaScript file.
 * 
 * The dynamically generated HTML file has the following structure for
 * each instance (all instances are shown in the paragraph with the id
 * "edit"):
 * <div ... data-instance="..."> <!-- data-instance is the name of the class -->
 *   <h2>...</h2> <!-- "Key:" -->
 *   <input value="..."> <!-- The value is the instance's key -->
 *   <div>...</div> <!-- Instance div-internal divs without "data-type" attribute contain an attribute explanation text -->
 *   <div data-type="..."></div> <!-- This is an attribute widget where the user can change the value -->
 *   ...
 * </div>
 * 
 * This structure is much more understandable if you see it live while
 * having loaded a BachBro data JSON file.
 */

/* Sets the <h1> caption which is shown in both edit and file selection mode. */
function captionSet(text) {
    document.getElementById("caption").innerHTML = text
}

/* A hyperlink which triggers a JS function. */
function elementFunctionLink(description, method) {
    return "<a href='#' onClick='" + method + "()'>" + description + "</a><br/>"
}

/* Returns the 'n'-th previous DOM element of 'element'. */
function elementGetNthPreviousSibling(n, element) {
    for (i = 0; i < n; i++) {
        element = element.previousElementSibling
    }
    return element
}

/* Returns the 'n'-th next DOM element of 'element'. */
function elementGetNthNextSibling(n, element) {
    for (i = 0; i < n; i++) {
        element = element.nextElementSibling
    }
    return element
}

function elementHide(name) {
    document.getElementById(name).style.display = "none"
}

function elementShow(name) {
    document.getElementById(name).style.display = ""
}

/* Opens a new tab with the edited JSON as text output. */
function fileSave() {
    toSave = {} // Its content will be shown in the new tab

    // Iterating through all instance divs.
    keyDivs = document.getElementById("edit").getElementsByTagName("div")
    for (keyDiv of keyDivs) {
        instance = keyDiv.dataset.instance // The instance's class name.
        if (instance) { // Otherwise, it is not a keyDiv
            keys = keyDiv.getElementsByTagName("input")
            if (keys.length == 0) {
                continue
            }
            key = keys[0].value

            // Iterating through all attributes of the instance.
            toSave[key] = {}
            attributeDivs = keyDiv.getElementsByTagName("div")
            for (attributeDiv of attributeDivs) {
                type = attributeDiv.dataset.type
                if (!type) {
                    continue
                }
                variableName = attributeDiv.dataset.variable

                // Retrieve data according to attribute type.
                values = undefined
                if (type == "instrumentLabels") {
                    values = []
                    stringDivs = attributeDiv.getElementsByTagName("div")

                    if (stringDivs.length > 0) {
                        for (stringDiv of stringDivs) {
                            stringValues = []
                            labelInputs = stringDiv.getElementsByTagName("input")

                            if (labelInputs.length > 0) {
                                for (labelInput of labelInputs) {
                                    stringValues.push(labelInput.value)
                                }
                            }
                            values.push(stringValues)
                        }
                    }
                } else if (type == "integerList") {
                    values = []
                    textareaDivs = attributeDiv.getElementsByTagName("div")

                    if (textareaDivs.length > 0) {
                        for (textareaDiv of textareaDivs) {
                            textareas = textareaDiv.getElementsByTagName("textarea")
                            if (textareas.length > 0) {
                                values.push(parseInt(textareas[0].value))
                            }
                        }
                    }
                } else if (type == "integer") {
                    values = parseInt(attributeDiv.getElementsByTagName("input")[0].value)
                } else if (type == "stringNotes") {
                    values = []
                    noteDivs = attributeDiv.getElementsByTagName("div")

                    if (noteDivs.length > 0) {
                        for (noteDiv of noteDivs) {
                            inputs = noteDiv.getElementsByTagName("input")
                            if (inputs.length > 0) {
                                for (input of inputs) {
                                    if (input.type == "text") {
                                        note = input.value
                                    } else {
                                        octave = input.value
                                    }
                                }
                                values.push([note, octave])
                            }
                        }
                    }
                } else if (type == "text") {
                    values = attributeDiv.getElementsByTagName("input")[0].value
                } else if (type == "textList") {
                    values = []
                    textareaDivs = attributeDiv.getElementsByTagName("div")

                    if (textareaDivs.length > 0) {
                        for (textareaDiv of textareaDivs) {
                            textareas = textareaDiv.getElementsByTagName("textarea")
                            if (textareas.length > 0) {
                                values.push(textareas[0].value)
                            }
                        }
                    }
                }

                toSave[key][variableName] = values
            }
        }
    }

    // Create and show JSON as text.
    toSave = JSON.stringify(toSave, null, "\t")

    newTab = window.open("", "Save")
    newTab.document.write("<pre>" + toSave + "</pre>")

    if (newTab != undefined) {
        newTab.focus()
    } else {
        alert("Please allow pop-ups for BachBro data editor.")
    }
}

/* Adds a copy of the instance div either above or below its current position. */
function instanceAddCopy(clickedButton, direction) {
    key = clickedButton.parentNode.dataset.instance
    newElement = document.createElement("div")
    newElement.dataset.instance = key
    newElement.innerHTML = instanceDivDeclaration(key) + clickedButton.parentNode.innerHTML + "</div>"

    if (direction == "above") {
        clickedButton.parentNode.parentNode.insertBefore(newElement, clickedButton.parentNode)
    } else {
        clickedButton.parentNode.parentNode.insertBefore(newElement, clickedButton.parentNode.nextSibling)
    }
}

/* Adds a new instance of the file's class above 'clickedButton''s instance div. */
function instanceAddNew(clickedButton) {
    key = clickedButton.parentNode.dataset.instance
    instanceKey = ""
    fileData = undefined
    editMode = editModes[key]
    source = instanceRepresentation(key, instanceKey, fileData, editMode, true)

    newElement = document.createElement("div")
    newElement.dataset.instance = key
    newElement.innerHTML = source
    clickedButton.parentNode.parentNode.insertBefore(newElement, clickedButton.parentNode)
}

/* Deletes the instance div. */
function instanceDelete(clickedButton) {
    clickedButton.parentElement.remove()
}

/* Style (visual separation of instances) and instance dataset variable setting. */
function instanceDivDeclaration(key) {
    source = "<div style='padding-top:5px; padding-left:5px; padding-bottom:30px; border:1px solid black' data-instance='" + key + "'>"
    return source
}

/* Returns the HTML of a class instance either with the given data or default values. */
function instanceRepresentation(key, instanceKey, fileData, editMode, isDefault) {
    // Instance key name entry and instance copying/deletion/adding buttons.
    source = ""
    source += instanceDivDeclaration(key)
    source += "<h2 style='display: inline'>Instance: </h2>"
    source += "<input type='text' size='50' value='" + instanceKey + "'/>"
    source += "<button onClick='instanceDelete(this)'>Delete instance</button>"
    source += "<button onClick='instanceAddCopy(this, " + '"' + "above" + '"' + ")'>Add copy above</button>"
    source += "<button onClick='instanceAddCopy(this, " + '"' + "below" + '"' + ")'>Add copy below</button>"
    source += "<button onClick='instanceAddNew(this)'>Add new instance above</button>"

    // Addition of widgets which correspond to the attribute's type.
    if (!isDefault) {
        instance = fileData[instanceKey]
    }
    attributeKeys = Object.keys(editMode["attributes"])
    for (attributeKey of attributeKeys) {
        attribute = editMode["attributes"][attributeKey]
        source += "<div style='padding-top:20px;padding-bottom:5px'>"
        source += "<div style='font-size:24px'>" + attribute["key"] + "</div>"
        source += attribute["description"] + "</div>"

        type = attribute["type"]
        source += "<div data-type='" + type + "' data-variable='" + attribute["key"] + "'>"

        if (!isDefault) {
            value = instance[attribute["key"]]
        } else {
            value = defaults[attribute["type"]]
        }


        if (type == "instrumentLabels") {
            source += widgetInstrumentLabels(value)
        } else if (type == "integerList") {
            source += widgetIntegerList(value)
        } else if (type == "integer") {
            source += widgetInteger(value)
        } else if (type == "stringNotes") {
            source += widgetStringNotes(value)
        } else if (type == "text") {
            source += widgetText(value)
        } else if (type == "textList") {
            source += widgetTextList(value)
        }
        source += "</div>"
    }
    source += "</div>"
    return source
}

/* Hides the file selection, loads the selected JSON file and shows its content. */
function viewEditMode() {
    selectedFile = document.getElementById("file").files[0]
    fileReader = new FileReader()

    fileReader.addEventListener("load", function () {
        // Check if the file is a JSON file.
        try {
            fileData = JSON.parse(fileReader.result)
        } catch (error) {
            alert("The selected file is not a valid JSON file.")
            return
        }

        // Check if it is an editable BachBro data file.
        key = selectedFile.name.replace(".json", "")
        editMode = editModes[key]
        if (!editMode) {
            alert("The selected file is not a supported BachBro data JSON file (filename unknown).")
            return
        }

        // Switch view to file data view.
        elementHide("caption")
        elementHide("file")
        elementShow("edit")

        // Add file description, instance views and file saving link.
        source = ""
        source += elementFunctionLink("Back to file selection", "viewSelection")
        source += "<h1>" + selectedFile.name + "</h1>"
        source += "<div style='padding-bottom:20px'>" + editMode.text + "</div>"

        instanceKeys = Object.keys(fileData)
        for (instanceKey of instanceKeys) {
            source += instanceRepresentation(key, instanceKey, fileData, editMode, false)
        }
        source += "<div data-instance='" + key + "' style='padding-top:5px'>"
        source += "<button onClick='instanceAddNew(this)'>Add new instance</button><br/></div>"
        source += "<p style='font-size:30px'>"
        source += elementFunctionLink("Save edited " + selectedFile.name, "fileSave")
        source += "</p>"

        document.getElementById("edit").innerHTML = source
    }, false)

    if (selectedFile) {
        fileReader.readAsText(selectedFile)
    }
}

/* Shows the file selection. */
function viewSelection() {
    elementHide("edit")
    elementShow("caption")
    elementShow("file")
    captionSet("Choose BachBro data file to edit (usually located in BachBro's 'data' subfolder):")
}

/* Text entries which represent with their value a label on one note of one particular string. */
function widgetInstrumentLabels(values) {
    source = ""
    for (line of values) {
        source += "<div>"
        for (label of line) {
            source += widgetInstrumentLabelsSingleInput(label)
        }
        source += "</div>"
    }
    source += "<button onClick='widgetInstrumentLabelsAdjust(this)'>"
    source += "Readjust label number to changed string number and/or properties (deletes all current labels)</button><br/>"
    return source
}

/* Adjust the number of text entry lines and rows to the number of notes on each string. Each string has the same number of notes. */
function widgetInstrumentLabelsAdjust(clickedButton) {
    // Get string property containing inputs.
    labelWidget = clickedButton.parentElement
    fretDistanceWidget = elementGetNthPreviousSibling(2, labelWidget)
    stringRangeWidget = elementGetNthPreviousSibling(2, fretDistanceWidget)
    stringStartNotesWidget = elementGetNthPreviousSibling(2, stringRangeWidget)

    // Get string property values from the selected inputs.
    stringNumber = stringStartNotesWidget.getElementsByTagName("div").length - 1
    stringRange = stringRangeWidget.getElementsByTagName("input")[0].value
    stringRange = parseInt(stringRange)
    fretDistance = fretDistanceWidget.getElementsByTagName("input")[0].value
    fretDistance = parseInt(fretDistance)

    // Calculate row number.
    numFrets = stringRange / fretDistance
    if (!Number.isInteger(numFrets)) {
        alert("Error: stringRangeInCents divided by fretDistanceInCents is not an integer.")
        return
    }

    // Delete old label field.
    while (labelWidget.getElementsByTagName("div").length > 0) {
        labelWidget.getElementsByTagName("div")[0].remove()
    }

    // Generate new label field according to the changes string properties.
    source = ""
    for (let i = 0; i < stringNumber; i++) {
        source += "<div>"
        for (let j = 0; j < numFrets; j++) {
            source += widgetInstrumentLabelsSingleInput("")
        }
        source += "</div>"
    }
    labelWidget.innerHTML = source + labelWidget.innerHTML
}

/* A small text input. */
function widgetInstrumentLabelsSingleInput(value) {
    source = "<input type='text' size='3' value='" + value + "'/>"
    return source
}

/* HTML number input. */
function widgetInteger(value) {
    source = "<input type='number' value='" + value + "'/><br/>"
    return source
}

/* A list of lines of one text input (describing the note name) and a correspongding number input (describing the octave) */
function widgetStringNotes(values) {
    source = ""
    for (startNote of values) {
        source += "<div>"

        source += widgetStringNotesSingleElement(startNote)
        source += "</div>"
    }
    source += "<div><button onClick='widgetStringNotesAddNote(this)'>Add new element</button><br/></div>"
    return source
}

function widgetStringNotesDeleteNote(clickedButton) {
    clickedButton.parentNode.remove()
}

/* Adds a new note div above. */
function widgetStringNotesAddNote(clickedButton) {
    var newElement = document.createElement("div")
    newElement.innerHTML = widgetStringNotesSingleElement(["", 0])
    clickedButton.parentNode.parentNode.insertBefore(newElement, clickedButton.parentNode)
}

/* The string start note widget consists of an integer input, a text input and buttons. */
function widgetStringNotesSingleElement(startNote) {
    note = startNote[0]
    octave = startNote[1]

    source = ""
    source += "<input type='text' value='" + note + "'/>"
    source += "<input type='number' value='" + octave + "'/>"
    source += "<button onClick='widgetStringNotesDeleteNote(this)'>Delete element</button>"
    source += "<button onClick='widgetStringNotesAddNote(this)'>Add new element above</button>"

    return source
}

/* HTML text input. */
function widgetText(value) {
    source = "<input size='50' type='text' value='" + value + "'/><br/>"
    return source
}

/* A list of text inputs with list action buttons. */
function widgetTextList(values) {
    source = ""
    if (values.length > 0) {
        for (value of values) {
            source += "<div>"
            source += widgetTextListSingleInput(value)
            source += "</div>"
        }
    }
    source += "<div><button onClick='widgetTextListAddElement(this)'>Add new element</button><br/></div>"
    return source
}

/* Adds a text input with list action buttons above. */
function widgetTextListAddElement(clickedButton) {
    newElement = document.createElement("div")
    newElement.innerHTML = widgetTextListSingleInput("")
    clickedButton.parentNode.parentNode.insertBefore(newElement, clickedButton.parentNode)
}

function widgetTextListDeleteElement(clickedButton) {
    clickedButton.parentElement.remove()
}

/* One text input with list action buttons. */
function widgetTextListSingleInput(value) {
    source = "<textarea rows='1' columns='25'>" + value + "</textarea>"
    source += "<button onClick='widgetTextListDeleteElement(this)'>Delete element</button>"
    source += "<button onClick='widgetTextListAddElement(this)'>Add new element above</button><br/>"
    return source
}

/* A list of number inputs with list action buttons. */
function widgetIntegerList(values) {
    source = ""
    if (values.length > 0) {
        for (value of values) {
            source += "<div>"
            source += widgetIntegerListSingleInput(value)
            source += "</div>"
        }
    }
    source += "<div><button onClick='widgetIntegerListAddElement(this)'>Add new element</button><br/></div>"
    return source
}

/* Adds a number input. */
function widgetIntegerListAddElement(clickedButton) {
    newElement = document.createElement("div")
    newElement.innerHTML = widgetIntegerListSingleInput("0")
    clickedButton.parentNode.parentNode.insertBefore(newElement, clickedButton.parentNode)
}

function widgetIntegerListDeleteElement(clickedButton) {
    clickedButton.parentElement.remove()
}

/* One number input with list action buttons. */
function widgetIntegerListSingleInput(value) {
    source = "<input type='number' value='" + value + "'/>"
    source += "<button onClick='widgetIntegerListDeleteElement(this)'>Delete element</button>"
    source += "<button onClick='widgetIntegerListAddElement(this)'>Add new element above</button><br/>"
    return source
}

/* Global variables which describe the JSON structure of the BachBro data files. */
// The definition of the attributes of all BachBro data file classes.
var attributesClefs = [{
        "key": "sign",
        "description": "The MusicXML sign type, which defines the clef's look. Some possible values are 'G', 'C' and 'F'.",
        "type": "text"
    },
    {
        "key": "line",
        "description": "Defines on which note sheet line (from the bottom) the clef should apper. E.g., a usual 'G' clef appears on the second line.",
        "type": "integer"
    },
    {
        "key": "octave_change",
        "description": "Shows if this clef is an octave changed version of the 'sign' clef. Is 0, if there is no octave change.<br/>E.g., the octave lowered 'G' clef has an octaveChange value of '-1'.",
        "type": "integer"
    }
]

var attributesGenres = [{
        "key": "weakConsonantIntervals",
        "description": "All intervals of this genre which are regarded as non-dissonant, but at the same time as not perfectly consonant, too. " +
            "All values must have a corresponding name in intervals.json.",
        "type": "textList"
    },
    {
        "key": "strongConsonantIntervals",
        "description": "All intervals of this genre which are regarded as perfectly consonant." +
            "All values must have a corresponding name in intervals.json.",
        "type": "textList"
    },
    {
        "key": "weakDissonantIntervals",
        "description": "All intervals of this genre which are regarded as non-consonant, but at the same time as not totally dissonant, too." +
            "All value must have a corresponding name in intervals.json.",
        "type": "textList"
    },
    {
        "key": "strongDissonantIntervals",
        "description": "All intervals of this genre which are regarded as totally consonant, just like the tritonus in classical western music." +
            "All value must have a corresponding name in intervals.json.",
        "type": "textList"
    },
    {
        "key": "rhythmFile",
        "description": "If there is a MusicXML file which shows the usual rhythms of this genre (other information is possible), too, its file location " +
            "(starting from BachBro's 'data' subfolder) has to be given here.<br/>" +
            "E.g., if there is a 'westernRhythms.xml' file in the 'data' subfolder for this instance's genre, the value of this attribute would " +
            "be 'westernRhythms.xml'.<br/>" +
            "The file has to be in the 'data' folder or in a subfolder of it.<br/>" +
            "The information sources of this file should be named in this file.<br/>" +
            "If there is no such rhythm file, the value can be left empty.",
        "type": "text"
    },
    {
        "key": "sources",
        "description": "The information sources for this instance's data, e.g. a book or a website. Each element will be shown in an own paragraph.",
        "type": "textList"
    }
]

var attributesInstruments = [{
        "key": "stringStartNotes",
        "description": "Each note stands for the lowest (first) note which is played on one string of the instrument. E.g., if there two notes 'B,3'" +
            " and 'A,2' are given, the instrument will have two strings, where the lowest playable notes are 'B' in the 3nd octave as well as " +
            "'A' in the 2nd octave." +
            "<br/>The note names must have a representative in the note names in notes.json.",
        "type": "stringNotes"
    },
    {
        "key": "stringRangeInCents",
        "description": "The range of playable notes on each string of this instrument in cents (100 cents = one semitone, and 200 cents = one whole tone). " +
            "E.g., if only the notes 'C' and 'C#' can be played on a one-stringed instrument, the value would be '100' (the distance between 'C' and 'C#', a semitone).<br/>" +
            "The minimal value is 0. " +
            "The division of this instance's stringRangeInCents by its fretDistanceInCents must result in an whole-number, as this division shows how many frets this instrument has on each string (a comma value would make no sense here).",
        "type": "integer"
    },
    {
        "key": "fretDistanceInCents",
        "description": "The distance of playable notes on this instrument in cents (100 cents = one semitone, and 200 cents = one whole tone). " +
            "E.g., a typical fretted western string instrument (such as an acoustic guitar) has a fret distance of 100 (one semitone, like from 'C' to 'C#', as no tone between 'C' and 'C#' can be played on such a guitar).<br/>" +
            "The minimal value is 0, the maximal value this instance's value of 'stringRangeInCents'.<br/>" +
            "The division of this instance's stringRangeInCents by its fretDistanceInCents must result in an whole-number, as this division shows how many frets this instrument has on each string (a comma value would make no sense here).",
        "type": "integer"
    },
    {
        "key": "labels",
        "description": "Each line of input fields stands for one string of the instrument, in the same order as the strings in this instance's stringStartNotes." +
            " Each row stands for one note of this string.<br/>" +
            "Every kind of text is usable, but non-latin characters and long text may not be displayed properly.<br/>" +
            "Keep in mind that you have to adjust the number of lines and rows after the number of strings in 'stringNotes' and/or the value of 'stringRangeInCents' and/or 'fretDistanceInCents' is changed.",
        "type": "instrumentLabels"
    }
]

var attributesIntervals = [{
    "key": "cents",
    "description": "The interval value in cents (100 cents = one semitone, and 200 cents = one whole tone) of the interval. E.g., a minor second has a cent value of 100 cents, and a major second a value of 200 cents.<br/>" +
        "The value cannot be negative.",
    "type": "integer"
}]

var attributesMidiInstruments = [{
    "key": "midiNumber",
    "description": "The number by which this instrument can be found according to the MIDI standard.",
    "type": "integer"
}]

var attributesModes = [{
    "key": "numberSharps",
    "description": "Shows by how many sharps or flats after the clef this mode is represented. The value is 0, if there should be no flats or sharps." +
        "The value is positive and greater than 0, if the mode is represented with sharps, and negative, if it is represented by flats.<br/>" +
        "E.g., the 'G major' mode has the value '1' (for 1 sharp), whereas the mode 'F major' has the value '-1' (for one flat).",
    "type": "integer"
}]

var attributesNoteLengths = [{
        "key": "divisions",
        "description": "Shows how many times longer than a 64th note this note length is. E.g., a '16th' note length is 4 times longer than a 64th note.<br/>" +
            "The minimal value is 1. There is theoretically no maximal value, although lengths longer than a whole note (64 times a 64th note) may be problematic for some scorewriters.",
        "type": "integer"
    },
    {
        "key": "musicXMLType",
        "description": "The representation of this note in the MusicXML standard (used in the MusicXML export of audio recordings and scale/chord samples).<br/>" +
            "E.g., quarter notes have the representation '1/4'. Consult the MusicXML standard documentation to find out the correct one.",
        "type": "text"
    },
    {
        "key": "musicXMLAddition",
        "description": "Is empty, if the length should not be represented with a dot (such as a quarter note). Is 'dot', if the length should be represented as a dotted note (such as the dotted quarter note).<br/>" +
            "This addition is used in the MusicXML export.",
        "type": "text"
    },
    {
        "key": "calculatorSymbol",
        "description": "The text that shall be shown in the fractions calculator for this note length. E.g., quarter notes have the text '1/4'.",
        "type": "text"
    }
]

var attributesNotes = [{
        "key": "centsToC",
        "description": "The distance (in cents: 100 cents = one semitone, and 200 cents = one whole tone) of this note to the next lower 'C'.<br/>" +
            "E.g., the note 'C#' has a distance of 100 cents (one semitone), whereas 'B' has a distance of 1100 (eleven semitones).<br/>" +
            "The distance cannot be negative. The maximal value is 1200 (12 semitone, one octave).",
        "type": "integer"
    },
    {
        "key": "musicXMLStep",
        "description": "The whole tone (according to the MusicXML standard) by which this note is called. " +
            "E.g., the musicXMLStap of a C-flat note (the note is called after the 'C') instance would be 'C'.<br/>" +
            "Possible values are 'A', 'B', 'C', 'D', 'E', 'F' and 'G'.",
        "type": "text"
    },
    {
        "key": "musicXMLAlter",
        "description": "The distance (in semitones: 1.0 is one semitone, 2.0 a whole tone) of the note to the note to which it is called after.<br/>" +
            "E.g., the note 'C' has the distance 0.0 to 'C', whereas 'C#' has the distance 1.0, and 'Cb' the distance -1.0.",
        "type": "text"
    },
    {
        "key": "musicXMLAccidental",
        "description": "The accidental symbol (according to the MusicXML standard) that should be shown by a scorewriter together with this note. " +
            "Some possible values are 'sharp', 'flat', 'quarter-sharp' and 'slash-flat'.",
        "type": "text"
    }
]

var attributesScales = [{
        "key": "notesInCentsToKeynote",
        "description": "Each element stands for one note of the scale. E.g., if there are 8 elements, the scale will be octatonic.<br/> " +
            "Each numeric value of an element stands for the distance (in cents: 100 cents = one semitone, and 200 cents = one whole tone) of " +
            "the represented note to the next lower keynote of the scale.<br/>" +
            "E.g., in a C major scale, the distance of the note 'D' is 200 cents to the next lower keynote (the C). Therefore, in a major scale, " +
            "the first numeric element has the value '200'.",
        "type": "integerList"
    },
    {
        "key": "info",
        "description": "Some information about this scale (the sources should be written as elements of this instance's 'source' attribute. Each element will " +
            "be shown in an own paragraph.",
        "type": "textList"
    },
    {
        "key": "sources",
        "description": "One or more references (e.g. a book or a website) for the scale data. Each element will be shown in an own paragraph.",
        "type": "textList"
    }
]

// Default values depending on attribute type. Used if a new blank instance is created.
var defaults = {
    "text": "",
    "integer": 0,
    "textList": [],
    "integerList": [],
    "instrumentLabels": [],
    "stringNotes": []
}

// The key names stand for the JSON file names. "text" is the file's content global description, "attributes" information about the instance's attributes.
var editModes = {
    "clefs": {
        "text": "The clefs are used in the MusicXML export.",
        "attributes": attributesClefs
    },
    "genres": {
        "text": "As defined here, genres are historically developed traditions of music playing and composition, just like the western classical music genre (from baroque to early romanticism).",
        "attributes": attributesGenres
    },
    "instruments": {
        "text": "All instruments for the scale viewer and the scale finder.",
        "attributes": attributesInstruments
    },
    "intervals": {
        "text": "The interval definitions are used for the genres definitions.",
        "attributes": attributesIntervals
    },
    "midi_instruments": {
        "text": "The instances represent the instruments of the MIDI standard. " +
            "This standard is used by MusicXML playback programs, such as usual scorewriters.",
        "attributes": attributesMidiInstruments
    },
    "modes": {
        "text": "The mode definitions are used for the MusicXML export. Each mode stands for how many sharps or flats should be shown right after the clef.",
        "attributes": attributesModes
    },
    "note_lengths": {
        "text": "The note lenghts are used in the MusicXML export, as well as in the fractions calculator.",
        "attributes": attributesNoteLengths
    },
    "notes": {
        "text": "All notes (in the sense of the pitch of a tone) which are used e.g. for the instrument, keynote and MusicXML export functions. Non-western standard notes (translated into a well-tempered system) are usable, too. Currently, '#2' stands for a half-sharp and 'b2' for a half-flat.",
        "attributes": attributesNotes
    },
    "scales": {
        "text": "All scales that can be shown e.g. on the piano, the other instruments, in the MusicXML samples and in the scale finder.",
        "attributes": attributesScales
    }
}

// Start with the file selection dialog view.
viewSelection()