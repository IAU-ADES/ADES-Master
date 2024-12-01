from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.build import build
from setuptools.command.egg_info import egg_info
from setuptools.command.editable_wheel import editable_wheel
from pathlib import Path

def manage_symlinks(action):
    root = Path("Python") / "ades" / "data"
    if not root.exists():
        root.mkdir()

    xml = Path("xml")
    xsd = Path("xsd")
    xslt = Path("xslt")
    for path in [xml, xsd, xslt]:
        install_path = root / path.name
        if action == "create":
            if install_path.exists(): # check if symlink exists; False if the path does not exist
                continue
            install_path.symlink_to(path.absolute())
        elif action == "delete":
            if install_path.exists():
                install_path.unlink()
    
    if action == "delete":
        root.rmdir()

class Build(build):
    def run(self):
        manage_symlinks("create")
        super(Build, self).run()

class EditableWheel(editable_wheel):
    def run(self):
        manage_symlinks("create")
        super(EditableWheel, self).run()

setup(
    cmdclass={
        'build': Build,
        'editable_wheel': EditableWheel,
    },
    use_scm_version=True,
)
