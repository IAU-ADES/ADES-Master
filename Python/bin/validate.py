# Validates an xml file against a schema
#
# Usage:
#  ./validate.py <schema> <xml file>
#
#  ./validate.py submit.xsd  newsubmit.xml
#
#
# This program uses xmlutility but shows how to 
# do the same task making direct lxml calls.
#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#

#import lxml.etree
import traceback
from xmlutility import readXML
from xmlutility import XMLtoSchema
import sys

#
# Read in the schema
#
#schemaxml = lxml.etree.parse(sys.argv[1])
#schema  = lxml.etree.XMLSchema(schemaxml)

def validate(args):
    results = {}

    schemaxml = readXML(args[1])
    schema  = XMLtoSchema(schemaxml)

    #
    # Read in the xml file
    #
    #candidate = lxml.etree.parse(sys.argv[2])
    candidate = readXML(args[2])

    #
    # Check for validity -- prints errors on stdout if any are found
    #
    try:
        schema.assertValid(candidate)
        results[schema] = None
    except:  
        results[schema] = traceback.format_exc()
      
    #
    # now print the results, and the reason for failure if the
    # validation failed.  
    #
    out = open("validate.file",'w')
    for result in sorted(results):
        r = results[result]
        if r:
            print (result, "has failed:")
            out.write(str(result)+" has failed: \n")
            print (r)
        else:
            print (result, "is OK")
            out.write(str(result)+" is OK\n")
    out.close()
    
# -------------------------------------------------------------------
if __name__ == '__main__':
    validate(sys.argv)
