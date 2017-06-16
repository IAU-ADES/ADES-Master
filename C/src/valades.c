
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
 *    generalxsd.xslt        creates xsd file to validate in general
 *    generalhumanxsd.xslt   Same but in human-readable form
 *
 */


//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s adesmaster stylesheet xmldatafile\n", name);

}

int main(int argc, char **argv) {

	if (argc <= 3) {
		usage(argv[0]);
		return(1);
	}
	//int i; // this is to check for memory leaks
	//for (i=0; i<nMemoryTest+1; i++) {
	//	xmlChar *test = xmlCharStrdup("malloc this");
	//	int j = xmlValidateAdes(argv[1], argv[2], argv[3]);
	//	if (i%nMemoryTest == 0) printf ("%d %p\n", j, test);
	//	xmlFree(test);
	//}
	
	return xmlValidateAdes(argv[1], argv[2], argv[3]);

}

