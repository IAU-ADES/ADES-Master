/*
 * include file for ades C interface.   
 *
 *
 */

#ifndef __ADES_H__
#define __ADES_H__
#ifdef __cplusplus
#include <string>
#include <vector>
#include <map>
#include <exception>
#endif /* __cplusplus */

#include <string.h>
#include <libxml/xmlschemas.h>
#include <libxml/xmlmemory.h>
#include <libxml/debugXML.h>
#include <libxml/HTMLtree.h>
#include <libxml/xmlIO.h>
#include <libxml/xinclude.h>
#include <libxml/catalog.h>
#include <libxslt/xslt.h>
#include <libxslt/xsltInternals.h>
#include <libxslt/transform.h>
#include <libxslt/xsltutils.h>

#include <psvtools.h>
#include <adestables.h>
#include <adesxmltools.h>

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

/*
 * ADESreadXML reads an xml doc from a file.
 * on error, it returns NULL
 *
 *xmlDocPtr ADESreadXML(const char *xmlFileName) {
 *      xmlDocPtr doc;
 *
 *      //doc = xmlParseFile(argv[i]);
 *      // second argument to xmlReadFile is encoding, but this
 *      // should be automatic
 *      doc = xmlReadFile(xmlFileName, NULL, 0);
 *      return doc;
 *
 *      Must be free'd with xmlFreeDoc
 *
 */
#define ADESreadXML(file) xmlReadFile(file, NULL, 0)

/*
 * These macros are based on ADES_PATH which was defined
 * with -D and points to the directory just above this one
 *
 * ADES_MASTER  : adesmaster.xml file
 * ADES_TABLES  : adestables.xslt fileb
 * ADES_XSD_XSLT: directory with xslt files for xsd
 *
 */

#ifndef ADES_PATH
	Must have -DADES_PATH on compile line!
#endif /* ADES_PATH */

/*
 * Stringify(foo) turns into "foo" -- I have no 
 * idea how standard this is but it works in gcc
 *
 * This requires two macros and th # operation .  
 */
#define Stringify_help(s) #s
#define Stringify(s) Stringify_help(s)

#define ADES_MASTER Stringify(ADES_PATH)  "/../xml/adesmaster.xml"
#define ADES_XSD_XSLT Stringify(ADES_PATH)  "/../xslt/xsd/"


#define nMemoryTest 10


#ifdef __cplusplus
}
#endif /* __cplusplus */
#endif /* __ADES_H__ */
