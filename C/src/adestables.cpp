
#include <ades.h>

DictMap allowedElementDict;
DictMap requiredElementDict;
DictMapSet allowedElementDictSet;
DictMapSet requiredElementDictSet;


//
//  Alloc grows by factor of two each time,
//  so Len growth leads to amortized O(1) time
//  for the realloc step.
//
static int psvTableAlloc = 0;
int psvTableLen = 0;
psvTableEntry *psvTable = NULL;

static void adesFreePsvTable() {
	// deallocates psvTable
	int i;
	for (i=0; i<psvTableLen; i++) {
		xmlFree(psvTable[i].tagtype);
		xmlFree(psvTable[i].name);
	}
	free(psvTable);  // free memory and reset counters and pointers
	psvTable = NULL;
	psvTableLen = 0;
	psvTableAlloc = 0;
}


std::map<std::string, std::vector<HeaderStruct> > BaseHeaderInfoMap;

// we could keep this as part of psvTables since it needs to be copied but never changes
static void makeHeaderInfoMap(const std::string &subtype) { 
        BaseHeaderInfoMap[subtype]; // force a new entry
	StringSet psvList;
        for (int i=0; i<psvTableLen; i++) {
                HeaderStruct h;
                psvTableEntry *t = &psvTable[i];
		if ( subtype == (const char *) t->tagtype ) {
			h.name = (char *) t->name; // converts to std::string
			h.width = t->width;
                	h.dpos = t->dpos;
                	h.fmt = t->just;
                	h.seen = false;

                	if (xmlUTF8Strlen(t->name) > h.width) {
                        	h.width = xmlUTF8Strlen(t->name);
                	}
                	BaseHeaderInfoMap[subtype].push_back(h);
			psvList.insert(h.name);
		}
        }
	//
	// now add other allowed elements between notes and remarks (or insert just before end)
	//
        for (StringVector::const_iterator x = allowedElementDict[subtype].begin();
		x != allowedElementDict[subtype].end(); x++) {
		if (psvList.find(*x) == psvList.end()) { // if not in set add it
			HeaderStruct h;
                	h.name = *x; 
                	h.width = x->size();
                	h.dpos = 0;
                	h.fmt = 'R';
                	h.seen = false;
			// 
			// insert just before last element
			//
			std::vector<HeaderStruct>::iterator it = BaseHeaderInfoMap[subtype].end() - 1;
			BaseHeaderInfoMap[subtype].insert(it, h);

			psvList.insert(h.name);
		}
	}

}

static void makeHeaderInfo() { // make this for all obsData elements
	for (StringVector::const_iterator x = allowedElementDict["obsData"].begin();
		x != allowedElementDict["obsData"].end(); x++) {
		//printf("calling makeHeaderInfoMap %s\n", x->c_str());
		makeHeaderInfoMap(*x);
	}
}
	
