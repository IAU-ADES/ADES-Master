'''
Test mpc80coltoxml converting a few obs80col format to xml
with and without the header
'''

#Import global
import pytest
import os
import subprocess
import sys

from ades import mpc80coltoxml

# ------------------ Testing without the header ------------------
#Testing file without the header - this test should pass
def test_mpc80coltoxml_mpcfile():
    obsfile = "input/K20Q04A_test.obs"
    xmlfile = "output/K20Q04A_test.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run("mpc80coltoxml.py "+obsfile+" "+xmlfile,shell=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)

def test_mpc80coltoxml_mpcfile_routine():
    obsfile = "input/K20Q04A_test.obs"
    xmlfile = "output/K20Q04A_test.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    mpc80coltoxml.mpc80coltoxml(obsfile, xmlfile, nosplit=False)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)

# ------------------ Testing with the header ------------------    
#Testing file with the header - this test should pass
def test_mpc80coltoxml_submitted_nosplit():
    obsfile = "input/85_test.obs"
    xmlfile = "output/85_test_nosplit.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run("mpc80coltoxml.py --nosplit "+obsfile+" "+xmlfile,shell=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)
    
def test_mpc80coltoxml_submitted_nosplit_routine():
    obsfile = "input/85_test.obs"
    xmlfile = "output/85_test_nosplit.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    mpc80coltoxml.mpc80coltoxml(obsfile,xmlfile, nosplit=True)
    assert(os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0)

# ------------------ Testing with the header without --nosplit ------------------    
#Testing file with the header, but without using --nosplit -- this test does not pass
def test_mpc80coltoxml_submitted_split():
    obsfile = "input/85_test.obs"
    xmlfile = "output/85_test_split.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run("mpc80coltoxml.py "+obsfile+" "+xmlfile,shell=True)
    print('******* Test 3 should fail ********')
    assert(os.path.exists(xmlfile))
    
def test_mpc80coltoxml_submitted_split_routine():
    obsfile = "input/85_test.obs"
    xmlfile = "output/85_test_split.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    mpc80coltoxml.mpc80coltoxml(obsfile, xmlfile, nosplit=False)
    assert(os.path.exists(xmlfile))

