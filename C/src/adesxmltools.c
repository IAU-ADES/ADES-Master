
#include <ades.h>

// xmlSchemaSetValidErrors(valid_ctxt_ptr, (xmlSchemaValidityErrorFunc) err, (xmlSchemaValidityWarningFunc) warn, ctx);
void err(void *ctx, const char *msg, ...)
{
  char *buf = NULL; 
  va_list args;

  va_start(args, msg); // get size
  size_t sz = vsnprintf(buf, 0, msg, args);
  va_end(args);

  buf = (char*)malloc(sz+1);
  va_start(args, msg); // fill buffer
  sz = vsnprintf(buf, sz, msg, args);
  //printf("sz %ld len(buf) %ld\n",sz, strlen(buf));
  va_end(args);

  if(sz==0) { // Can't create schema validity error!
  } else {    // Do something to store `buf`, 
              // you may need to use void *ctx to achieve this
    printf("err: %s\n", buf);
  }
  free(buf);
  return;
}

void warn(void *ctx, const char *msg, ...)
{
  char *buf = NULL; 
  va_list args;

  va_start(args, msg); // get size
  size_t sz = vsnprintf(buf, 0, msg, args);
  printf("sz %ld len(buf) %ld\n",sz, sizeof(buf));
  va_end(args);

  buf = (char*)malloc(sz+1);
  va_start(args, msg); // fill buffer
  sz = vsnprintf(buf, sz, msg, args);
  va_end(args);

  if(sz==0) { // Can't create schema validity error!
  } else {    // Do something to store `buf`, 
              // you may need to use void *ctx to achieve this
    printf("warn: %s\n", buf);
  }
  free(buf);
  return;
}

// xmlSchemaSetValidErrors(valid_ctxt_ptr, (xmlSchemaValidityErrorFunc) err, (xmlSchemaValidityWarningFunc) warn, ctx);

xmlChar *errAndWarn = NULL;
void errToXmlChar(void *ctx, const char *msg, ...)
{
  char *buf = NULL; 
  va_list args;

  va_start(args, msg); // get size
  size_t sz = vsnprintf(buf, 0, msg, args);
  va_end(args);

  buf = (char*)malloc(sz+1);
  va_start(args, msg); // fill buffer
  sz = vsnprintf(buf, sz, msg, args);
  //printf("sz %ld len(buf) %ld\n",sz, strlen(buf));
  va_end(args);

  if(sz==0) { // Can't create schema validity error!
  } else {    // Do something to store `buf`, 
              // you may need to use void *ctx to achieve this
    //printf("err: %s\n", buf);
    errAndWarn = xmlStrcat(errAndWarn, BAD_CAST buf);
    errAndWarn = xmlStrcat(errAndWarn, BAD_CAST "\n");
  }
  free(buf);
  return;
}

void warnToXmlChar(void *ctx, const char *msg, ...)
{
  char *buf = NULL; 
  va_list args;

  va_start(args, msg); // get size
  size_t sz = vsnprintf(buf, 0, msg, args);
  printf("sz %ld len(buf) %ld\n",sz, sizeof(buf));
  va_end(args);

  buf = (char*)malloc(sz+1);
  va_start(args, msg); // fill buffer
  sz = vsnprintf(buf, sz, msg, args);
  va_end(args);

  if(sz==0) { // Can't create schema validity error!
  } else {    // Do something to store `buf`, 
              // you may need to use void *ctx to achieve this
    //printf("warn: %s\n", buf);
    errAndWarn = xmlStrcat(errAndWarn, BAD_CAST buf);
    errAndWarn = xmlStrcat(errAndWarn, BAD_CAST "\n");
  }
  free(buf);
  return;
}





