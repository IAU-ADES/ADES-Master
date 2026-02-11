'''
Test mpc80coltoxml converting a few obs80col format to xml
with and without the header
'''

#Import global
import pytest
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

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

# ------------------ Testing submission mode ------------------

# Elements that should be omitted when submission=True
_non_submission_elements = {'subFmt', 'precTime', 'precRA', 'precDec'}

def _get_xml_element_tags(xmlfile):
    """Return the set of all element tag names in an XML file."""
    tree = ET.parse(xmlfile)
    return {elem.tag for elem in tree.iter()}

def test_mpc80coltoxml_submission_false_has_non_submit_elements():
    """Default mode (submission=False) should include subFmt, precTime, etc."""
    obsfile = "input/K20Q04A_test.obs"
    xmlfile = "output/K20Q04A_test_submission_false.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    mpc80coltoxml.mpc80coltoxml(obsfile, xmlfile, submission=False)
    assert os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0
    tags = _get_xml_element_tags(xmlfile)
    for elem in _non_submission_elements:
        assert elem in tags, f"{elem} should be present when submission=False"

def test_mpc80coltoxml_submission_true_omits_non_submit_elements():
    """Submission mode (submission=True) should omit subFmt, precTime, etc."""
    obsfile = "input/K20Q04A_test.obs"
    xmlfile = "output/K20Q04A_test_submission_true.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    mpc80coltoxml.mpc80coltoxml(obsfile, xmlfile, submission=True)
    assert os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0
    tags = _get_xml_element_tags(xmlfile)
    for elem in _non_submission_elements:
        assert elem not in tags, f"{elem} should be absent when submission=True"

def test_mpc80coltoxml_submission_true_preserves_core_elements():
    """Submission mode should preserve core observation elements."""
    obsfile = "input/K20Q04A_test.obs"
    xmlfile = "output/K20Q04A_test_submission_core.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    mpc80coltoxml.mpc80coltoxml(obsfile, xmlfile, submission=True)
    assert os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0
    tags = _get_xml_element_tags(xmlfile)
    for elem in ['ra', 'dec', 'mag', 'stn', 'obsTime', 'astCat', 'band']:
        assert elem in tags, f"{elem} should be preserved when submission=True"

def test_mpc80coltoxml_submission_cli():
    """CLI --submission flag should omit non-submission elements."""
    obsfile = "input/K20Q04A_test.obs"
    xmlfile = "output/K20Q04A_test_submission_cli.xml"
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    subprocess.run(
        [sys.executable, "-m", "ades.mpc80coltoxml", "--submission", obsfile, xmlfile],
        check=True,
    )
    assert os.path.exists(xmlfile) and os.stat(xmlfile).st_size != 0
    tags = _get_xml_element_tags(xmlfile)
    for elem in _non_submission_elements:
        assert elem not in tags, f"{elem} should be absent with --submission CLI flag"

