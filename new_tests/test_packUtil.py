import pytest
from ades import packUtil
import sys

provID_examples = {
    "J95X00A": "1995 XA",
    "J95X01L": "1995 XL1",
    "J95F13B": "1995 FB13",
    "J98SA8Q": "1998 SQ108",
    "J98SC7V": "1998 SV127",
    "J98SG2S": "1998 SS162",
    "K99AJ3Z": "2099 AZ193",
    "K08Aa0A": "2008 AA360",
    "K07Tf8A": "2007 TA418",
    "PLS2040": "2040 P-L",
    "T1S3138": "3138 T-1",
    "T2S1010": "1010 T-2",
    "T3S4101": "4101 T-3",
    "K26Cz9Z": "2026 CZ619",
    "_QC0000": "2026 CA620",
    "_QC0aEM": "2026 CZ6190",
    "_QCzzzz": "2026 CL591673",
    "K14A00A": "2014 AA",
    "K14B01A": "2014 BA1",
    "K14Aa0A": "2014 AA360",
    "K14Az9Q": "2014 AQ619",
    "J97B06A": "1997 BA6",
    "PLS4007": "4007 P-L",
    "T1S4568": "4568 T-1",
    "T2S1238": "1238 T-2",
    "T3S1438": "1438 T-3"
}

comet_provID_examples = {
    "CJ95A010": "C/1995 A1",
    "XJ94P01b": "X/1994 P1-B",
    "DJ94P010": "D/1994 P1",
    "AK48X130": "A/2048 X13",
    "CK33L89c": "C/2033 L89-C",
    "PK88AA30": "P/2088 A103"
}
    
permID_examples = {
    "03202": "3202",
    "50000": "50000",
    "A0345": "100345",
    "a0017": "360017",
    "K3289": "203289",
    "~0000": "620000",
    "~000z": "620061",
    "~AZaz": "3140113",
    "~zzzz": "15396335"
}


@pytest.mark.parametrize("packed_provID,unpacked_provID", provID_examples.items())
def test_unpack_provID_examples(packed_provID, unpacked_provID):
    _, provID, _ = packUtil.unpackPackedID(" "*5 + packed_provID)
    assert(provID == unpacked_provID)


@pytest.mark.parametrize("packed_provID,unpacked_provID", provID_examples.items())
def test_pack_provID_examples(packed_provID, unpacked_provID):
    packedID = packUtil.packTupleID((None, unpacked_provID, None))
    packed_provID = packedID[5:]
    assert(packed_provID == packed_provID)

@pytest.mark.parametrize("packed_provID,unpacked_provID", comet_provID_examples.items())
def test_unpack_comet_provID_examples(packed_provID, unpacked_provID):
    _, provID, _ = packUtil.unpackPackedID(" "*4 + packed_provID)
    assert(provID == unpacked_provID)


@pytest.mark.parametrize("packed_provID,unpacked_provID", comet_provID_examples.items())
def test_pack_comet_provID_examples(packed_provID, unpacked_provID):
    packedID = packUtil.packTupleID((None, unpacked_provID, None))
    packed_provID = packedID[4:]
    assert(packed_provID == packed_provID)

@pytest.mark.parametrize("packed_permID,unpacked_permID", permID_examples.items())
def test_unpack_permID_examples(packed_permID, unpacked_permID):
    permID, _, _ = packUtil.unpackPackedID(packed_permID + " "*7)
    assert(permID == unpacked_permID)


@pytest.mark.parametrize("packed_permID,unpacked_permID", permID_examples.items())
def test_pack_permID_examples(packed_permID, unpacked_permID):
    packedID = packUtil.packTupleID((unpacked_permID, None, None))
    packed_permID = packedID[:5]
    assert(packed_permID == packed_permID)
