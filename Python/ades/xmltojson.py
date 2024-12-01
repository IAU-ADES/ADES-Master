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
from ades import convertutility
import sys


def xmltojson(xmlfile, jsonfile, xmlencoding="utf-8", jsonencoding="utf-8"):
    """ """
    with open(xmlfile, 'rb') as xf, open(jsonfile, 'w', encoding=jsonencoding) as jf:
        json.dump(xmltodict.parse(xf.read().decode(xmlencoding), dict_constructor=OrderedDict), jf, indent=4, ensure_ascii=False)

def main():
    # read command line arguments
    # construct argument parser for a conversion tool
    parser = convertutility.conversion_parser(
        description='Convert ADES XML to JSON', 
    )
    args = parser.parse_args()
    # call function to read xml into a dict and then write to json
    call = lambda i, o : xmltojson(i, o, xmlencoding=args.input_encoding, jsonencoding=args.output_encoding)
    # call function with filename arguments
    convertutility.call_with_files(call, args)


if __name__ == '__main__':
    main()
