'''
Test the validation scripts


Notes:
adesmaster.xml:
 - "...residuals and related fields may be included in the observation file or stored in a separate file."

ADES_Description.pdf:
 - "...As described above, residuals may be included within an observation ... However, residuals information can also appear as an immediate child of an ades element by including information that allows each of the residuals to be referred to its associated observations."
 - "...at a minimum, the Optical Residuals group must contain the elements [orbProd, orbID] and either [resRA,resDec,selAst,sigRA,sigDec] or [photProd,resMag,selPhot,sigMag] or both"

Questions related to residuals
(1) What are the intended semantic meanings of 'selAst'? Why can't it be boolean?

'''

# Import global
import subprocess
import os,sys

# Define useful paths (for import & subprocess)
master_dir =  os.path.dirname(os.path.dirname(__file__))
test_dir = os.path.join(master_dir, "new_tests")
x2j_py = "xml2json.py"
j2x_py = "json2xml.py"
valsubmit_py = "valsubmit.py"
valgeneral_py = "valgeneral.py"

from ades import valgeneral


'''
General validation of observations with RESIDUALS
'''

# ------------------------
# valgeneral
def test_valgeneral_residual_A():
    """ Test a file that combines optical & residuals """
    # Input file to use for the test
    xmlfile = os.path.join(test_dir, "input/obsResidual.xml")
    # Run the validation script
    result = subprocess.run(f"{valgeneral_py} {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Check the result is as expected
    assert result.stdout.strip() == 'general is OK' ,f'expected `general is OK`, got {result.stdout}'

def test_valgeneral_residual_B():
    """ Test a file that combines optical & residuals  : As for ...A above, but using import"""
    # Input file to use for the test
    xmlfile = os.path.join(test_dir, "input/obsResidual.xml")
    # Clean ...
    if os.path.exists("valgeneral.file"):
        os.remove("valgeneral.file")
    # Run the validation
    valgeneral.valgeneral(xmlfile)
    # Check the result is as expected
    with open("valgeneral.file",'r') as valfile:
        assert valfile.readlines()[0].replace("\n","") == 'general is OK'
    # Clean ...
    if os.path.exists("valgeneral.file"):
        os.remove("valgeneral.file")


def test_valgeneral_residual_C():
    """ Test a file of stand-alone residuals """
    # Input file to use for the test
    xmlfile = os.path.join(test_dir, "input/standaloneResidual.xml")
    # Run the validation script
    result = subprocess.run(f"{valgeneral_py} {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Check the result is as expected
    assert result.stdout.strip() == 'general is OK' ,f'expected `general is OK`, got {result.stdout}'

def test_valgeneral_residual_D():
    """ Test a file of stand-alone residuals : As for ...C above, but using import """
    # Input file to use for the test
    xmlfile = os.path.join(test_dir, "input/standaloneResidual.xml")
    # Clean ...
    if os.path.exists("valgeneral.file"):
        os.remove("valgeneral.file")
    # Run the validation
    valgeneral.valgeneral(xmlfile)
    # Check the result is as expected
    with open("valgeneral.file",'r') as valfile:
        assert valfile.readlines()[0].replace("\n","") == 'general is OK'
    # Clean ...
    if os.path.exists("valgeneral.file"):
        os.remove("valgeneral.file")
