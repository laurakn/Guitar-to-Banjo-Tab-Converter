Script to convert standard text-based guitar tabs to the banjo. Only convert to the four main strings to avoid issues with multiple notes on the 5th string. 

Finds the lowest note on the guitar and transposes the song to fit to the given banjo tuning (banjo and guitar tuning can be specified at the top of the script). Notes that are too high for the banjo and shifted down to the first usable octave.

### To run

Change value for

    path

to be the path to the .txt file containing the guitar tabs.

and 

    out_file

to be the name of the file you wish to same the converted tabs too (will save in whichever directory you run the scipt in).

Change values for banjo and guitar tuning as needed. The banjo tuning only is for the first 4 strings. 

Run the script

    python convert_guitar_tabs.py 


Will likely need a small amount of clean up, but is a good baseline.

