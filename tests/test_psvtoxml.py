'''
Test conversion from psv to xml 
'''

#Import global
import os
import subprocess
import sys

from ades import psvtoxml


#Testing the script from command line
def test_psv_to_xml_conversion():
    psv_infile = "input/2023MQ5.psv"
    xml_outfile = "output/2023MQ5.xml"
    if os.path.exists(xml_outfile):
        os.remove(xml_outfile)
    subprocess.run("psvtoxml.py "+psv_infile+" "+xml_outfile,shell=True)       
    assert(os.path.exists(xml_outfile) and os.stat(xml_outfile).st_size != 0)
    
#Testing the script as a function
def test_psv_to_xml_conversion_routine():
    psv_infile = "input/2023MQ5.psv"
    xml_outfile = "output/2023MQ5.xml"
    if os.path.exists(xml_outfile):
        os.remove(xml_outfile)
    psvtoxml.psvtoxml(psv_infile, xml_outfile)
    assert(os.path.exists(xml_outfile) and os.stat(xml_outfile).st_size != 0)

# Testing that a PSV file with unrecognized header fields (e.g. xObs, yObs, zObs,
# obsCoord) fails with a diagnostic message listing the
# unrecognized fields.
def test_psv_bad_headers_fail():
    psv_infile = "input/fail_headers.psv"
    xml_outfile = "output/fail_headers.xml"
    if os.path.exists(xml_outfile):
        os.remove(xml_outfile)
    result = subprocess.run(
        "psvtoxml.py " + psv_infile + " " + xml_outfile,
        shell=True, capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "unrecognized header field" in result.stdout

# Testing that a PSV file with valid positional header fields (pos1, pos2,
# pos3, ctr, sys) converts successfully to XML.
def test_psv_valid_headers_pass():
    psv_infile = "input/pass_headers.psv"
    xml_outfile = "output/pass_headers.xml"
    if os.path.exists(xml_outfile):
        os.remove(xml_outfile)
    result = subprocess.run(
        "psvtoxml.py " + psv_infile + " " + xml_outfile, shell=True
    )
    assert result.returncode == 0
    assert(os.path.exists(xml_outfile) and os.stat(xml_outfile).st_size != 0)
