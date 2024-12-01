from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.build import build
from pathlib import Path

def create_symlinks():
    root = Path("Python") / "bin" / "data"
    if not root.exists():
        root.mkdir()

    xml = Path("xml")
    xsd = Path("xsd")
    xslt = Path("xslt")
    for path in [xml, xsd, xslt]:
        install_path = root / path.name
        if install_path.is_symlink(): # check if symlink exists; False if the path does not exist
            continue
        install_path.symlink_to(path.absolute())

class Build(build):
    def run(self):
        create_symlinks()
        super(Build, self).run()

setup(
    cmdclass={
        'build': Build,
    }
)