//
// implementation in pure C not used
//
////void adesParsePsvTable(const xmlChar *tablePtr, int tableLen) {
////	//
////	// Populates psvTable from the string tablePtr of length tableLen
////    // this does not create the map using tagtype
////	//
////
////	//printf("tableLen = %d, retval = %d, tablePtr=%p\n",tableLen, retval, tablePtr);
////    const xmlChar *tagtypePtr,
////	const xmlChar *psvPtr, *namePtr, *widthPtr, *justPtr, *dposPtr, *ptr2;
////	xmlChar *name, *widthStr, *dposStr; // not const for free
////	int width, dpos;
////	//fprintf(stdout, "%s\n",tablePtr);
////
////	psvPtr = xmlStrstr(tablePtr, BAD_CAST "\npsv ");
////	while (psvPtr) {
////		//printf("%s\n", psvPtr+5);
////		// xmlStrndup can segfault if ptr2 is 0, so we 
////		// might want more checking here and not just
////		// for dposStr
////		tagtypePtr = xmlStrstr(psvPtr+5, BAD_CAST "tagtype ") + 5;
////		ptr2 = xmlStrstr(namePtr, BAD_CAST " ");
////
////		namePtr = xmlStrstr(psvPtr+5, BAD_CAST "name ") + 5;
////		ptr2 = xmlStrstr(namePtr, BAD_CAST " ");
////		name = xmlStrndup(namePtr, ptr2 - namePtr);
////
////		widthPtr = xmlStrstr(namePtr, BAD_CAST "width ") + 6;
////		ptr2 = xmlStrstr(widthPtr, BAD_CAST " ");
////		widthStr = xmlStrndup(widthPtr, ptr2 - widthPtr);
////
////		justPtr = xmlStrstr(widthPtr, BAD_CAST "just ") + 5;
////
////		dposPtr = xmlStrstr(justPtr, BAD_CAST "dpos ") + 5;
////		ptr2 = xmlStrstr(dposPtr, BAD_CAST "\n");
////		if (!ptr2) { // we went off the end of the string 
////				dposStr = xmlStrdup(dposPtr);
////		} else {
////				dposStr = xmlStrndup(dposPtr, ptr2 - dposPtr);
////		}
////
////		sscanf((const char *) widthStr, "%d", &width);
////		sscanf((const char *) dposStr, "%d", &dpos);
////		xmlFree(dposStr);
////		xmlFree(widthStr);
////
////		//printf("psv list %s %d %c %d\n", name, width, *justPtr, dpos);
////
////		if (psvTableLen == psvTableAlloc) {  // need more room
////			psvTableAlloc = 2*psvTableAlloc + 1; // plus one since we start at zero
////			psvTable = (psvTableEntry *) 
////				realloc(psvTable, (psvTableAlloc)*sizeof(psvTableEntry));
////		}
////		psvTable[psvTableLen].name = name;   // no xmlFree(name); now owned by psvTable
////		psvTable[psvTableLen].width = width;
////		psvTable[psvTableLen].dpos = dpos;
////		psvTable[psvTableLen].just = *justPtr;
////		psvTableLen++;
////
////		psvPtr = xmlStrstr(psvPtr+5, BAD_CAST "\npsv ");
////		printf("psvPtr = %p\n", psvPtr);
////		
////	}
////
////}

static void adesProcessPsvWords(const StringVector &words) {
	int width, dpos;
	xmlChar *name;
	xmlChar *tagtype;
	if (words.size() != 11) {
		return; // throw an exception here
	}

	if (psvTableLen == psvTableAlloc) {  // need more room
		psvTableAlloc = 2*psvTableAlloc + 1; // plus one since we start at zero
		psvTable = (psvTableEntry *) 
			realloc(psvTable, (psvTableAlloc)*sizeof(psvTableEntry));
	}
	tagtype = xmlCharStrdup(words[2].c_str());  // note c_str memory is owned by words
	name = xmlCharStrdup(words[4].c_str());  // note c_str memory is owned by words
	sscanf((const char *) words[6].c_str(), "%d", &width);
	sscanf((const char *) words[10].c_str(), "%d", &dpos);

	psvTable[psvTableLen].tagtype = tagtype; // no xmlFree(name); now owned by psvTable
	psvTable[psvTableLen].name = name;   // no xmlFree(name); now owned by psvTable
	psvTable[psvTableLen].width = width;
	psvTable[psvTableLen].dpos = dpos;
	psvTable[psvTableLen].just = (const xmlChar) words[8][0];
	psvTableLen++;


}

//
// line is an input line
// delimiter is the character, usually ' ' or '|', on which to split
//
// returns a vector of the words found in the line
//
StringVector adesSplitLine(const xmlChar *line, xmlChar delimiter) {
	const xmlChar *ptr;
	xmlChar *temp, *xmldelimit;
	StringVector words;
	xmldelimit = xmlCharStrdup("x"); // need a string of length 1 for xmlStrstr
	xmldelimit[0] = delimiter; 
	ptr = line;
	do {
		if (*ptr != delimiter) {
			const xmlChar *ptr2 = xmlStrstr(ptr, xmldelimit);
			if (ptr2) {
				temp = xmlStrndup(ptr, ptr2 - ptr);
				//printf("%s\n", temp);
				words.push_back((const char *)temp);
				xmlFree(temp);
				ptr = ptr2;
			} else { // must be at EOS so grab last word
				temp = xmlStrdup(ptr);
				//printf("%s\n", temp);
				words.push_back((const char *)temp);
				xmlFree(temp);
				break;
			}
		}
	} while (*ptr++);
	xmlFree(xmldelimit);
	return words;
}

