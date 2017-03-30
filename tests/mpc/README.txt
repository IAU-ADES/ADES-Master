These files show the results of the current mpc80coltoxml and xmltompc80col conversions.

The .mpc files are in test/
The .mpc.xml and .mpc.xml.mpc file results are in results


For header, newheader and test as <run>

mpc80coltoxml <run>.mpc <run>.mpc.xml  (makes .mpc.xml)
xmltompc80col <run>.mpc.xml <run>.mpc.xml.mpc  (makes .mpc.xml.mpc)

diff <run>.mpc <run>.mpc.xml.mpc shows differences realated mostly to

1) Satellites are not yet processed into xml.  This will be fixed soon.
2) Radar needs some value conversion and won't round-trip yet
3) if mag is present but band is not the band is set to B
4) if band is present but mag is not then band is removed
