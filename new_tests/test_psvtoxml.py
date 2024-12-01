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
