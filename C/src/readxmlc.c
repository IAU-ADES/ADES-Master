
/*
 * C program to demonstrate walking through an xml file
 *
 * Usage:
 *   ./readxmlc <xml file>
 *
 */

#include <string.h>
#include <ctype.h>
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


int isnotempty(xmlChar *s) // 1 if not all whitespace -- this only works
{                          // because ades nodes have no tail.
  while (*s) {
    if (!isspace(*s)) return 1;
    s++;
  }
   return 0;
}

//
// process optical elements specially
// 
void processOpticalElement(int depth, const xmlNodePtr node) {
  for (int i=0; i<depth; i++) printf ("  "); // indent
  printf("%s\n", node->name);                  // print tag
  for (int i=0; i<depth+1; i++) printf ("  "); // indent
  printf("OPTICAL ELEMENT LIST FOUND\n");

  // now process any child elements, which are all terminals
  for (xmlNodePtr child = node->children; child; child = child->next) {
    if (child->type == XML_ELEMENT_NODE) {
      xmlChar *text = xmlNodeListGetString(child->doc, child->children, 1);
      for (int i=0; i<depth+1; i++) printf ("  "); // indent
      printf("%s = %s\n", child->name, text);
      xmlFree(text);
    }
  }

}

void printElement(int depth, const xmlNodePtr node) {
  for (int i=0; i<depth; i++) printf ("  "); // indent
  printf("%s", node->name);                  // print tag

  // print any attributes
  for (xmlAttrPtr attr = node->properties; attr; attr = attr->next) {
    xmlChar *attribute = xmlGetProp(node, attr->name); 
    if (attribute) {   
       printf(" {'%s': '%s'}", attr->name, attribute);
       xmlFree(attribute);  // free memory
    }
  }
  // xmlNodeListGetString(,,1) properly translates strings
  xmlChar* text = xmlNodeListGetString(node->doc, node->children, 1);
  if (text && isnotempty(text)) {
    printf(": %s", text);
  }
  xmlFree(text); // may be NULL but that's OK.

  printf("\n");                              // end line

  // now process any child elements
  for (xmlNodePtr child = node->children; child; child = child->next) {
    if (child->type == XML_ELEMENT_NODE) {
      if (!strcmp((const char *)child->name, "optical")) {
        processOpticalElement(depth+1, child);
      } else {
        printElement(depth+1, child);
      }
    } 
  }

}

//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s <xml file>\n", name);
    printf("      if <xml file> is stdout, writes to stdout as bytes");
}

static char utf8[] = "UTF-8";

int main(int argc, char **argv) {
  char *xmlEncoding = utf8;
  char *xmlFile = NULL;

  if (argc != 2) {
    usage(argv[0]);
    return(1);
  } else {
    xmlFile = argv[1];
  }

  xmlDocPtr doc = NULL;
  doc = xmlReadFile(xmlFile, NULL, 0);
  xmlNodePtr root = xmlDocGetRootElement(doc);

  printElement(0, root);

  xmlFreeDoc(doc); // remember to clean up at the end

}

