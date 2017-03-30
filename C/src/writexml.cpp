
#include <ades.h>

/*
 * C++ program to create and write a new xml file
 * using ElementStack
 *
 * Usage:
 *   ./writexml <output xml file> 
 *
 */


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

	adesReadTables(ADES_MASTER, ADES_TABLES); // initialize tables

	ElementStack stack;
	// stack.clear() is already done in constructor

        PropVec property;
        property.push_back(PropPair("version", "2017"));
        stack.addPush(BAD_CAST "ades", NULL, property );

	stack.addPush(BAD_CAST "obsBlock");
		stack.addPush(BAD_CAST "obsContext");
			stack.addPush(BAD_CAST "observatory");
				stack.add(BAD_CAST "mpcCode", BAD_CAST "F51");
				stack.add(BAD_CAST "name", BAD_CAST "Pan-STARRS 1");
			stack.addPopPush(BAD_CAST "submitter");
				stack.add(BAD_CAST "name", BAD_CAST "P. Villa");
				stack.add(BAD_CAST "institution", BAD_CAST "Ejército Constitucionalista");
			stack.addPopPush(BAD_CAST "observers");
				stack.add(BAD_CAST "name", BAD_CAST "P. Villa");
				stack.add(BAD_CAST "name", BAD_CAST "F. Madero");
			stack.addPopPush(BAD_CAST "measurers");
				stack.add(BAD_CAST "name", BAD_CAST "P. Villa");
				stack.add(BAD_CAST "name", BAD_CAST "F. Madero");
			stack.addPopPush(BAD_CAST "telescope");
				stack.add(BAD_CAST "aperture", BAD_CAST "1.5");
				stack.add(BAD_CAST "design", BAD_CAST "Reflector");
				stack.add(BAD_CAST "detector", BAD_CAST "CCD");
			stack.addPopPush(BAD_CAST "fundingSource", BAD_CAST "Your favorite funding agency");
			stack.addPopPush(BAD_CAST "comment");
				stack.add(BAD_CAST "line", BAD_CAST "A comment line with >stuff< in it");
				stack.add(BAD_CAST "line", BAD_CAST "Another comment line");
		stack.pop();
	stack.addPopPush(BAD_CAST "obsData");
		stack.addPush(BAD_CAST "optical");
			stack.add(BAD_CAST "permID", BAD_CAST "1234456");
			stack.add(BAD_CAST "trkSub", BAD_CAST "aa");
			stack.add(BAD_CAST "mode", BAD_CAST "CCD");
			stack.add(BAD_CAST "stn", BAD_CAST "F51");
        		stack.add(BAD_CAST "obsTime", BAD_CAST "2016-08-29T12:32:34Z");
			stack.add(BAD_CAST "ra", BAD_CAST "10.21");
			stack.add(BAD_CAST "dec", BAD_CAST "21.21");
			stack.add(BAD_CAST "astCat", BAD_CAST "2MA");
			stack.add(BAD_CAST "mag", BAD_CAST "15.3");
			stack.add(BAD_CAST "band", BAD_CAST "w");
			stack.add(BAD_CAST "notes", BAD_CAST "klmn");
			stack.add(BAD_CAST "remarks", BAD_CAST "A free-form \"remark\" <with stuff>");
		stack.addPopPush(BAD_CAST "optical");
			stack.add(BAD_CAST "permID", BAD_CAST "1334456");
			stack.add(BAD_CAST "trkSub", BAD_CAST "aa");
			stack.add(BAD_CAST "mode", BAD_CAST "CCD");
			stack.add(BAD_CAST "stn", BAD_CAST "F51");
        		stack.add(BAD_CAST "obsTime", BAD_CAST "2016-08-29T12:32:34Z");
			stack.add(BAD_CAST "ra", BAD_CAST "10.21");
			stack.add(BAD_CAST "dec", BAD_CAST "21.21");
			stack.add(BAD_CAST "astCat", BAD_CAST "2MA");
			stack.add(BAD_CAST "mag", BAD_CAST "15.3");
			stack.add(BAD_CAST "band", BAD_CAST "w");
			stack.add(BAD_CAST "notes", BAD_CAST "klmn");
			stack.add(BAD_CAST "remarks", BAD_CAST "Another One");
		stack.pop();
	stack.pop();



	xmlDocPtr doc = stack.takeDocAndClear();
	saveXmlDoc (doc, argv[1], xmlEncoding, 1); // 1 means pretty-print; 0 means squish
	xmlFree(doc);
	

	

}

