import pytest
import packUtil

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
    "J95A010": "1995 A1",
    "J94P01b": "1994 P1-B",
    "J94P010": "1994 P1",
    "K48X130": "2048 X13",
    "K33L89c": "2033 L89-C",
    "K88AA30": "2088 A103",
    "K14A00A": "2014 AA",
    "K14B01A": "2014 BA1",
    "K14Aa0A": "2014 AA360",
    "K14Az9Q": "2014 AQ619",
    "J97B06A": "1997 BA6",
    "PLS4007": "4007 P-L",
    "T1S4568": "4568 T-1",
    "T2S1238": "1238 T-2",
    "T3S1438": "1438 T-3",
}

@pytest.mark.parametrize("packed,unpacked", provID_examples.items())
def test_unpack_provID_examples(packed, unpacked):
    _, provID, _ = packUtil.unpackPackedID(" "*5 + packed)
    assert(provID == unpacked)


@pytest.mark.parametrize("packed,unpacked", provID_examples.items())
def test_pack_provID_examples(packed, unpacked):
    packedID = packUtil.packTupleID((None, unpacked, None))
    provID = packedID[5:]
    assert(provID == packed)

