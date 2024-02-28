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

#Import global
import os 
import subprocess
import sys

sys.path.append("../Python/bin")
import valgeneral
import valall
import validate
import valsubmit
import adesutility


'''
General validation of observations with RESIDUALS
'''

# ------------------------
# valgeneral
def test_valgeneral_residual_A():
    """ Test a file that combines optical & residuals """
    # Input file to use for the test
    xmlfile = "input/obsResidual.xml"
    # Run the validation script
    result = subprocess.run(f"python3 ../Python/bin/valgeneral.py {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Check the result is as expected
    print('***'*11, result)
    assert result.stdout.strip() == 'general is OK' ,f'expected `general is OK`, got {result.stdout}'

def test_valgeneral_residual_B():
    """ Test a file of stand-alone residuals """
    # Input file to use for the test
    xmlfile = "input/standaloneResidual.xml"
    # Run the validation script
    result = subprocess.run(f"python3 ../Python/bin/valgeneral.py {xmlfile}",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Check the result is as expected
    print('***'*11, result)
    assert result.stdout.strip() == 'general is OK' ,f'expected `general is OK`, got {result.stdout}'