//
// a useful debugging function
//
static void printDictMap(const DictMap &dict, const char *name) {
	printf("DictMap %s ----------------------------------------------:\n", name);
	for (DictMap::const_iterator i=dict.begin(); i!=dict.end(); i++) {
		printf ("%s: [ ", i->first.c_str());
		for (StringVector::const_iterator j=i->second.begin();
				j!=i->second.end(); 
				j++) {
			printf("%s ", j->c_str());
		}
		printf ("]\n");
	}
}

static void printDictMapSet(const DictMapSet &dictset, const char *name) {
	printf("DictMapSet %s ----------------------------------------------:\n", name);
	for (DictMapSet::const_iterator i=dictset.begin(); i!=dictset.end(); i++) {
		printf ("%s: [ ", i->first.c_str());
		for (StringSet::const_iterator j=i->second.begin();
				j!=i->second.end(); 
				j++) {
			printf("%s ", j->c_str());
		}
		printf ("]\n");
	}
}


//
// used by adesReadTabls to build psvTable, allowedElementDict,
// and requiredElementDict. There is a step by the caller to
// remove duplicate elements in the Dicts.
//
static void adesProcessTableLine(const xmlChar *line) {
	StringVector words = adesSplitLine(line, (xmlChar) ' ');
	//printf("-->%ld\n", words.size());
	//for (StringVector::iterator i = words.begin(); i!= words.end(); i++) {
	//	printf("--> %s\n", i->c_str());
	//}
	static bool stillRequired = false;
	static std::string currentElement; // state preserved across calls!
	if (words.size()) { // skip empty lines
		if (words[0] == "element") {
			// need check for words length
			allowedElementDict[currentElement].push_back(words[1]);
			if (stillRequired and (words[3] == "required")) {
				requiredElementDict[currentElement].push_back(words[1]);
			}
		} else if (words[0] == "top") { // top means add new element to Dicts
			currentElement = words[1]; // check length! New elements are empty
			allowedElementDict[currentElement] = StringVector();
			requiredElementDict[currentElement] = StringVector();
			stillRequired = true;
		} else if (words[0] == "open") {
			// 'open' may be optional sequence or group, which
			// should be ignored for required.  Choice is not
			// required even if it is a required choice, because
			// there will be no common elements to the choice
			// 
			// need error checking for length of words
			if ((words[1] != "choice") || (words[3] != "required")) {
				stillRequired = false;
			}
		} else if (words[0] == "close") {
			stillRequired = true;
		} else if (words[0] == "psv") {
			adesProcessPsvWords(words);
		} 
	}
}

void printAdesTables() {

	printf("PSV Table ----------------------------------------------:\n");
	for (int i=0; i<psvTableLen; i++) {
	psvTableEntry *p = &psvTable[i];
	printf ("psv: %s %d %c %d\n", p->name, p->width, p->just, p->dpos);
	}

	printDictMap(allowedElementDict, "allowedElementDict");
	printDictMap(requiredElementDict, "requiredElementDict");
	printDictMapSet(allowedElementDictSet, "allowedElementDictSet");
	printDictMapSet(requiredElementDictSet, "requiredElementDictSet");
}

// 
// used by adesReadTables.  It removes the duplcates from a DictMap
// keeping the order.
//
static void removeDictMapDuplicates(DictMap &dict) {
//
// Now remove duplicates in the DictMap table lists, working
// through the list backwards.  This will not accomodate all
// possible structures (since I can write context-dependent
// ordering in the lists arbitrarily with <choice>), but
// in all of our cases eliminating duplicates working backwards
// will give an appropriate order.
//
	for (DictMap::iterator i=dict.begin(); i!=dict.end(); i++) {
		StringVector deduped;
		std::set<std::string> seen;
		for (StringVector::reverse_iterator j = i->second.rbegin();
				j != i->second.rend();
				j++) {
			if (seen.find(*j) == seen.end()) { // new one
				seen.insert(*j);
				deduped.push_back(*j);
			}
		}
		std::reverse(deduped.begin(), deduped.end());
		i->second = deduped;
	}
}

