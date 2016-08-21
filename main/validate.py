#!/usr/bin/env python
#
# Validates an xml file against a schema
#
# Usage:
#  ./validate.py <schema> <xml file>
#
#  ./validate.py submit.xsd  newsubmit.xml
#
import lxml.etree
import sys

#
# Read in the schema
#
with open(sys.argv[1]) as f:
  sd = lxml.etree.parse(f)
  sc = lxml.etree.XMLSchema(sd)

#
# Read in the xml file
#
with open(sys.argv[2]) as f:
  od = lxml.etree.parse(f)


#
# Check for validity -- prints errors on stdout if any are found
#
sc.assertValid(od)
