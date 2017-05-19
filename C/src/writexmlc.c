
/*
 * C program to create and write a new xml file
 * using basic lmxl2 calls
 *
 * Usage:
 *   ./writexmlc <output xml file> 
 *
 */

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



//-------------------------------------------------------------------------
// simple use of standard lxml2 commands.  
//-------------------------------------------------------------------------

xmlNodePtr createADESTree() {
  xmlNodePtr n = xmlNewNode(NULL, BAD_CAST "ades");
  xmlNewProp(n, BAD_CAST "version", BAD_CAST "2017");
  return n;
}

xmlNodePtr addElement(xmlNodePtr parent, const xmlChar *tag) {
  xmlNodePtr n = xmlNewTextChild(parent, NULL, tag, NULL);
  return n;
}

void addDataElement(xmlNodePtr parent, const xmlChar *tag, const xmlChar *text) {
  xmlNewTextChild(parent, NULL, tag, text);
}

//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s <xml file> [<xml_encoding>]\n", name);
}

  static char utf8[] = "UTF-8";

  int main(int argc, char **argv) {
  char *xmlEncoding = utf8;

  if (argc <= 1) {
  usage(argv[0]);
    return(1);
  }
  if (argc > 2) {
    xmlEncoding = argv[2];
  }


  xmlNodePtr ades = createADESTree();

  xmlNodePtr obsBlock = addElement(ades, BAD_CAST "obsBlock");
    xmlNodePtr obsContext = addElement(obsBlock, BAD_CAST "obsContext");
      xmlNodePtr observatory = addElement(obsContext, BAD_CAST "observatory");
        addDataElement(observatory, BAD_CAST "mpcCode", BAD_CAST "F51");
        addDataElement(observatory, BAD_CAST "name", BAD_CAST "Pan-STARRS 1");
      xmlNodePtr submitter = addElement(obsContext, BAD_CAST "submitter");
        addDataElement(submitter, BAD_CAST "name", BAD_CAST "P. Villa");
        addDataElement(submitter, BAD_CAST "institution", BAD_CAST "Ejército Constitucionalista");
      xmlNodePtr observers = addElement(obsContext, BAD_CAST "observers");
        addDataElement(observers, BAD_CAST "name", BAD_CAST "P. Villa");
        addDataElement(observers, BAD_CAST "name", BAD_CAST "F. Madero");
      xmlNodePtr measurers = addElement(obsContext, BAD_CAST "measurers");
        addDataElement(measurers, BAD_CAST "name", BAD_CAST "P. Villa");
        addDataElement(measurers, BAD_CAST "name", BAD_CAST "F. Madero");
      xmlNodePtr telescope = addElement(obsContext, BAD_CAST "telescope");
        addDataElement(telescope, BAD_CAST "aperture", BAD_CAST "1.5");
        addDataElement(telescope, BAD_CAST "design", BAD_CAST "Reflector");
        addDataElement(telescope, BAD_CAST "detector", BAD_CAST "CCD");
      addDataElement(obsContext, BAD_CAST "fundingSource", BAD_CAST "Your favorite funding agency");
      xmlNodePtr comment = addElement(obsContext, BAD_CAST "comment");
        addDataElement(comment, BAD_CAST "line", BAD_CAST "A comment line with >stuff< in it");
        addDataElement(comment, BAD_CAST "line", BAD_CAST "Another comment line");
    xmlNodePtr obsData = addElement(obsBlock, BAD_CAST "obsData");
      xmlNodePtr optical = addElement(obsData, BAD_CAST "optical");
        addDataElement(optical, BAD_CAST "permID", BAD_CAST "1234456");
        addDataElement(optical, BAD_CAST "trkSub", BAD_CAST "aa");
        addDataElement(optical, BAD_CAST "mode", BAD_CAST "CCD");
        addDataElement(optical, BAD_CAST "stn", BAD_CAST "F51");
        addDataElement(optical, BAD_CAST "obsTime", BAD_CAST "2016-08-29T12:32:34Z");
        addDataElement(optical, BAD_CAST "ra", BAD_CAST "10.21");
        addDataElement(optical, BAD_CAST "dec", BAD_CAST "21.21");
        addDataElement(optical, BAD_CAST "astCat", BAD_CAST "2MA");
        addDataElement(optical, BAD_CAST "mag", BAD_CAST "15.3");
        addDataElement(optical, BAD_CAST "band", BAD_CAST "w");
        addDataElement(optical, BAD_CAST "notes", BAD_CAST "klmn");
        addDataElement(optical, BAD_CAST "remarks", BAD_CAST "A free-form \"remark\" <with stuff>");
      optical = addElement(obsData, BAD_CAST "optical");
        addDataElement(optical, BAD_CAST "permID", BAD_CAST "1334456");
        addDataElement(optical, BAD_CAST "trkSub", BAD_CAST "aa");
        addDataElement(optical, BAD_CAST "mode", BAD_CAST "CCD");
        addDataElement(optical, BAD_CAST "stn", BAD_CAST "F51");
        addDataElement(optical, BAD_CAST "obsTime", BAD_CAST "2016-08-29T12:32:34Z");
        addDataElement(optical, BAD_CAST "ra", BAD_CAST "10.21");
        addDataElement(optical, BAD_CAST "dec", BAD_CAST "21.21");
        addDataElement(optical, BAD_CAST "astCat", BAD_CAST "2MA");
        addDataElement(optical, BAD_CAST "mag", BAD_CAST "15.3");
        addDataElement(optical, BAD_CAST "band", BAD_CAST "w");
        addDataElement(optical, BAD_CAST "notes", BAD_CAST "klmn");
        addDataElement(optical, BAD_CAST "remarks", BAD_CAST "Another One");



  xmlDocPtr doc = xmlNewDoc(BAD_CAST "1.0"); // version 1.0 element
  xmlDocSetRootElement(doc, ades);          // doc owns all memory now

  // 1 means pretty-print; 0 means squish
  xmlSaveFormatFileEnc(argv[1], doc, xmlEncoding, 1);

  //int doc_txt_len;
  //xmlChar *doc_txt_ptr = NULL;
  //xmlDocDumpFormatMemoryEnc(doc, &doc_txt_ptr, &doc_txt_len, xmlEncoding, 1);
  //if (doc_txt_len) {
  //  fprintf(stdout, "%s\n", doc_txt_ptr);
  //}
  //xmlFree(doc_txt_ptr); // clean up memory



  xmlFree(doc);
	
}

