# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import traceback
import re

from ades import adesutility

def format_schema_errors(schema):
    """Format every entry in a schema's error log as `  line N: message` lines.

    lxml fills error_log during validate(); assertValid() stops at the first
    invalid element and raises, so only one error is ever available there.
    """
    return "".join(
        "  line {}: {}\n".format(entry.line, entry.message)
        for entry in schema.error_log
    )

def validate_schema(schema_name, schema, candidate, out, all_errors=False):
    #
    # Check for validity -- prints errors on stdout if any are found
    #
    if all_errors:
        result = None
        if not schema.validate(candidate):
            result = format_schema_errors(schema)
    else:
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
        if all_errors:
            out.write(result)
        print (result)
    else:
        print (schema_name, "is OK")
        out.write(str(schema_name)+" is OK\n")

    return result

def validate_xslt(schema_name, schemaxslt, candidate, out, all_errors=False):
    masterfile = adesutility.adesmaster

    #
    # read in master file 
    #
    xml_tree = adesutility.readXML(masterfile)

    xslt_tree = adesutility.readXML(schemaxslt)
    schema = adesutility.XMLtoSchemaViaXSLT(xml_tree, xslt_tree)

    return validate_schema(schema_name, schema, candidate, out, all_errors)

def validate_xslts(schemaxslts, candidate, out, all_errors=False):
    results = {}
    for schema_name in schemaxslts:
        results[schema_name] = validate_xslt(schema_name, schemaxslts[schema_name], candidate, out, all_errors)
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
