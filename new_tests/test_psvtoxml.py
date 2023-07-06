'''
Test conversion from psv to xml 
'''

#Import global
import os
import subprocess

def test_psv_to_xml_conversion():
    psv_infile = "input/2023MQ5.psv"
    xml_outfile = "output/2023MQ5.xml"
    if os.path.exists(xml_outfile):
        os.remove(xml_outfile)
    subprocess.run("python3 ../Python/bin/psvtoxml.py "+psv_infile+" "+xml_outfile,shell=True)       
    assert(os.path.exists(xml_outfile) and os.stat(xml_outfile).st_size != 0)
    print('******* Test 1 should pass *******')