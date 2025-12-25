"""
Takes in txt file that has standard guitar tabs and converts to banjo tabs. Only convets to banjo strings 1-4, leaving 5th string for manual conversion. 

Finds lowest guitar note to determine offset needed to fit on banjo tuning. For notes that too high, also converts to lower octives.
"""

import re
import numpy as np

path = "such_great_heights.txt" # path to file to convert
out_file = "such_great_heights_banjo.txt" # filename to save output to

ADDITIONAL_OFF_SET = None # can add this to shift song up or down in addition to the conversion off set, adds to found off set
USER_OFF_SET = None # can use this if you know the off set desired already, replaces found off set

# can change the tunings to whatever is needed
guitar_tuning = "EADGBE" # string order 654321

# ignoring fifth string in conversion, worked out better to manually set that
banjo_tuning = "CGBD" # string order 4321
# lowest tunings gCGCD, fCFAC
# 22 frets on banjo

note_to_num = {'A': 10,
              'A#': 11,
              r'A\u266F': 11,
              r'Bb': 11,
              r'Bb\u266D': 11,
              'B': 12,
              'C': 1,
              r'C#': 2,
              r'Db': 2,
              r'C\u266F': 2,
              r'D\u266D': 2,
              'D': 3,
              r'D#': 4,
              r'Eb': 4,
              r'D\u266F': 4,
              r'E\u266D]': 4,
              'E': 5,
              'F': 6,
              r'F#': 7,
              r'Gb': 7,
              r'F\u266F': 7,
              r'G\u266D': 7,
              'G': 8,
              r'G#': 9,
              r'Ab': 9,
              r'G\u266F': 9,
              r'A\u266D': 9}

num_to_note = {1: 'C',
                2: "C#",
                3: 'D',
                4: 'D#',
                5: 'E',
                6: 'F',
                7: 'F#',
                8: 'G',
                9: "G#",
                10: 'A',
                11: "A#",
                12: 'B',
                0: 'B'}

# two bellow middle c octave is 0, 'C' = 67 in ascii

# dictionary mapping of open string to octave
octave = 0
guitar_string_octave = {}
string = 6
prev = ord(guitar_tuning[0])
for note in guitar_tuning:
    if ((prev > ord(note)) and (ord(note) >= 67)) or (prev < 67 and ord(note) >=67):
        octave += 1
    guitar_string_octave[string] = octave
    string -= 1
    prev = ord(note)

# string order 123456
guitar_num_tuning = np.array([note_to_num[n] + 12*guitar_string_octave[6-i] for i, n in enumerate(guitar_tuning)])[::-1]

# banjo_string_octave = {5: 3} 
banjo_string_octave = {}
prev = ord(banjo_tuning[0])
string = 3
octave = 2
for note in banjo_tuning:
    if ((prev > ord(note)) and (ord(note) >= 67)) or (prev < 67 and ord(note) >=67):
        octave += 1
    banjo_string_octave[string] = octave
    string -= 1
    prev = ord(note)

# string order 12345
banjo_num_tuning = np.array([note_to_num[n] + 12*banjo_string_octave[len(banjo_tuning)-1-i] for i, n in enumerate(banjo_tuning)])[::-1]
BANJO_MIN = banjo_num_tuning[3]
BANJO_MAX = banjo_num_tuning[0] + 22 # can edit this in incremints of 12 to shift to lower octaves


chord_pattern = r"[A-Ga-g]{1}[#b\u266D\u266F]{,1}"

def get_line_type(line):
    if re.search(r'[a-zA-Z]{4,}', line):
        t = "space"
    elif re.search(r'[|-].*[|]', line):
        t = "notes"
    elif re.search(chord_pattern, line):
        t = "chords"
    else:
        t = "space"
    return t

def _guitar_to_banjo(num_note):
    # find string that's lower and closest to note

    diff = num_note - banjo_num_tuning
    valid_idx = np.where(diff >= 0)[0]
    string = valid_idx[diff[valid_idx].argmin()] 
    fret = num_note - banjo_num_tuning[string]
    return string, str(fret)

def initiliaze_row(line):
    row = ['-'*len(line)] * 5
    # add pipe symbols
    pipes = re.finditer("[|]", line)
    for pipe in pipes:
        index = pipe.span()[0]
        for r in range(5):
            row[r] = row[r][:index] + '|' +row[r][index + 1:]
    return row

