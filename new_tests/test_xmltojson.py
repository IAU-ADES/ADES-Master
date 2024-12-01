'''
Test xml2json conversion routine
'''

# Import global
import os, sys
import subprocess

# Define useful paths (for import & subprocess)
master_dir =  os.path.dirname(os.path.dirname(__file__))
test_dir = os.path.join(master_dir, "new_tests")
x2j_py = "xmltojson.py"
j2x_py = "jsontoxml.py"
valsubmit_py = "valsubmit.py"
valgeneral_py = "valgeneral.py"

from ades import xmltojson

#Test conversion from psv to xml
def test_xml2json_A():
    xmlfile = os.path.join(test_dir, "input/319.xml")
    jsonfile = os.path.join(test_dir, "output/319.json")
    if os.path.exists(jsonfile):
        os.remove(jsonfile)
    subprocess.run(f"{x2j_py} {xmlfile} {jsonfile}",shell=True)
    assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0)
    
def test_xml2json_B():
    """ roundtrip test """
    xmlfile = os.path.join(test_dir, "input/319.xml")
    jsonfile = os.path.join(test_dir, "output/319.json")
    xmlfile2 = os.path.join(test_dir, "output/319.xml")
    if os.path.exists(jsonfile):
        os.remove(jsonfile)
    if os.path.exists(xmlfile2):
        os.remove(xmlfile2)

    #Do the roundtrip conversion
    subprocess.run(f"{x2j_py} {xmlfile} {jsonfile}",shell=True)
    subprocess.run(f"{j2x_py} {jsonfile} {xmlfile2}",shell=True)

    # Check that the output files exist and are not empty
    assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0)
    assert(os.path.exists(xmlfile2) and os.stat(xmlfile2).st_size != 0)

    # Check that before & after are both VALID
    # NB I am doing this because the output XML is not EXACTLY the same as the input XML:...
    #  - some of the formatting changes (e.g. single versus double quotes, different whitespace, ...
    #  - As such, it's easier just to check that the output XML remains valid
    result = subprocess.run(f"{valsubmit_py} {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert result.stdout.strip() == 'submit is OK' ,f'expected `submit is OK`, got {result.stdout}'
    result = subprocess.run(f"{valsubmit_py} {xmlfile2}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert result.stdout.strip() == 'submit is OK' ,f'expected `submit is OK`, got {result.stdout}'

def test_xml2json_C():
    """ roundtrip test on XML file(s) with residuals """
    for xmlfile in [
            os.path.join(test_dir, "input/obsResidual.xml"),
            os.path.join(test_dir, "input/standaloneResidual.xml")]:
        jsonfile = os.path.join(test_dir, "output/resid.json")
        xmlfile2 = os.path.join(test_dir, "output/resid.xml")
        if os.path.exists(jsonfile):
            os.remove(jsonfile)
        if os.path.exists(xmlfile2):
            os.remove(xmlfile2)

        #Do the roundtrip conversion
        subprocess.run(f"{x2j_py} {xmlfile} {jsonfile}",shell=True)
        subprocess.run(f"{j2x_py} {jsonfile} {xmlfile2}",shell=True)

        # Check that the output files exist and are not empty
        assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0), f'problem with {jsonfile}'
        assert(os.path.exists(xmlfile2) and os.stat(xmlfile2).st_size != 0), f'problem with {xmlfile2}'

        # Check that before & after are both VALID
        # NB I am doing this because the output XML is not EXACTLY the same as the input XML:...
        #  - some of the formatting changes (e.g. single versus double quotes, different whitespace, ...
        #  - As such, it's easier just to check that the output XML remains valid
        result = subprocess.run(f"{valgeneral_py} {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.stdout.strip() == 'general is OK' ,f'{xmlfile}:expected `submit is OK`, got {result.stdout}'
        result = subprocess.run(f"{valgeneral_py} {xmlfile2}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.stdout.strip() == 'general is OK' ,f'{xmlfile2}:expected `submit is OK`, got {result.stdout}'

def test_xml2json_D():
    """ Calling via import (rather than from command-line) """
    xmlfile = os.path.join(test_dir, "input/319.xml")
    jsonfile = os.path.join(test_dir, "output/319.json")
    if os.path.exists(jsonfile):
        os.remove(jsonfile)
    xmltojson.xmltojson(xmlfile, jsonfile)
    assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0)
