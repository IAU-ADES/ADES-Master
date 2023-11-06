'''
Test the validation scripts
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
General validation, which also includes the files generated by the MPC 
that could in principle have additional fields
'''

# ------------------------
# valgeneral
def test_valgeneral():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("validation.file"):
        os.remove("validation.file")
    subprocess.run("python3 ../Python/bin/valgeneral.py "+xmlfile+"> validation.file",shell=True)
    with open("validation.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if val == 'general is OK':
            assert(True)
        else:
            assert(False)
            
def test_valgeneral_routine():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("valgeneral.file"):
        os.remove("valgeneral.file")
    valgeneral.valgeneral(xmlfile)
    with open("valgeneral.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if val == 'general is OK':
            assert(True)
        else:
            assert(False)
# ------------------------
# valall
def test_valall():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("valall.file"):
        os.remove("valall.file")
    subprocess.run("python3 ../Python/bin/valall.py "+xmlfile+"> valall.file",shell=True)
    with open("valall.file",'r') as valfile:
        lines = [line.strip() for line in valfile.readlines()]
        assert(all([f"{schema_name} is OK" in lines for schema_name in sorted(adesutility.schemaxslts.keys())]))
        # for line in valfile.readlines()

        #     if line.strip() in :

        # val = valfile.readlines()[0].replace("\n","")

        # if val == 'general is OK':
        #     assert(True)
        # else:
        #     assert(False)

def test_valall_routine():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("valall.file"):
        os.remove("valall.file")
    valall.valall(xmlfile)
    with open("valall.file",'r') as valfile:
        lines = [line.strip() for line in valfile.readlines()]
        assert(all([f"{schema_name} is OK" in lines for schema_name in adesutility.schemaxslts.keys()]))
            
# ------------------------
# validate

#Validate v2022 with general.xsd            
def test_validate_v2022():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("validation.file"):
        os.remove("validation.file")
    subprocess.run("python3 ../Python/bin/validate.py ../xsd/general.xsd "+xmlfile+"> validation.file",shell=True)
    with open("validation.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if 'is OK' in val:
            assert(True)
        else:
            assert(False)

#Validate v2022 with general.xsd            
def test_validate_v2022_routine():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("validate.file"):
        os.remove("validate.file")
    validate.validate("../xsd/general.xsd", xmlfile)
    with open("validate.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if 'is OK' in val:
            assert(True)
        else:
            assert(False)

#Validate past version (v2017) with general.xsd            
def test_validate_v2017():
    xmlfile = "input/obs.xml"
    if os.path.exists("validation.file"):
        os.remove("validation.file")
    subprocess.run("python3 ../Python/bin/validate.py ../past_versions/v2017/general_v2017.xsd "+xmlfile+"> validation.file",shell=True)
    with open("validation.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if 'is OK' in val:
            assert(True)
        else:
            assert(False)

#Validate past version (v2017) with general.xsd            
def test_validate_v2017_routine():
    xmlfile = "input/obs.xml"
    if os.path.exists("validate.file"):
        os.remove("validate.file")
    validate.validate('../past_versions/v2017/general_v2017.xsd', xmlfile)
    with open("validate.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if 'is OK' in val:
            assert(True)
        else:
            assert(False)

# ------------------------

'''
Validation for the submitters, e.g. some fields cannot be present 
'''
def test_val_submit():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("validation.file"):
        os.remove("validation.file")
    subprocess.run("python3 ../Python/bin/valsubmit.py "+xmlfile+"> validation.file",shell=True)
    with open("validation.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if 'is OK' in val:
            assert(True)
        else:
            assert(False)

def test_val_submit_routine():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("valsubmit.file"):
        os.remove("valsubmit.file")
    valsubmit.valsubmit(xmlfile)
    with open("valsubmit.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if 'is OK' in val:
            assert(True)
        else:
            assert(False)    
