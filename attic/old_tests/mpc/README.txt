These files show the results of the current mpc80coltoxml and xmltompc80col conversions.

The .mpc files are in test/
The .mpc.xml and .mpc.xml.mpc file results are in results


For header, newheader and test as <run>

mpc80coltoxml <run>.mpc <run>.mpc.xml  (makes .mpc.xml)
xmltompc80col <run>.mpc.xml <run>.mpc.xml.mpc  (makes .mpc.xml.mpc)

diff <run>.mpc <run>.mpc.xml.mpc shows differences realated mostly to

1) if mag is present but band is not the band is set to B
2) if band is present but mag is not then band is removed


As of Jan 16, 2018, this handles the astCat codes properly,
translating the single-character codes into and out of the
IAU-ADES 2017 codes.  The test.mpc file demonstrates this.

As of Aug 20, 2019, this handles the extended minor planet
permID's  (above 619999; ~000z format).  This only affects
mpc80coltoxml and xmltompc80col; the xmltopsv allows
and still allows arbitrary positive integers for the ID
