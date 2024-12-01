from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.build import build
from pathlib import Path

def manage_symlinks(action):
    root = Path("Python") / "bin" / "data"
    if not root.exists():
        root.mkdir()

    xml = Path("xml")
    xsd = Path("xsd")
    xslt = Path("xslt")
    for path in [xml, xsd, xslt]:
        install_path = root / path.name
        if action == "create":
            if install_path.is_symlink(): # check if symlink exists; False if the path does not exist
                continue
            install_path.symlink_to(path.absolute())
        elif action == "delete":
            if install_path.is_symlink():
                install_path.unlink()
    
    if action == "delete":
        root.rmdir()

class Build(build):
    def run(self):
        manage_symlinks("create")
        super(Build, self).run()
        manage_symlinks("delete")

setup(
    cmdclass={
        'build': Build,
    },
    use_scm_version=True,
)
