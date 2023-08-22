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
import argparse

import xmlutility

def valades(adesmaster, xsltschema, xmlfile):
    xml_tree = xmlutility.readXML(adesmaster)
    xslt_tree = xmlutility.readXML(xsltschema)
    schema = xmlutility.XMLtoSchemaViaXSLT(xml_tree, xslt_tree)

    candidate = xmlutility.readXML(xmlfile)

    schema.assertValid(candidate)

# ---------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("adesmaster", type=str, help="ADES master xml")
    parser.add_argument("xsltschema", type=str, help="Schema definition file")
    parser.add_argument("xmlfile", type=str, help="XML file to check against schema")

    args = parser.parse_args()

    valades(args.adesmaster, args.xsltschema, args.xmlfile)
