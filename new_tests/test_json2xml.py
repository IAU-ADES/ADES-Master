'''
Test json2xml conversion routine
'''

#Import global
import os
import subprocess

#Test conversion from psv to xml
def test_json2xml_A():
    jsonfile = "input/319.json"
    xmlfile = "output/319.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run(f"python3 ../Python/bin/json2xml.py {jsonfile} {xmlfile}",shell=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)

def test_json2xml_B():
    """ roundtrip test """
    jsonfile = "input/319.json"
    xmlfile = "output/319.xml"
    jsonfile2 = "output/319.json"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    if os.path.exists(jsonfile2):
        os.remove(jsonfile2)

    #Do the roundtrip conversion
    subprocess.run(f"python3 ../Python/bin/json2xml.py {jsonfile} {xmlfile}",shell=True)
    subprocess.run(f"python3 ../Python/bin/xml2json.py {xmlfile} {jsonfile2}",shell=True)
    # Check that the output files exist and are not empty
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)
    assert(os.path.exists(jsonfile2) and os.stat(jsonfile2).st_size != 0)
    #Check that the input & output are identical
    assert(open(jsonfile).read() == open(jsonfile2).read())