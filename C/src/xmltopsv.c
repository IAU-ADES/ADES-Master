
#include <ades.h>

/*
 * C program to convert an xml file to a psv file
 *
 * Usage:
 *   ./xmltopsv <xml file> <output psv file>
 *   ./xmltopsv some.xml some.psv
 *
 *
 */


//-------------------------------------------------------------------------


static void usage(const char *name) {
    printf("Usage: %s <xml file> <psv file>\n", name);
    printf("      if <psv file> is stdout, writes to stdout as bytes");
}

int main(int argc, char **argv) {

	if (argc <= 2) {
		usage(argv[0]);
		return(1);
	}

	adesReadTables(ADES_MASTER, ADES_TABLES); // initialize tables

	//int i; // this is to check for memory leaks
	//for (i=0; i<nMemoryTest+1; i++) {
	//	xmlChar *test = xmlCharStrdup("malloc this");
	//	int j = convertXmlToPsv(argv[1], argv[2]);
	//	if (i%nMemoryTest == 0) printf ("%d %p\n", j, test);
	//	xmlFree(test);
	//}
	
	
	return convertXmlToPsv(argv[1], argv[2]);

}

