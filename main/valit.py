#!/usr/bin/env python
#
# Python script to create a schema from the
# adesmaster file and use that to validate an
# xml file
#
# Usage:
#   ./valit.py <adesmaster file> <xslt file for schema> <xml file to validate>
#   ./valit.py adesmaster.py submitxsd.xslt newsubmit.xml
#
import lxml.etree
import sys

with open(sys.argv[1]) as xml:
   xml_tree = lxml.etree.parse(xml)

with open(sys.argv[2]) as xslt:
   xslt_tree = lxml.etree.parse(xslt)
   xslt_transform = lxml.etree.XSLT(xslt_tree)
   schema = xslt_transform(xml_tree)
   ## 
   ##  extra stutter step if we use a text-based 
   ##  schema xslt such as submittestxsd.xslt
   ## 
   st = str(schema)             # into text
   schema = lxml.etree.XML(st)  # out again into non-text xml
 
   sc = lxml.etree.XMLSchema(schema)

with open(sys.argv[3]) as f:
  od = lxml.etree.parse(f)

sc.assertValid(od)
