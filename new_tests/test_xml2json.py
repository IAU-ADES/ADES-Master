'''
Test xml2json conversion routine
'''

#Import global
import os
import subprocess
import re

#Test conversion from psv to xml
def test_xml2json_A():
    xmlfile = "input/319.xml"
    jsonfile = "output/319.json"
    if os.path.exists(jsonfile):
        os.remove(jsonfile)
    subprocess.run(f"python3 ../Python/bin/xml2json.py {xmlfile} {jsonfile}",shell=True)
    assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0)
    
def test_xml2json_B():
    """ roundtrip test """
    xmlfile = "input/319.xml"
    jsonfile = "output/319.json"
    xmlfile2 = "output/319.xml"
    if os.path.exists(jsonfile):
        os.remove(jsonfile)
    if os.path.exists(xmlfile2):
        os.remove(xmlfile2)

    #Do the roundtrip conversion
    subprocess.run(f"python3 ../Python/bin/xml2json.py {xmlfile} {jsonfile}",shell=True)
    subprocess.run(f"python3 ../Python/bin/json2xml.py {jsonfile} {xmlfile2}",shell=True)

    # Check that the output files exist and are not empty
    assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0)
    assert(os.path.exists(xmlfile2) and os.stat(xmlfile2).st_size != 0)

    # Check that before & after are both VALID
    # NB I am doing this because the output XML is not EXACTLY the same as the input XML:...
    #  - some of the formatting changes (e.g. single versus double quotes, different whitespace, ...
    #  - As such, it's easier just to check that the output XML remains valid
    result = subprocess.run(f"python3 ../Python/bin/valsubmit.py {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert result.stdout.strip() == 'submit is OK' ,f'expected `submit is OK`, got {result.stdout}'
    result = subprocess.run(f"python3 ../Python/bin/valsubmit.py {xmlfile2}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert result.stdout.strip() == 'submit is OK' ,f'expected `submit is OK`, got {result.stdout}'

def test_xml2json_C():
    """ roundtrip test on XML file(s) with residuals """
    for xmlfile in ["input/obsResidual.xml","input/standaloneResidual.xml"]:
        jsonfile = "output/resid.json"
        xmlfile2 = "output/resid.xml"
        if os.path.exists(jsonfile):
            os.remove(jsonfile)
        if os.path.exists(xmlfile2):
            os.remove(xmlfile2)

        #Do the roundtrip conversion
        subprocess.run(f"python3 ../Python/bin/xml2json.py {xmlfile} {jsonfile}",shell=True)
        subprocess.run(f"python3 ../Python/bin/json2xml.py {jsonfile} {xmlfile2}",shell=True)

        # Check that the output files exist and are not empty
        assert(os.path.exists(jsonfile) and os.stat(jsonfile).st_size != 0)
        assert(os.path.exists(xmlfile2) and os.stat(xmlfile2).st_size != 0)

        # Check that before & after are both VALID
        # NB I am doing this because the output XML is not EXACTLY the same as the input XML:...
        #  - some of the formatting changes (e.g. single versus double quotes, different whitespace, ...
        #  - As such, it's easier just to check that the output XML remains valid
        result = subprocess.run(f"python3 ../Python/bin/valgeneral.py {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.stdout.strip() == 'general is OK' ,f'{xmlfile}:expected `submit is OK`, got {result.stdout}'
        result = subprocess.run(f"python3 ../Python/bin/valgeneral.py {xmlfile2}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.stdout.strip() == 'general is OK' ,f'{xmlfile2}:expected `submit is OK`, got {result.stdout}'