// Don't need these -------------------------
//
// functions modelled after the python lxml library
// which gets the memory management right, or at
// least better than I probably could :-(.
//
// finds the next text node
// note c_node is used as a temp variable
//
xmlNode* ADEStextNodeOrSkip(xmlNode *c_node) {
	while (c_node) {
		if ( (c_node->type == XML_TEXT_NODE) ||
		     (c_node->type == XML_CDATA_SECTION_NODE))  {
			return c_node;
		} else if ( (c_node->type == XML_XINCLUDE_START) ||
		         (c_node->type == XML_XINCLUDE_END))  {
			c_node = c_node->next;
		} else {
			return NULL;
		}
	}
	return NULL;
}
//
// removes all text nodes from c_node
// note c_node is used as a temp variable
//
void ADESremoveText(xmlNode *c_node) {
	xmlNode *c_next;
	c_node = ADEStextNodeOrSkip(c_node);
	while (c_node) {
		c_next = ADEStextNodeOrSkip(c_node->next);
		xmlUnlinkNode(c_node);
		xmlFreeNode(c_node);
		c_node = c_next;
	}
}
//
// replaces or adds a node text element
// remove by passing NULL as value
//
int ADESsetNodeText(xmlNode *c_node, xmlChar *value) {
	xmlNode *c_text_node;
	// remove all text node children -- these are text 
	// and there should only be one
	ADESremoveText(c_node->children);
	if (value || *value == 0) {  // check for NULL or '' and ignore
		c_text_node = xmlNewDocText(c_node->doc, value);
		xmlAddChild(c_node, c_text_node);
		return 0;
	}
	return 0;
}
//
// replaces or adds a node tail  text element
// remove by passing NULL as value
//
int ADESsetTailText(xmlNode *c_node, xmlChar *value) {
	xmlNode *c_text_node;
	// remove all text nodes at next -- these are 
	// tail text and there should only be one
	ADESremoveText(c_node->next);
	if (value || *value == 0) {  // check for NULL or '' and ignore
		c_text_node = xmlNewDocText(c_node->doc, value);
		xmlAddNextSibling(c_node, c_text_node);
		return 0;
	}
	return 0;
}
//
// figure out adding attributes later -- we don't do this much
//
// Don't need these -------------------------
//
//





//
// strip white space (tabs, newlines, and spaces) from the
// beginning and end of strings   Note the xml parser adds
// text and tail-text nodes to recover the spacing.
// 
// This returns a new xmlChar array which must be freed with xmlFree
//
xmlChar *regularizeWhiteSpace(const xmlChar *textstr) {
	const xmlChar *begin, *end; 
	xmlChar *output;
	if (textstr == NULL) return NULL; // nothing gets nothing
	//printf ("%d %p\n", xmlStrlen(textstr) ,textstr);
	for (end=textstr + xmlStrlen(textstr) - 1; end != textstr - 1; end--) {
		//printf ("The end is %p %d\n", end, (int) *end);
		if ((*end != ' ') && (*end!='\n') && (*end !='\t')) {
			break;
		}
	}
	//printf ("textstr, end  %p %p %ld\n", textstr, end, (end-textstr)+1);
	if (end == textstr-1) return NULL; // no non-whitespace characters
	for (begin=textstr; *begin; begin++) {
		if ((*begin != ' ') && (*begin!='\n') && (*begin !='\t') ) {
			break;
		}
	}
	// sizeof(xmlChar) had better be sizeof(char) and sizeof(unsiged char)
	// need trailing NUL and space for end-begin+1 characters
	////output = (xmlChar*) xmlMallocAtomic((end-begin+2)*sizeof(xmlChar)); 
	////memcpy(output, begin, end-begin+1);      // copy characters
	////output[end-begin+1] = 0;                 // trailing NUL
	//printf ("begin, end  %p %p %ld\n", begin, end, (end-begin)+1);
	output = xmlStrndup(begin, end-begin+1);
	return output;                           // caller now owns the memory

}

void testRegularizeWhiteSpace(const xmlChar *textstr) {
	xmlChar *newstr = regularizeWhiteSpace(textstr);
	printf ("in, out = %p %p\n", textstr, newstr);
	if (textstr && newstr) {
		printf("in, out is .%s. .%s.\n", textstr, newstr);
		xmlFree(newstr);
		return;
	}
	if (textstr) {
		printf("in is .%s.\n", textstr);
	}
	if (newstr) {
		printf("out is .%s.\n", newstr);
	}
	xmlFree(newstr);
}
//
// Get the text from a node.  This strips any white space from
// both the left and the right, so it removes any C_DATA spacing
// stuff.  This is what we want for ADES.
// 
// the returned xmlChar * must be freed with xmlFree 
//
xmlChar *xmlNodeGetRegularizedText(xmlNode *node) {
	xmlChar *text = xmlNodeListGetString(node->doc, node->children, 1);
	xmlChar *regtext = regularizeWhiteSpace(text);
	xmlFree(text);
	return regtext;
}
//
// returns an xmlChar which starts with a space
// if there are any attributes and continues with
// an attribute declarates (such as att1="foo" att2="bar"
//
// the returned xmlChar * must be freed with xmlFree 
//
xmlChar *xmlNodeGetAttributeString(xmlNode *node) {
	xmlAttrPtr attr;
	// an empty but not null string
	xmlChar *attstr = xmlStrcat(NULL, (const xmlChar *)""); 
	xmlChar *attribute; 
	for(attr = node->properties; attr; attr = attr->next) {
		attribute = xmlGetProp(node, attr->name);
		attstr = xmlStrcat(attstr, (const xmlChar *)" ");
		attstr = xmlStrcat(attstr, attr->name);
		attstr = xmlStrcat(attstr, (const xmlChar *)"=\"");
		attstr = xmlStrcat(attstr, attribute);
		attstr = xmlStrcat(attstr, (const xmlChar *)"\"");
		xmlFree(attribute); // xmlGetProp made a copy
	}
	return attstr;
}


