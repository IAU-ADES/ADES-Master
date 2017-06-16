
#include <ades.h>

/*
 * C program to validate an xml file against all six schemas
 *
 * Usage:
 *   ./valall <xml file>
 *
 * xslt files:               All of thsee transform adesmaster.xml to a schema
 *    submitxsd.xslt         creates xsd file to validate submission xml
 *    submithumanxsd.xslt    Same but in human-readable form
 *    generalxsd.xslt        creates xsd file to validate in general
 *    generalhumanxsd.xslt   Same but in human-readable form
 *
 */


//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s xmldatafile\n", name);

}

int main(int argc, char **argv) {

	if (argc <= 1) {
		usage(argv[0]);
		return(1);
	}
	//int i; // this is to check for memory leaks
	//for (i=0; i<nMemoryTest+1; i++) {
	//	xmlChar *test = xmlCharStrdup("malloc this");
	//	int j = xmlValidateAll(argv[1]);
	//	if (i%nMemoryTest == 0) printf ("%d %p\n", j, test);
	//	xmlFree(test);
	//}
	
	return xmlValidateAll(argv[1], -1);

}

