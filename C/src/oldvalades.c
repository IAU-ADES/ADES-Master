
#include <ades.h>

/*
 * C program to create a schema from the
 * adesmaster file and use that to validate an
 * xml file
 *
 * Usage:
 *   ./valades.py <adesmaster file> <xslt file for schema> <xml file to validate>
 *   ./valades.py adesmaster.xml submitxsd.xslt newsubmit.xml
 *
 * xslt files:               All of thsee transform adesmaster.xml to a schema
 *    submitxsd.xslt         creates xsd file to validate submission xml
 *    submithumanxsd.xslt    Same but in human-readable form
 *    distribxsd.xslt        creates xsd file to validate distribution xml
 *    distribhumanxsd.xslt   Same but in human-readable form
 *    generalxsd.xslt        creates xsd file to validate in general
 *    generalhumanxsd.xslt   Same but in human-readable form
 *
 */

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



//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s [options] adesmaster stylesheet file\n", name);
    printf("      --param name value : pass a (parameter,value) pair\n");

}

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
static int valadesFreeForReturn(int retval) {
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

int main(int argc, char **argv) {
	int i;
	int validFlag = 0;
	int doc_txt_len;
        xmlChar *doc_txt_ptr = NULL;

	int retval;

	xmlSchemaValidityErrorFunc errfunc;
	xmlSchemaValidityWarningFunc warnfunc; 

	if (argc <= 3) {
		usage(argv[0]);
		return(1);
	}
	
	xmlSubstituteEntitiesDefault(1); // but we do use this

	i = 1;
	doc = ADESreadXML(argv[i]);
	if (!doc) return valadesFreeForReturn(-2);
       	i++;
	cur = xsltParseStylesheetFile(BAD_CAST argv[i]);
	if (!cur) return valadesFreeForReturn(-2);
	i++;
	datadoc = ADESreadXML(argv[i]);
	if (!datadoc) return valadesFreeForReturn(-2);
	i++;

	res = xsltApplyStylesheet(cur, doc, NULL);

	// malloc's space for doc_txt_ptr; must xmlFree
	retval =  xsltSaveResultToString(&doc_txt_ptr,
	                                 &doc_txt_len,
	                                 res,
	                                 cur);

	if (retval != 0) return valadesFreeForReturn(-2);

	schemadoc = xmlParseDoc(doc_txt_ptr);
	xmlFree(doc_txt_ptr); 
	doc_txt_ptr = NULL; 

	pCtx = xmlSchemaNewDocParserCtxt(schemadoc);
	if (!pCtx) return valadesFreeForReturn(-2);

	sPtr = xmlSchemaParse(pCtx);
	if (!sPtr) return valadesFreeForReturn(-2);

        schemaCtx = xmlSchemaNewValidCtxt(sPtr);
	if (!schemaCtx) return valadesFreeForReturn(-2);

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

	return valadesFreeForReturn(validFlag);

}