//
// creates a new doc with a copy of <node>
// as the root element.  <node> is copied
// recursively.  The returned xmlDoc owns
// all the memory.   This is a deep copy 
// of node, and the input node may be freed
// afterwards with no consequences.
//
xmlDocPtr copyNodeToNewDoc(xmlNode *node) {
	xmlDocPtr newDoc;
	xmlNodePtr copyNode = xmlCopyNode(node, 1); // 1 is deep copy;
	xmlUnlinkNode(copyNode);                    // remove copy from old doc
	newDoc = xmlNewDoc(BAD_CAST "1.0");         // version 1.0 document
	xmlDocSetRootElement(newDoc, copyNode);    // set as root
	return newDoc;
}


//
// An example of recursively walking through the document
//
// Note that our structure only has element with sub-elements,
// or elements with text, but never both (there is no tail text).
//
// Therefore, any particular element node will have text which
// is the first (and only) none-whitespace (!) text node in 
// its children.  Uncomment the XML_TEXT_NODE block to see
// this more clearly
//
static char spaces[] = "                                        ";
static int nspaces=40;

// return value is a test of grabbing a sub-node; probably
// we want something else call-back driven in the real
// program.
xmlDocPtr walkNodes(xmlNodePtr node, int level){
	int nextLevel = level + 1;
	char *indent = &spaces[nspaces-level*2];
	xmlNode *c_node;
	static xmlDocPtr copyNewDoc = NULL; // for test return
	int i;
	if (nextLevel > 10) nextLevel = 10;
        for (c_node = node; c_node; c_node = c_node->next) {
		if (c_node->type == XML_ELEMENT_NODE) {
			xmlChar *text = xmlNodeGetRegularizedText(c_node);
			xmlChar *attstr;

			for (i=0; i<nMemoryTest+1; i++) { // check for memory leaks
				attstr = xmlNodeGetAttributeString(c_node);
				//if (i%nMemoryTest == 0) printf("attstr = %p\n", attstr);
				if (i!=nMemoryTest) xmlFree(attstr); // free if not last one
			}
			if (text) {
				printf("%s%s%s|%s|%d %d\n",indent, c_node->name, attstr, text, xmlUTF8Strlen(text),xmlStrlen(text));
				xmlFree(text);
			} else {
				printf("%s%s%s||\n",indent, c_node->name, attstr);
			}
			xmlFree(attstr);
			if (xmlStrEqual(c_node->name, BAD_CAST "obsBlock")) {
			        for (i=0; i<nMemoryTest+1; i++) { // check for memory leaks
        				copyNewDoc = copyNodeToNewDoc(c_node);
					if (i%nMemoryTest == 0) printf("process obsBlock %p\n", copyNewDoc);
					if (i != nMemoryTest) xmlFreeDoc(copyNewDoc); // clean up
				}
			}
		}
		walkNodes(c_node->children, nextLevel);
	}
	return copyNewDoc;
}

//-------------------------------------------------------------------------

void printXmlDoc(xmlDocPtr doc, FILE *fout, int verbose) {
	xmlChar *doc_txt_ptr = NULL;
	int doc_txt_len = 0;

	if (verbose) fprintf(fout, "doc  = %p\n", doc);
	xmlDocDumpFormatMemoryEnc(doc, &doc_txt_ptr, &doc_txt_len, "UTF-8", 1);
	if (verbose) fprintf(fout, "datadoc doc_txt_len = %d, doc_txt_ptr=%p\n",doc_txt_len, doc_txt_ptr);
	if (doc_txt_len) {
		fprintf(fout, "%s\n",doc_txt_ptr);
	} else {
	}
	xmlFree(doc_txt_ptr);
}


