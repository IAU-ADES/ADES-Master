#!/usr/bin/env python3
# 
# valsubmit checks the submit xml format
# Usage: valsubmit <xml data file>
#    ./valsubmit newsubmit.xml
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

from ades import adesutility
from ades.valutility import validate_xslt, validate_xml_declaration
import io
from ades import convertutility

#
# This script validates an xml file against six different
# xsd files generated from xslt.  
#
# Usage:
#   ./valsubmit <xml to validate>
#

#
# adesmaster.xml is the master xml file describing the format
#

def valsubmit(xmlfile):
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
  #
  # read in file to be validataed
  #
  
  candidate = adesutility.readXML(xmlfile)
  #
  # validate against submit schemaxslt files
  # 
  with open("valsubmit.file",'w') as out:
    validate_xml_declaration(xmlfile, out)
    validate_xslt("submit", adesutility.schemaxslts['submit'], candidate, out)
  
def main():
  # construct argument parser for a validation tool (input only)
  parser = convertutility.input_parser(
    description='Validate XML against submit schema', 
    input_help="XML file to check against schema",
  )

  args = parser.parse_args()

  # create callable
  call = lambda i, o : valsubmit(i)
  # call function with filename arguments
  convertutility.call_with_files(call, args)


# --------------------------------------------------------
if __name__ == '__main__':
  main()
