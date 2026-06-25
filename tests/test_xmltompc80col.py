"""
Test the conversion from XML to MPC80 col format
Always use high precision, we are not doing low anymore
"""

# Import global
import os
import subprocess
from tempfile import NamedTemporaryFile
import pytest


def _test_doesnt_crash(inpath):
    # To be Windows-friendly, we have to close the file before launching the
    # subprocess. In that case we might as well leave the file on disk if
    # anything goes wrong.
    with NamedTemporaryFile(suffix=".obs", delete=False) as f_output_temp:
        pass

    subprocess.run(
        ["xmltompc80col.py", inpath, f_output_temp.name],
        shell=False,
        check=True,
    )

    assert os.path.exists(f_output_temp.name)
    assert os.stat(f_output_temp.name).st_size != 0
    os.remove(f_output_temp.name)


def _test_output_is_expected(inpath, exppath):
    with open(exppath) as f_expected:
        expected = f_expected.read()

    with NamedTemporaryFile(suffix=".obs") as f_output_temp:
        pass

    subprocess.run(
        ["xmltompc80col.py", inpath, f_output_temp.name],
        shell=False,
        check=True,
    )

    with open(f_output_temp.name) as f_output_temp:
        observed = f_output_temp.read()

    os.remove(f_output_temp.name)

    assert observed == expected


def test_trksub_submission():
    """Test trksub submission"""
    _test_doesnt_crash("input/trksub_sub.xml")


def test_trksub_submission_newregex():
    """After changing the regex in xmltompc80col.py, test trksub submission"""
    _test_doesnt_crash("input/gb_trksub.xml")


def test_trksub_8char():
    """Converting the file even if the trksub is 8-char long"""
    _test_doesnt_crash("input/trksub_8char.xml")


def test_provid_notrksub():
    """Converting the file even if trksub=provid """
    _test_doesnt_crash("input/provid_no_trksub.xml")


def test_band_conversions():
    """Testing some edge cases mapping ADES to obs80 band designations"""
    _test_output_is_expected("input/band_conversions.xml", "expected/band_conversions.obs")


@pytest.mark.xfail
def test_trksub_9char():
    """ The code should stop with an error for any trksubs longer than 8 chars"""
    _test_doesnt_crash("input/trksub_9chars.xml")