'''
Test conversion from psv to xml 
'''

#Import global
import os
import subprocess
import sys

from ades import xmltopsv

#Testing main
def test_psv_to_xml_conversion():
    xml_infile = "input/obs.xml"
    psv_outfile = "output/obs.psv"
    if os.path.exists(psv_outfile):
        os.remove(psv_outfile)
    subprocess.run("xmltopsv.py "+xml_infile+" "+psv_outfile,shell=True)       
    assert(os.path.exists(psv_outfile) and os.stat(psv_outfile).st_size != 0)

#Testing routine call
def test_psv_to_xml_conversion_routine():
    xml_infile = "input/obs.xml"
    psv_outfile = "output/obs.psv"
    if os.path.exists(psv_outfile):
        os.remove(psv_outfile)
    xmltopsv.xmltopsv(xml_infile,psv_outfile)     
    assert(os.path.exists(psv_outfile) and os.stat(psv_outfile).st_size != 0)