//
// used by adesReadTables.  It looks up a line at a time and then
// process the line with adesProcessTableLine.  It is separate mostly
// because of the epecial handling on the last line
//
// It finishes the de-duplication in the DictMaps after reading all
// the lines.
//
static void adesParseTableLines(const xmlChar *tablePtr, int tableLen) {
	//
	// Populates allowedElementDict from the string tablePtr of length tableLen
	//

	const xmlChar *psvPtr, *ptr2;
	xmlChar *line; // not const for free
	//fprintf(stdout, "%s\n",tablePtr);

	psvPtr = tablePtr;
	while ( (ptr2 = xmlStrstr(psvPtr+1, BAD_CAST "\n")) ) {
			line = xmlStrndup(psvPtr+1, ptr2 - psvPtr-1);
			adesProcessTableLine(line);
                        xmlFree(line);
		psvPtr = ptr2;
	}
	adesProcessTableLine(psvPtr+1); // last line may have no \n; don't copy

	removeDictMapDuplicates(allowedElementDict);
	removeDictMapDuplicates(requiredElementDict);
	
	makeHeaderInfo();
}

void adesReadTables(const char *adesmaster, const char *tableades) {
	//
	// reads the tableades.xslt transformation against adesmaster.xml 
	// to populate:
	// psvTable
	// allowedElementDict
	// requiredElementDict
	//
	// psv table lines look like this:
	// psv name <name> width <width> just <just> dpos <dpos>
	//
	// where <name> is an unquoted xml string
	//       <width> is a string with a small positive integer value
	//       <just> is "C", "R", "L" or "D"
	//       <dpos> is a small positive integer value
	//
	//       <dpos> is zero for "L", "R" and "C"
	//
	xsltStylesheetPtr cur = NULL;
	xmlDocPtr doc, res;

	int tableLen;
	int retval;
	xmlChar *tablePtr = NULL;

	cur = xsltParseStylesheetFile(BAD_CAST tableades);
	doc = ADESreadXML(adesmaster);
	res = xsltApplyStylesheet(cur, doc, NULL);

	retval =  xsltSaveResultToString(&tablePtr,
	                                 &tableLen,
	                                 res,
	                                 cur);

	if (retval != 0) {
		xmlFree(tablePtr);  // Free in reverse order of allocate for 
		tablePtr = NULL;    // best contiguous memeory.  Reset ptr's to NULL
		xmlFreeDoc(res);
		res = NULL;
		xmlFreeDoc(doc);
		doc = NULL;
		xsltFreeStylesheet(cur);
		cur = NULL;
		return;   // this is bad
	}
	adesFreePsvTable(); // start afresh
	allowedElementDict.clear();
	requiredElementDict.clear();

	//adesParsePsvTable(tablePtr, tableLen);
	adesParseTableLines(tablePtr, tableLen);

	xmlFree(tablePtr);  // Free in reverse order of allocate for 
	tablePtr = NULL;    // best contiguous memeory.  Reset ptr's to NULL
	xmlFreeDoc(res);
	res = NULL;
	xmlFreeDoc(doc);
	doc = NULL;
	xsltFreeStylesheet(cur);
	cur = NULL;

	//
	// finally create sets for all elements in allowedElementDict
	// which is the same as requiredElementDict.   This is used
	// by psvtoxml to check for keyword header type and general
	// validity.
	//

	for (DictMap::const_iterator x = allowedElementDict.begin();
	                             x != allowedElementDict.end(); x++) {
		allowedElementDictSet[x->first] = StringSet(allowedElementDict[x->first].begin(),
				   			    allowedElementDict[x->first].end());
		requiredElementDictSet[x->first] = StringSet(requiredElementDict[x->first].begin(),
							     requiredElementDict[x->first].end());
	}

}

