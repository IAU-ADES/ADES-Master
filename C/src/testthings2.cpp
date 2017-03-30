
#include <ades.h>


static void usage(const char *name) {
    printf("Usage: %s [options] xmlfile\n", name);
    printf("      --param name value : pass a (parameter,value) pair\n");

}




int
main(int argc, char **argv) {
	int i;
	const char *params[16 + 1];
	int nbparams = 0;
	xsltStylesheetPtr cur = NULL;
	xmlDocPtr doc, res, schemadoc, datadoc;

	int doc_txt_len;
	int retval;
	xmlChar *doc_txt_ptr = NULL;

	if (argc <= 1) {
		usage(argv[0]);
		return(1);
	}
	

 for (i = 1; i < argc; i++) {
        if (argv[i][0] != '-')
            break;
	if ((!strcmp(argv[i], "-param")) ||
                   (!strcmp(argv[i], "--param"))) {
		i++;
		params[nbparams++] = argv[i++];
		params[nbparams++] = argv[i];
		if (nbparams >= 16) {
			fprintf(stderr, "too many params\n");
			return (1);
		}
        }  else {
            fprintf(stderr, "Unknown option %s\n", argv[i]);
            usage(argv[0]);
            return (1);
        }
    }

	params[nbparams] = NULL;

	adesReadTables(ADES_MASTER, ADES_TABLES); // need to initials tables for PSV

	xmlSubstituteEntitiesDefault(1); // but we do use this
	cur = xsltParseStylesheetFile(BAD_CAST ADES_XSD_XSLT "generalxsd.xslt");
	doc = ADESreadXML(ADES_MASTER);
	res = xsltApplyStylesheet(cur, doc, params);


	//
	//  malloc's space for doc_txt_ptr; sets doc_txt_len
	//  free with XMLFree(doc_txt_ptr)
	//
	//int xsltSaveResultToString(xmlChar** doc_txt_ptr,
	//                           int* doc_txt_len,
	//                           xmlDoc* result,
	//                           xsltStylesheet* style);
	retval =  xsltSaveResultToString(&doc_txt_ptr,
	                                 &doc_txt_len,
	                                 res,
	                                 cur);

	printf("doc_txt_len = %d, retval = %d, doc_txt_ptr=%p\n",doc_txt_len, retval, doc_txt_ptr);
	if (retval == 0) {
	   fprintf(stdout, "%s\n",doc_txt_ptr);
	}

	schemadoc = xmlParseDoc(doc_txt_ptr);

	//
	// uncomment the xmlSaveFileEnc line to write schema
	//
	//xmlSaveFileEnc("outputxsdfile", schemadoc, "UTF-8");


	xmlFree(doc_txt_ptr); 
	doc_txt_ptr = NULL;   /* xmlFree can't do this since it needs void ** */
	
	//datadoc = xmlParseFile(argv[i]);  // pick up only argument
	datadoc = ADESreadXML(argv[i]);

	printf("datadocptr = %p\n", datadoc);

	if (!datadoc) return -1;

	//xmlDocDumpMemoryEnc(datadoc, &doc_txt_ptr, &doc_txt_len, "UTF-8");
	//xmlDocDumpMemory(datadoc, &doc_txt_ptr, &doc_txt_len);
	xmlDocDumpMemoryEnc(datadoc, &doc_txt_ptr, &doc_txt_len, "ASCII");
	printf("datadoc doc_txt_len = %d, retval = %d, doc_txt_ptr=%p\n",doc_txt_len, retval, doc_txt_ptr);
	if (retval == 0) {
	   fprintf(stdout, "%s\n",doc_txt_ptr);
	}
	xmlFree(doc_txt_ptr); 
	doc_txt_ptr = NULL;   /* xmlFree can't do this since it needs void ** */

	xmlDocPtr copyNewDoc = walkNodes(xmlDocGetRootElement(datadoc), 0);

	/* xsltSaveResultToFile(stdout, res, cur); */

	xmlSchemaParserCtxtPtr pCtx = xmlSchemaNewDocParserCtxt(schemadoc);
	if (!pCtx) return -1;

	xmlSchemaPtr sPtr = xmlSchemaParse(pCtx);
	if (!sPtr) return -1;


        xmlSchemaValidCtxtPtr schemaCtx = xmlSchemaNewValidCtxt(sPtr);
	if (!schemaCtx) return -1;

	//int	xmlSchemaGetValidErrors		(xmlSchemaValidCtxtPtr ctxt, 
	//		xmlSchemaValidityErrorFunc * err, 
	//		xmlSchemaValidityWarningFunc * warn, 
	//		void ** ctx)
	xmlSchemaValidityErrorFunc errfunc;
	xmlSchemaValidityWarningFunc warnfunc; 
	void *ctx = NULL;
	printf ("fee\n");
	xmlSchemaGetValidErrors(schemaCtx, &errfunc, &warnfunc, &ctx);
	printf ("fie %p %p %p\n", errfunc, warnfunc, ctx);

        xmlSchemaSetValidErrors(schemaCtx, (xmlSchemaValidityErrorFunc) err, (xmlSchemaValidityWarningFunc) warn, &ctx);
	printf ("foe %p\n", ctx);
        // xmlSchemaSetValidErrors(schemaCtx, (xmlSchemaValidityErrorFunc) err, (xmlSchemaValidityWarningFunc) warn, ctx);
	//
	//if (xmlSchemaValidateDoc(schemaCtx, datadoc)) return -1;
	if (xmlSchemaValidateDoc(schemaCtx, datadoc)) {
	   printf( "datadoc is INVALID\n" );
	} else {
	   printf( "datadoc is valid\n" );
	   adesDocToPsv(datadoc, stdout); // so print it as PSV
	   printf( "end of valid datadoc PSV\n" );

	}
	printf ("foo\n");


	printf("copyNewDoc = %p\n", copyNewDoc);
	xmlDocDumpMemoryEnc(copyNewDoc, &doc_txt_ptr, &doc_txt_len, "ASCII");
	printf("datadoc doc_txt_len = %d, retval = %d, doc_txt_ptr=%p\n",doc_txt_len, retval, doc_txt_ptr);
	if (retval == 0) {
	   fprintf(stdout, "%s\n",doc_txt_ptr);
	}
	xmlFree(doc_txt_ptr); 
	doc_txt_ptr = NULL;   /* xmlFree can't do this since it needs void ** */

	if (xmlSchemaValidateDoc(schemaCtx, copyNewDoc)) {
	   printf( "copyNewDoc is INVALID\n" );
	} else {
	   printf( "copyNewDoc is valid\n" );
	}
	if (copyNewDoc) {
	   obsBlockToPsv(xmlDocGetRootElement(copyNewDoc), stdout);
	}
	xmlFreeDoc(copyNewDoc);
	// also xmlSchemaValidateOneElement(schemaCtx, xmlNodePtr);

	xmlSchemaFreeValidCtxt ( schemaCtx );
	xmlSchemaFree ( sPtr );
	xmlSchemaFreeParserCtxt ( pCtx );

	xmlFreeDoc(schemadoc);
	schemadoc = NULL;
	xsltFreeStylesheet(cur);
	cur = NULL;
	xmlFreeDoc(res);
	res = NULL;
	xmlFreeDoc(doc);
	doc = NULL;

	for (i=0; i<nMemoryTest+1; i++) { // check for memory leaks
        	xmlDocPtr newdoc = xmlNewDoc(BAD_CAST "1.0");
		if (i%nMemoryTest == 0) printf("new newdoc = %p\n", newdoc);

		// xmlNewNode has type Element, which is what we want
		xmlNodePtr node = xmlNewNode(NULL, BAD_CAST "ades");
		// adds an attribute -- harder to modify but we don't
		xmlNewProp(node, BAD_CAST "version", BAD_CAST "2017");

		xmlNodePtr node2 = xmlNewNode(NULL, BAD_CAST "subelement");
        	//ADESsetNodeText(node2, BAD_CAST "hi > there <"); // memory to node2
        	//ADESsetTailText(node2, BAD_CAST "tail text"); // memory to node2
		xmlAddChild(node, node2); // takes memory from node2
		
		//xmlNodePtr node3 = xmlNewNode(NULL, BAD_CAST "subsubelement");
        	//ADESsetNodeText(node3, BAD_CAST BAD_CAST "and & and"); // memory to node3
		//xmlAddChild(node2, node3); // takes memory from node3
		xmlNewTextChild(node2, NULL, BAD_CAST "subsubelemnt", BAD_CAST "and & and");

		//xmlNodePtr node4 = xmlNewNode(NULL, BAD_CAST "subsubelement");
        	//ADESsetNodeText(node4, BAD_CAST BAD_CAST "hi > there <"); // memory to node3
		//xmlAddChild(node2, node4); // takes memory from node4
		xmlNewTextChild(node2, NULL, BAD_CAST "subsubelemnt", BAD_CAST "hi > there <");



		//xmlUnlinkNode(node2);
		//xmlFreeNode(node2);
		xmlDocSetRootElement(newdoc, node); // takes memory from node

		// note: pretty printing relies on not having any tail text and 
		//       not mixing text and sub-nodes
		//walkNodes(xmlDocGetRootElement(newdoc), 0);
		xmlFree(doc_txt_ptr); 
		doc_txt_ptr = NULL;   /* xmlFree can't do this since it needs void ** */
		xmlDocDumpFormatMemoryEnc(newdoc, &doc_txt_ptr, &doc_txt_len, "UTF-8", 1);

	        if (i==nMemoryTest) walkNodes(xmlDocGetRootElement(newdoc), 0);
		

		xmlFreeDoc(newdoc); // frees everything
	}


	printf("datadoc doc_txt_len = %d, retval = %d, doc_txt_ptr=%p\n",doc_txt_len, retval, doc_txt_ptr);
	if (retval == 0) {
	   fprintf(stdout, "%s\n",doc_txt_ptr);
	}


	for (i=0; i<nMemoryTest+1; i++) { // check for memory leaks
		adesReadTables(ADES_MASTER, ADES_TABLES);
		if (i%nMemoryTest == 0) {
			printf("psvTable %8d: %p\n", i, psvTable);
		}
	}


	printAdesTables();



	testApplyPadding(BAD_CAST "This is a test", 20, 'L', 0);
	testApplyPadding(BAD_CAST "This is a test", 20, 'R', 0);
	testApplyPadding(BAD_CAST "This is a test", 20, 'C', 0);
	testApplyPadding(BAD_CAST "This is a test", 21, 'C', 0);
	testApplyPadding(BAD_CAST "This is a test", 22, 'C', 0);
	testApplyPadding(BAD_CAST "This is a test", 5, 'L', 0);
	testApplyPadding(BAD_CAST "This is a test", 5, 'R', 0);
	testApplyPadding(BAD_CAST "This is a test", 5, 'C', 0);
	testApplyPadding(BAD_CAST "43.12", 20, 'D' , 3);
	testApplyPadding(BAD_CAST "43.12234324", 25, 'D' , 8);
	testApplyPadding(BAD_CAST "43.12234324", 10, 'D' , 8);

	testApplyPadding(BAD_CAST "123.4567890123", 10, 'D', 1);
	testApplyPadding(BAD_CAST "123.4567890123", 10, 'D', 6);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 1);
	testApplyPadding(BAD_CAST "333", 10, 'D', 5);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 5);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 5);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 5);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 8);
	testApplyPadding(BAD_CAST "333", 10, 'D', 8);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 8);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 8);
	testApplyPadding(BAD_CAST ".333.", 10, 'D', 9);
	testApplyPadding(BAD_CAST "333", 10, 'D', 9);
	testApplyPadding(BAD_CAST "333", 10, 'D', 9);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 9);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 10);
	testApplyPadding(BAD_CAST "333", 10, 'D', 10);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 10);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 10);
	testApplyPadding(BAD_CAST ".333", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333.", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333.11", 10, 'D', 11);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 2);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 2);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 4);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 5);
	testApplyPadding(BAD_CAST "333.45444", 10, 'D', 6);
	testApplyPadding(BAD_CAST "333.454440000", 10, 'L', 0);
	testApplyPadding(BAD_CAST "333.454440000", 10, 'R', 0);
	testApplyPadding(BAD_CAST "333.45444", 10, 'L', 0);
	testApplyPadding(BAD_CAST "333.45444", 10, 'R', 0);
	testApplyPadding(BAD_CAST "", 10, 'D', 5) ;

        xsltCleanupGlobals();
        xmlCleanupParser();


	return(0);

}

