#!/usr/bin/env python
import lxml.etree
import traceback
import sys

#
# This scirpt uses the lxml module which is not shipped with
# python.
#
# This script validates an xml file against six different
# xsd files generated from xslt.  
#
# Usage:
#   ./valall.py <xml to validate>
#

#
# adesmaster.xml is the master xml file describing the format
#
masterfile = "adesmaster.xml"

#
# Six xsd schemas are built, in pairs designed to be favored
# for machine reading and human reading.  Both items in a pair
# are functionally identical for validation
#
#       machine              human
#    submitxsd.xslt       submithumanxsd.xslt    -- submissions only
#    distribxsd.xslt      distribhumanxsd.xslt   -- distributions only
#    generalxsd.xslt      generalhumanxsd.xslt   -- both
#
#
schemaxslts = ['submitxsd.xslt', 'distribxsd.xslt', 'generalxsd.xslt', 
      'submithumanxsd.xslt', 'distribhumanxsd.xslt', 'generalhumanxsd.xslt']


results = {}

#
# read in master file 
#
with open(masterfile) as masterxml:
   xml_tree = lxml.etree.parse(masterxml)

#
# read in file to be validataed from sys.argv[1]
#
with open(sys.argv[1]) as candidatefile:
  candidate = lxml.etree.parse(candidatefile)

#
# validate against all schemaxslt files
# 
for schemaxslt in schemaxslts:
  with open(schemaxslt) as xslt:
     xslt_tree = lxml.etree.parse(xslt)
  xslt_transform = lxml.etree.XSLT(xslt_tree)
  schema = xslt_transform(xml_tree)

  ## 
  ##  The human-readable xslt files do not generate xml trees
  ##  but rather text trees.  The text trees are the text of 
  ##  a valid xsd but can't bu used directly by XMLSchema.
  ##
  ##  So convert the schema to a string and back to XML
  ## 
  st = str(schema)
  schema = lxml.etree.XML(st)
  ##
  ## Now schema is an xml tree and not sometimes a text tree
  ##
  sc = lxml.etree.XMLSchema(schema)

  #
  # check the input xml against the generated schema.
  #
  try:
    sc.assertValid(candidate)
    results[schemaxslt] = None
  except:  
    results[schemaxslt] = traceback.format_exc()

#
# now print the results, and the reason for failure if the
# validation failed.  
#
for result in results:
  r = results[result]
  if r:
    print result, "has failed:"
    print r
  else:
    print result, "is OK"


      