//-------------------------------------------------------------------------

static xmlDocPtr doc = NULL; 
static xsltStylesheetPtr cur = NULL;
static xmlDocPtr datadoc = NULL;
static xmlDocPtr res = NULL;
static xmlDocPtr schemadoc = NULL;
static xmlSchemaParserCtxtPtr pCtx = NULL;
static xmlSchemaValidCtxtPtr schemaCtx = NULL;
static xmlSchemaPtr sPtr = NULL;


/*
 * This function frees all the xml structures
 * sets the pointers to NULL, and returns
 * retval.  The intended usage is 
 *
 * return freeForReturn(retval)
 *
 * This works around the lack of destructors in the
 * xml system.  Since it is always OK to free NULL and 
 * since the pointers are all intiallized to NJLL 
 * this works fine.  The only painful thing is the
 * need to have the pointers declared as static globals;
 */
static int freeForReturn(int retval) {
	xmlSchemaFreeValidCtxt ( schemaCtx );
	schemaCtx = NULL;
	xmlSchemaFree ( sPtr );
	sPtr = NULL;
	xmlSchemaFreeParserCtxt ( pCtx );
	pCtx = NULL;

	xmlFreeDoc(schemadoc);
	schemadoc = NULL;
	xmlFreeDoc(res);
	res = NULL;
	xmlFreeDoc(datadoc);
	datadoc = NULL;
	xsltFreeStylesheet(cur);
	cur = NULL;
	xmlFreeDoc(doc);
	doc = NULL;

	xsltCleanupGlobals();
	xmlCleanupParser();

	return retval;
}

//-------------------------------------------------------------------------

int xmlValidateAdes(char *adesmaster, char *schemaxslt, char *xmldatafile) {
	int validFlag = 0;
	int doc_txt_len;
        xmlChar *doc_txt_ptr = NULL;

	int retval;

	xmlSchemaValidityErrorFunc errfunc;
	xmlSchemaValidityWarningFunc warnfunc; 

	xmlSubstituteEntitiesDefault(1); // but we do use this

	doc = ADESreadXML(adesmaster);
	if (!doc) return freeForReturn(-2);
	cur = xsltParseStylesheetFile(BAD_CAST schemaxslt);
	if (!cur) return freeForReturn(-2);
	datadoc = ADESreadXML(xmldatafile);
	if (!datadoc) return freeForReturn(-2);

	res = xsltApplyStylesheet(cur, doc, NULL);

	// malloc's space for doc_txt_ptr; must xmlFree
	retval =  xsltSaveResultToString(&doc_txt_ptr,
	                                 &doc_txt_len,
	                                 res,
	                                 cur);

	if (retval != 0) return freeForReturn(-2);

	schemadoc = xmlParseDoc(doc_txt_ptr);
	xmlFree(doc_txt_ptr); 
	doc_txt_ptr = NULL; 

	pCtx = xmlSchemaNewDocParserCtxt(schemadoc);
	if (!pCtx) return freeForReturn(-2);

	sPtr = xmlSchemaParse(pCtx);
	if (!sPtr) return freeForReturn(-2);

        schemaCtx = xmlSchemaNewValidCtxt(sPtr);
	if (!schemaCtx) return freeForReturn(-2);

	void *ctx = NULL; /* need to pass &ctx */
	xmlSchemaGetValidErrors(schemaCtx, &errfunc, &warnfunc, &ctx);

        xmlSchemaSetValidErrors(schemaCtx, (xmlSchemaValidityErrorFunc) err, (xmlSchemaValidityWarningFunc) warn, &ctx);
	if (xmlSchemaValidateDoc(schemaCtx, datadoc)) {
	   //printf( "datadoc is INVALID\n" );
	   validFlag = -1;
	} else {
	   //printf( "datadoc is valid\n" );
	   validFlag = 0;

	}

	return freeForReturn(validFlag);

}

//-------------------------------------------------------------------------

//
// validate xmldatafiel against the schemas and print out 
// the result.  This requires capturing the errors and warnings to
// a string and remembering the results
//
//  If called with schema = -1, it validates against all the
//  schemas.  If called with schema=n, it just validates
//  against n.  Use schema=2 for submit and schema=0 for general

