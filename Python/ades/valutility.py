# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import traceback
import re

from ades import adesutility

def validate_schema(schema_name, schema, candidate, out):
    #
    # Check for validity -- prints errors on stdout if any are found
    #
    try:
        schema.assertValid(candidate)
        result = None
    except:  
        result = traceback.format_exc()

    #
    # now print the results, and the reason for failure if the
    # validation failed.  
    #
    if result:
        print (schema_name, "has failed:")
        out.write(str(schema_name)+" has failed: \n")
        print (result)
    else:
        print (schema_name, "is OK")
        out.write(str(schema_name)+" is OK\n")

    return result

def validate_xslt(schema_name, schemaxslt, candidate, out):
    masterfile = adesutility.adesmaster

    #
    # read in master file 
    #
    xml_tree = adesutility.readXML(masterfile)

    xslt_tree = adesutility.readXML(schemaxslt)
    schema = adesutility.XMLtoSchemaViaXSLT(xml_tree, xslt_tree)

    return validate_schema(schema_name, schema, candidate, out)

def validate_xslts(schemaxslts, candidate, out):
    results = {}
    for schema_name in schemaxslts:
        results[schema_name] = validate_xslt(schema_name, schemaxslts[schema_name], candidate, out)
    return results

def validate_xml_declaration(xmlfile, out):
    valid = False
    with open(xmlfile, "r") as f:
        for line in f.readlines():
            if line.strip() != "":
                match = re.search(r"^<\?xml.*\?>", line.strip())
                valid = (match is not None)
                break
    
    if not valid:
        print("candidate file", xmlfile, "has no XML declaration")
        print("candidate file", xmlfile, "has no XML declaration", file=out)
