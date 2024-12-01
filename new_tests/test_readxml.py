'''
Test reading XML file 
'''

#Import global
import os
import subprocess
import sys
from contextlib import redirect_stdout

from ades import readxmlpy

#Test the script from command line
def test_read_xml():
    infile = "input/trksub_sub.xml"
    outfile = "output/read_xml_out.txt"
    subprocess.run("readxmlpy.py "+infile+"> "+outfile,shell=True)
    assert(os.path.exists(outfile) and os.stat(outfile).st_size != 0)

#Test the script as a routine
def test_read_xml_routine():
    infile = "input/trksub_sub.xml"
    outfile = "output/read_xml_out.txt"
    with open(outfile, "w") as f:
        with redirect_stdout(f):
            readxmlpy.readxmlpy(infile)
        
    assert(os.path.exists(outfile) and os.stat(outfile).st_size != 0)

    