#define nxsds 4
int xmlValidateAll(char *xmldatafile, int schema) {
	int i;
	int validFlag = 0;
	int doc_txt_len;
        xmlChar *doc_txt_ptr = NULL;

	int retval;
	int startschema = 0;
	int stopschema = nxsds;

	xmlSchemaValidityErrorFunc errfunc;
	xmlSchemaValidityWarningFunc warnfunc; 

	char *xsdNicknames[nxsds];
	char *xsdFilenames[nxsds];
	xmlChar *xsdErrors[nxsds];
	int xsdValid[nxsds];
	xsdFilenames[0] = "generalxsd.xslt";
	xsdFilenames[1] = "generalhumanxsd.xslt";
	xsdFilenames[2] = "submitxsd.xslt";
	xsdFilenames[3] = "submithumanxsd.xslt";
	xsdNicknames[0] = "general";
	xsdNicknames[1] = "generalhuman";
	xsdNicknames[2] = "submit";
	xsdNicknames[3] = "submithuman";
	xsdErrors[0] = NULL;
	xsdErrors[1] = NULL;
	xsdErrors[2] = NULL;
	xsdErrors[3] = NULL;
	xsdValid[0] = 0;
	xsdValid[1] = 0;
	xsdValid[2] = 0;
	xsdValid[3] = 0;

	if ((schema > -1) && (schema < stopschema)) {
		startschema = schema;
		stopschema = schema+1;
	}

	xmlSubstituteEntitiesDefault(1); // but we do use this

	doc = ADESreadXML(ADES_MASTER);
	if (!doc) return freeForReturn(-2);
	datadoc = ADESreadXML(xmldatafile);
	if (!datadoc) return freeForReturn(-2);

	for (i=startschema; i!=stopschema; i++) {
		xmlChar *thisxsd = xmlCharStrdup(ADES_XSD_XSLT);
		thisxsd = xmlStrcat(thisxsd, BAD_CAST xsdFilenames[i]);
		cur = xsltParseStylesheetFile(thisxsd);
		xmlFree(thisxsd); // done with name
		if (!cur) return freeForReturn(-2);

		res = xsltApplyStylesheet(cur, doc, NULL);

		// malloc's space for doc_txt_ptr; must xmlFree
		retval =  xsltSaveResultToString(&doc_txt_ptr,
	                                 	&doc_txt_len,
	                                 	res,
	                                 	cur);

		if (retval != 0) return freeForReturn(-2);
	
		schemadoc = xmlParseDoc(doc_txt_ptr);
		xmlFree(doc_txt_ptr); 
		doc_txt_ptr = NULL; 
	
		pCtx = xmlSchemaNewDocParserCtxt(schemadoc);
		if (!pCtx) return freeForReturn(-2);
	
		sPtr = xmlSchemaParse(pCtx);
		if (!sPtr) return freeForReturn(-2);

        	schemaCtx = xmlSchemaNewValidCtxt(sPtr);
		if (!schemaCtx) return freeForReturn(-2);

		void *ctx = NULL; /* need to pass &ctx */
		xmlSchemaGetValidErrors(schemaCtx, &errfunc, &warnfunc, &ctx);

        	xmlSchemaSetValidErrors(schemaCtx, (xmlSchemaValidityErrorFunc) errToXmlChar, 
				        (xmlSchemaValidityWarningFunc) warnToXmlChar, &ctx);
		if (xmlSchemaValidateDoc(schemaCtx, datadoc)) {
	   		validFlag = -1;
		} else {
	   		validFlag = 0;
		}

		xmlSchemaFreeValidCtxt ( schemaCtx );
		schemaCtx = NULL;
		xmlSchemaFree ( sPtr );
		sPtr = NULL;
		xmlSchemaFreeParserCtxt ( pCtx );
		pCtx = NULL;

		xmlFreeDoc(schemadoc);
		schemadoc = NULL;
		xmlFreeDoc(res);
		res = NULL;
		xsltFreeStylesheet(cur);
		cur = NULL;

		xsdValid[i] = validFlag;
		xsdErrors[i] = xmlStrdup(errAndWarn);
		xmlFree(errAndWarn); // need to free so the next run starts at NULL
		errAndWarn = NULL;
	}
        for (i=startschema; i!=stopschema; i++) {
		if (xsdValid[i] == 0) {
			printf("%s is OK\n", xsdNicknames[i]);
		} else {
			printf("%s has failed:\n", xsdNicknames[i]);
		}
		if (xsdErrors[i]) {
			printf("%s", xsdErrors[i]);
			xmlFree(xsdErrors[i]);
		}
	}

	return freeForReturn(0);

}

