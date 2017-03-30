
#include <ades.h>

/*
 * C program to convert an psv file into an xml file
 *
 * Usage:
 *   ./xmltopsv <psv file> <output xml file> 
 *   ./xmltopsv some.psv some.xml
 *
 */


//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s <psv file> <xml file> [<psv_encoding> [<xml_encoding]]\n", name);
    printf("      if <xml file> is stdout, writes to stdout as bytes");
}

static char utf8[] = "UTF-8";

int main(int argc, char **argv) {
	char *psvEncoding = utf8;
	char *xmlEncoding = utf8;

	if (argc <= 2) {
		usage(argv[0]);
		return(1);
	}
	if (argc > 3) {
		psvEncoding = argv[3];
	}
	if (argc > 4) {
		xmlEncoding = argv[4];
	}

	adesReadTables(ADES_MASTER, ADES_TABLES); // initialize tables

	//int i; // this is to check for memory leaks
	//for (i=0; i<nMemoryTest+1; i++) {
	//	xmlChar *test = xmlCharStrdup("malloc this");
	//	int j = convertPsvToXml(argv[1], argv[2], psvEncoding, xmlEncoding);
	//	if (i%nMemoryTest == 0) printf ("%d %p\n", j, test);
	//	xmlFree(test);
	//}
	
	
	return convertPsvToXml(argv[1], argv[2], psvEncoding, xmlEncoding);

}

