import pytest
import subprocess
import os

master_dir =  os.path.dirname(os.path.dirname(__file__))
test_dir = os.path.join(master_dir, "new_tests")
input_dir = os.path.join(test_dir, "input")
output_dir = os.path.join(test_dir, "output")

conversions = [
    ("xmltojson.py", "319.xml", "319.json"),
    ("jsontoxml.py", "319.json", "319.xml"),
    ("mpc80coltoxml.py", "K20Q04A_test.obs", "K20Q04A_test.xml"),
    ("psvtoxml.py", "2023MQ5.psv", "2023MQ5.xml"),
    ("psvtoxml.py", "2023MQ5.psv", "2023MQ5.xml"),
    ("xmltompc80col.py", "trksub_sub.xml", "trksub_sub.obs"),
]

@pytest.mark.parametrize("executable,in_filename,out_filename", conversions)
def test_pipe_executables(executable, in_filename, out_filename):
    in_path = os.path.join(input_dir, in_filename)
    out_path = os.path.join(output_dir, out_filename)
    with open(in_path, "rb") as in_file, open(out_path, "w") as out_file:
        p = subprocess.run(executable, input=in_file.read(), stdout=out_file)
    
    assert(os.path.exists(out_path) and os.stat(out_path).st_size != 0)

validation = [
    ("valall.py", "obs_v2022.xml", []),
    ("valgeneral.py", "obs_v2022.xml", []),
    ("valsubmit.py", "obs_v2022.xml", []),
    ("validate.py", "obs_v2022.xml", [os.path.join(master_dir, "xsd", "general.xsd")]),
    ("validate.py", "obs.xml", [os.path.join(master_dir, "past_versions", "v2017", "general_v2017.xsd")]),
]

@pytest.mark.parametrize("executable,in_filename,args", validation)
def test_pipe_validation(executable, in_filename, args):
    in_path = os.path.join(input_dir, in_filename)
    with open(in_path, "rb") as in_file:
        p = subprocess.Popen([executable] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(input=in_file.read())

    assert(b'is OK' in out and err == b'')