def convert_note(note: str, string: int):
    # notes including additional notation suchs a 'h', 'p', etc. Ex: 4p0 is considered one note for the purpose of this conversion
    # find fret positions
    guitar_frets = list(re.finditer(r'\d+', note))
    banjo_strings = []
    banjo_frets = []
    lens = []
    # for each note represented by a fret position, convert to banjo string and banjo fret position
    for guitar_fret in guitar_frets:
        # get the reference number for the note
        num_note = guitar_num_tuning[string] + eval(guitar_fret[0]) + OFF_SET
        # if note too high, shift to lower octave
        if num_note > BANJO_MAX:
            diff = (num_note - BANJO_MAX)
            if diff // 12 == 0:
                transpose = 1
            else: 
                transpose = diff // 12 + 1
            num_note = num_note - transpose * 12
        banjo_string, banjo_fret = _guitar_to_banjo(num_note)
        banjo_strings.append(banjo_string)
        banjo_frets.append(banjo_fret)
        lens.append(len(banjo_fret))
    # check if second note exits and if on same string, if not, return as separate elements
    if len(set(banjo_strings)) > 1:
        # if theres other notation, add in paranthesis so apparent what is lost
        notation = re.search('[^\d]', note)[0] # non-fret notation
        banjo_frets[0] += f'({notation})'
        lens[0] += len(notation)
        notes = list(zip(banjo_strings, banjo_frets, lens))
    # if on the same string or only one fret position
    else:
        for i, fret in enumerate(banjo_frets):
            note = note[:guitar_fret.span()[0]] + str(fret) + note[guitar_fret.span()[1]:]
        notes = [[banjo_string, note, lens[0]]]

    return notes

def convert_chord(chord: str):
    chord = chord[0].upper() + chord[1:]
    num_chord = note_to_num[chord]
    new_num_chord = (num_chord + OFF_SET) % 12
    new_chord = num_to_note[new_num_chord]
    return new_chord

# find lowest and highest note first to determine offset 
lowest = 100
with open(path, 'r') as file:
    string = 0
    for line in file:
        if get_line_type(line) == "notes":
            if string == 6:
                string = 0
            frets = re.findall(r"\d+", line)
            for fret in frets:
                fret = eval(fret)
                note_num = guitar_num_tuning[string] + fret
                if note_num < lowest:
                    lowest = note_num
            string += 1


if USER_OFF_SET:
    OFF_SET = USER_OFF_SET
else:
    OFF_SET = 0
    if lowest < BANJO_MIN:
        OFF_SET = BANJO_MIN - lowest
if ADDITIONAL_OFF_SET:
    OFF_SET += ADDITIONAL_OFF_SET



tabs = []
row = []
string = 0
with open(path, 'r') as file:
    for line in file:
        line = line.rstrip()
        line_type = get_line_type(line)
        if line_type == "notes":
            # if new row in tab, initialize empty row of the 5 strings
            if string == 0:
                row = initiliaze_row(line)
            # only if line has fret values
            if re.search('\d', line):
                # convert and add notes
                # find notes, including additional notation suchs a 'h', 'p', etc.
                notes = re.finditer(r"([^|-]+)", line)
                for elem in notes:
                    note = elem.group(1)
                    note_start = elem.span()[0]
                    # check that there are frets positions to convert
                    if re.search('\d+', note):
                        new_notes = convert_note(note, string)
                        for banjo_string, banjo_fret, note_len in new_notes:
                            note_len = note_len
                            row[banjo_string] = row[banjo_string][:note_start] + banjo_fret + row[banjo_string][note_start + note_len:]  
                            note_start += note_len
            string += 1
            # if finished 6th string on guitar tab, reset to first string and append completed row with converted tabs
            if string == len(guitar_num_tuning):
                string = 0
                tabs.append(row)
        # convert chords above tabs to match tab offset
        elif line_type == "chords":
            if OFF_SET > 0:
                chords = set(re.findall(chord_pattern, line))
                for chord in chords:
                    new_chord = convert_chord(chord)
                    line = line.replace(note, new_chord)
            tabs.append(line)
        else:
            tabs.append(line)
        

with open(out_file, 'w') as out:
    out.write(f"Banjo tuning {banjo_tuning} \n\n")
    for line in tabs:
        if isinstance(line, str):
            out.write(f"{line}\n")
        else:
            for elem in line:
                out.write(f"{elem}\n")
            out.write('\n')
                

        





    