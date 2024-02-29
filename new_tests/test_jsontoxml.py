'''
Test json2xml conversion routine
'''

# Import global
import os, sys
import subprocess

# Define useful paths (for import & subprocess)
master_dir =  os.path.dirname(os.path.dirname(__file__))
bin_dir = os.path.join(master_dir, "Python/bin")
test_dir = os.path.join(master_dir, "new_tests")
x2j_py = os.path.join(bin_dir, "xmltojson.py")
j2x_py = os.path.join(bin_dir, "jsontoxml.py")
valsubmit_py = os.path.join(bin_dir, "valsubmit.py")
valgeneral_py = os.path.join(bin_dir, "valgeneral.py")

# Import local
sys.path.append( bin_dir )
import jsontoxml

#Test conversion from psv to xml
def test_json2xml_A():
    jsonfile = os.path.join(test_dir, "input/319.json")
    xmlfile = os.path.join(test_dir, "output/319.xml")
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run(f"python3 {j2x_py} {jsonfile} {xmlfile}",shell=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)

def test_json2xml_B():
    """ roundtrip test """
    jsonfile = os.path.join(test_dir, "input/319.json")
    xmlfile = os.path.join(test_dir, "output/319.xml")
    jsonfile2 = os.path.join(test_dir, "output/319.json")
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    if os.path.exists(jsonfile2):
        os.remove(jsonfile2)

    #Do the roundtrip conversion
    subprocess.run(f"python3 {j2x_py} {jsonfile} {xmlfile}",shell=True)
    subprocess.run(f"python3 {x2j_py} {xmlfile} {jsonfile2}",shell=True)
    # Check that the output files exist and are not empty
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)
    assert(os.path.exists(jsonfile2) and os.stat(jsonfile2).st_size != 0)
    #Check that the input & output are identical
    assert(open(jsonfile).read() == open(jsonfile2).read())


def test_json2xml_C():
    jsonfile = os.path.join(test_dir, "input/319.json")
    xmlfile = os.path.join(test_dir, "output/319.xml")

    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    jsontoxml.jsontoxml(jsonfile, xmlfile)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)
