#!/usr/bin/env python3

""" Convert an XML file to a JSON file
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

def xmltojson(xmlfile, jsonfile, xmlencoding="utf-8"):
    """ """
    with open(xmlfile, 'rb') as xf, open(jsonfile, 'w') as jf:
        json.dump(xmltodict.parse(xf.read().decode(xmlencoding), dict_constructor=OrderedDict), jf, indent=4)


if __name__ == '__main__':

    # read command line arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("xmlfile", type=str, help="XML file to convert to JSON")
    parser.add_argument("jsonfile", type=str, help="Path to write JSON data to")
    parser.add_argument("--xmlencoding", default="utf-8", type=str, help="Text encoding for XML input")
    args = parser.parse_args()

    # call function to read xml into a dict and then write to json
    xmltojson(args.xmlfile, args.jsonfile, xmlencoding=args.xmlencoding)
