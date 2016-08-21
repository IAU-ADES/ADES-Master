#!/usr/bin/env python
#
# Simple python script to transform an xml file via xslt.
# This script uses the lxml module which is not shipped
# with python and must be installed separately
#
# Usage:  
#   ./xit.py <xml file> <xslt file>  > <output file>
#
#   ./xit.y adesmaster.xml submitxsd.xslt > xubmit.xsd
#    
#
#
import lxml.etree
import sys

#
# read in input xml file
#
with open(sys.argv[1]) as xml:
   xml_tree = lxml.etree.parse(xml)

#
# read in xslt file and create transformer
#
with open(sys.argv[2]) as xslt:
   xslt_tree = lxml.etree.parse(xslt)

xslt_transform = lxml.etree.XSLT(xslt_tree)

#
# create transformed output and print it on stdout
#
transformed = xslt_transform(xml_tree)
print (str(transformed))

