#
# valall checks all six xslt converters
# Usage: valall <xml data file>
#    ./valall newsubmit.xml
#
#
# __future__ imports for Python 3 compliance in Python 2
#
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#


import traceback
import sys
import argparse

import adesutility

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

def valall(xmlfile):
  masterfile = adesutility.adesmaster

  #
  # Six xsd schemas are built, in pairs designed to be favored
  # for machine reading and human reading.  Both items in a pair
  # are functionally identical for validation
  #
  #       machine              human
  #    submitxsd.xslt       submithumanxsd.xslt    -- submissions only
  #    generalxsd.xslt      generalhumanxsd.xslt   -- both
  #
  #
  schemaxslts = adesutility.schemaxslts


  results = {}

  #
  # read in master file
  #
  xml_tree = adesutility.readXML(masterfile)

  #
  # read in file to be validataed from sys.argv[1]
  #
  candidate = adesutility.readXML(xmlfile)

  #
  # validate against all schemaxslt files
  #
  for schemaName in schemaxslts:
    xslt_tree = adesutility.readXML(schemaxslts[schemaName])
    schema = adesutility.XMLtoSchemaViaXSLT(xml_tree, xslt_tree)
    #
    # check the input xml against the generated schema.
    #
    try:
      schema.assertValid(candidate)
      results[schemaName] = None
    except:
      results[schemaName] = traceback.format_exc()

  #
  # now print the results, and the reason for failure if the
  # validation failed.
  #
  for result in sorted(results):
    r = results[result]
    if r:
      print (result, "has failed:")
      print (r)
    else:
      print (result, "is OK")

# --------------------------------------------------------------
if __name__ == '__main__':
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("xmlfile", type=str, help="XML file to check against schema")

  args = parser.parse_args()
  valall(args.xmlfile)