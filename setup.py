from setuptools import setup
from setuptools.command.build import build
from setuptools.command.editable_wheel import editable_wheel
from pathlib import Path
import shutil

def manage_datadir(action):
    root = Path("Python") / "ades" / "data"
    if not root.exists():
        root.mkdir()

    xml = Path("xml")
    xsd = Path("xsd")
    xslt = Path("xslt")
    for path in [xml, xsd, xslt]:
        install_path = root / path.name
        if action == "create":
            if install_path.exists(): # check if directory exists; False if the path does not exist
                continue
            shutil.copytree(path.absolute(), install_path)
        elif action == "delete":
            if install_path.exists():
                shutil.rmtree(install_path)
    
    if action == "delete":
        root.rmdir()

class Build(build):
    def run(self):
        manage_datadir("create")
        super(Build, self).run()

class EditableWheel(editable_wheel):
    def run(self):
        manage_datadir("create")
        super(EditableWheel, self).run()

setup(
    cmdclass={
        'build': Build,
        'editable_wheel': EditableWheel,
    },
    use_scm_version=True,
)
