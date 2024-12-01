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
from ades import convertutility

def jsontoxml(jsonfile , xmlfile , jsonencoding="utf-8", xmlencoding="utf-8"):
    """ """
    with open(jsonfile, 'r', encoding=jsonencoding) as jf, open(xmlfile, 'w', encoding=xmlencoding) as xf:
        xf.write( xmltodict.unparse( json.load(jf, object_pairs_hook=OrderedDict) , pretty=True, encoding=xmlencoding) )

def main():
    # read command line arguments
    # construct argument parser for a conversion tool
    parser = convertutility.conversion_parser(
      description='Convert ADES JSON to XML', 
    )
    args = parser.parse_args()

    # call function to read xml into a dict and then write to json
    # create callable
    call = lambda i, o : jsontoxml(i, o, jsonencoding=args.input_encoding, xmlencoding=args.output_encoding)
    # call function with filename arguments
    convertutility.call_with_files(call, args)

if __name__ == '__main__':
    main()