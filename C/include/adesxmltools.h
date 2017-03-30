/*
 * include file for ades C interface.   
 *
 *
 */

#ifndef __ADESXMLTOOLS_H__
#define __ADESXMLTOOLS_H__

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


void err(void *ctx, const char *msg, ...);
void warn(void *ctx, const char *msg, ...);

extern xmlChar *errAndWarn; // set by below
void errToXmlChar(void *ctx, const char *msg, ...);
void warnToXmlChar(void *ctx, const char *msg, ...);


//
// strip white space (tabs, newlines, and spaces) from the
// beginning and end of strings   Note the xml parser adds
// text and tail-text nodes to recover the spacing.
// 
// This returns a new xmlChar array which must be free with xmlFree
//
xmlChar *regularizeWhiteSpace(const xmlChar *textstr);
void testRegularizeWhiteSpace(const xmlChar *textstr);
//
// Get the text from a node.  This strips any white space from
// both the left and the right, so it removes any C_DATA spacing
// stuff.  This is what we want for ADES.
// 
// the returned xmlChar * must be freed with xmlFree 
//
xmlChar *xmlNodeGetRegularizedText(xmlNode *node);
//
// returns an xmlChar which starts with a space
// if there are any attributes and continues with
// an attribute declarates (such as att1="foo" att2="bar"
//
// the returned xmlChar * must be freed with xmlFree 
//
xmlChar *xmlNodeGetAttributeString(xmlNode *node);




// Don't need these -------------------------
//
// functions modelled after the python lxml library
// which gets the memory management right, or at
// least better than I probably could :-(.
//
// finds the next text node
// note c_node is used as a temp variable
//
xmlNode* ADEStextNodeOrSkip(xmlNode *c_node);
//
// removes all text nodes from c_node
// note c_node is used as a temp variable
//
void ADESremoveText(xmlNode *c_node);
//
// replaces or adds a node text element
// remove by passing NULL as value
//
int ADESsetNodeText(xmlNode *c_node, xmlChar *value);
//
// replaces or adds a node tail  text element
// remove by passing NULL as value
//
int ADESsetTailText(xmlNode *c_node, xmlChar *value);
// Don't need these -------------------------
//





//
// creates a new doc with a copy of <node>
// as the root element.  <node> is copied
// recursively.  The returned xmlDoc owns
// all the memory.   This is a deep copy 
// of node, and the input node may be freed
// afterwards with no consequences.
//
xmlDocPtr copyNodeToNewDoc(xmlNode *node);

// return value is a test of grabbing a sub-node; probably
// we want something else call-back driven in the real
// program.
xmlDocPtr walkNodes(xmlNodePtr node, int level);

//
// prints an xml doc in a human-readable form
//
void printXmlDoc(xmlDocPtr doc, FILE *fout, int verbose);

int xmlValidateAdes(char *adesmaster, char *schemaxslt, char *xmldatafile);
int xmlValidateAll(char *xmldatafile, int schema);

#ifdef __cplusplus
}
#endif /* __cplusplus */
#endif /* __ADESXMLTOOLS_H__ */
