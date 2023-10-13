'''
Test occultations 
'''

#Import global
import os
import subprocess

#Test conversion from psv to xml
def test_psv_to_xml():
    psvfile = "input/319.psv"
    xmlfile = "output/319.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run("python3 ../Python/bin/psvtoxml.py "+psvfile+" "+xmlfile,shell=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)