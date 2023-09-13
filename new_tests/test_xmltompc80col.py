'''
Test the conversion from XML to MPC80 col format
Always use high precision, we are not doing low anymore
'''
#Import global
import os
import subprocess

def test_trksub_submission():
    infile = "input/trksub_sub.xml"
    outfile = "output/trksub_sub.obs"
    #Remove outfile if there
    if os.path.exists(outfile):
        os.remove(outfile)
    subprocess.run("python3 ../Python/bin/xmltompc80col.py "+infile+" "+outfile, shell=True)
    assert(os.path.exists(outfile) and os.stat(outfile).st_size != 0)
    print("****** Test 1 should pass *******")
