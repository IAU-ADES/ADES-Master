#!/usr/bin/env python
#
# Python script to create a schema from the
# adesmaster file and use that to validate an
# xml file
#
# Usage:
#   ./valades.py <adesmaster file> <xslt file for schema> <xml file to validate>
#   ./valades.py adesmaster.xml submitxsd.xslt newsubmit.xml
#
# xslt files:               All of thsee transform adesmaster.xml to a schema
#    submitxsd.xslt         creates xsd file to validate submission xml
#    submithumanxsd.xslt    Same but in human-readable form
#    generalxsd.xslt        creates xsd file to validate in general
#    generalhumanxsd.xslt   Same but in human-readable form
#
#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#
import sys

import xmlutility

def valades(args):
    xml_tree = xmlutility.readXML(args[1])
    xslt_tree = xmlutility.readXML(args[2])
    schema = xmlutility.XMLtoSchemaViaXSLT(xml_tree, xslt_tree)

    candidate =xmlutility.readXML(args[3])

    schema.assertValid(candidate)

# ---------------------------------------------------------------
if __name__ == '__main__':
    valades(sys.argv)