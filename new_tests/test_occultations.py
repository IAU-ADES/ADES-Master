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
    subprocess.run("psvtoxml.py "+psvfile+" "+xmlfile,shell=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)
    
#Test conversion from xml to obs80
def test_xml_to_obs80():
    xmlfile = "input/319.xml"
    obsfile = "output/319.obs"
    if os.path.exists(obsfile):
        os.remove(obsfile)
    subprocess.run("xmltompc80col.py "+xmlfile+" "+obsfile,shell=True)
    assert(os.path.exists(obsfile) and (os.stat(obsfile).st_size != 0 and os.stat(obsfile).st_size > 1190))