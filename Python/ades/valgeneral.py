#!/usr/bin/env python3
# 
# valgeneral checks the general xml format
# Usage: valgeneral <xml data file>
#    ./valgeneral newgeneral.xml
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
from ades import convertutility

#
# This script validates an xml file against six different
# xsd files generated from xslt.  
#
# Usage:
#   ./valgeneral <xml to validate>
#

#
# adesmaster.xml is the master xml file describing the format
#
def valgeneral(xmlfile):
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
  #
  # read in file to be validataed
  #
  candidate = adesutility.readXML(xmlfile)
  #
  # validate against general schemaxslt files
  # 
  with open("valgeneral.file", "w") as out:
    validate_xml_declaration(xmlfile, out)
    validate_xslt("general", adesutility.schemaxslts['general'], candidate, out)
  
def main():
  # construct argument parser for a validation tool (input only)
  parser = convertutility.input_parser(
    description='Validate XML against general schema', 
    input_help="XML file to check against schema"
  )
  args = parser.parse_args()
  # create callable
  call = lambda i, o : valgeneral(i)
  # call function with filename arguments
  convertutility.call_with_files(call, args)


  
# ------------------------------------------------------------
if __name__ == '__main__':
  main()