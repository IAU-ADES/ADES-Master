'''
Test reading XML file 
'''

#Import global
import os
import subprocess
import sys

sys.path.append("../Python/bin")
import readxmlpy

#Test the script from command line
def test_read_xml():
    infile = "input/trksub_sub.xml"
    outfile = "output/read_xml_out.txt"
    subprocess.run("python3 ../Python/bin/readxmlpy.py "+infile+"> "+outfile,shell=True)
    assert(os.path.exists(outfile) and os.stat(outfile).st_size != 0)

#Test the script as a routine
def test_read_xml():
    infile = "input/trksub_sub.xml"
    outfile = "output/read_xml_out.txt"
    readxmlpy.readxmlpy(['',infile,outfile])
    assert(os.path.exists(outfile) and os.stat(outfile).st_size != 0)

    
