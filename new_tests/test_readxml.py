'''
Test reading XML file 
'''

#Import global
import os
import subprocess

def test_read_xml():
    infile = "input/trksub_sub.xml"
    outfile = "output/read_xml_out.txt"
    subprocess.run("python3 ../Python/bin/readxmlpy.py "+infile+"> "+outfile,shell=True)
    assert(os.path.exists(outfile) and os.stat(outfile).st_size != 0)
    print('******* Test 1 should pass ********\n')