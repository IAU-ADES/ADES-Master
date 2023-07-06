'''
Test the file validation
'''

#Import global
import os 
import subprocess

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
            
def test_valall():
    xmlfile = "input/obs_v2022.xml"
    if os.path.exists("validation.file"):
        os.remove("validation.file")
    subprocess.run("python3 ../Python/bin/valall.py "+xmlfile+"> validation.file",shell=True)
    with open("validation.file",'r') as valfile:
        val = valfile.readlines()[0].replace("\n","")
        if val == 'general is OK':
            assert(True)
        else:
            assert(False)

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