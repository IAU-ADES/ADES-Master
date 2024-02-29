#!/usr/bin/env python3

""" Convert a JSON file to an XML file
    Does *NOT* check for validity of either the JSON or the XML files
"""
# __future__ imports for Python 3 compliance in Python 2
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
# Standard Imports
import xmltodict
import json
import argparse
from collections import OrderedDict  # Only necessary for python < 3.7

def jsontoxml(jsonfile , xmlfile , jsonencoding="utf-8"):
    """ """
    with open(jsonfile, 'r', encoding=jsonencoding) as jf, open(xmlfile, 'w') as xf:
        xf.write( xmltodict.unparse( json.load(jf, object_pairs_hook=OrderedDict) , pretty=True) )

if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("jsonfile", type=str, help="JSON file to convert to XML")
    parser.add_argument("xmlfile", type=str, help="Path to write XML data to")
    parser.add_argument("--jsonencoding", default="utf-8", type=str, help="Text encoding for JSON input")
    args = parser.parse_args()

    # call function to read xml into a dict and then write to json
    jsontoxml(args.jsonfile, args.xmlfile, jsonencoding=args.jsonencoding)