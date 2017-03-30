/*
 * include file for ades table readers
 *
 *
 */

#ifndef __ADESTABLES_H__
#define __ADESTABLES_H__

#ifdef __cplusplus

#include <map>
#include <set>
#include <vector>
#include <algorithm>

typedef std::vector<std::string> StringVector;
typedef std::set<std::string> StringSet;
typedef std::map<std::string, std::vector<std::string> > DictMap;
typedef std::map<std::string, std::set<std::string> > DictMapSet;
extern DictMap allowedElementDict;
extern DictMap requiredElementDict;
extern DictMapSet allowedElementDictSet;
extern DictMapSet requiredElementDictSet;

typedef struct  {
	std::string name;
	int width;
	int dpos;
	bool seen;
	char fmt;
} HeaderStruct;
extern std::map< std::string, std::vector<HeaderStruct> > BaseHeaderInfoMap;

StringVector adesSplitLine(const xmlChar *line, xmlChar delimiter);

#endif /* __cplusplus */

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#define ADES_TABLES Stringify(ADES_PATH)  "/../xslt/util/tableades.xslt"

typedef struct {
	xmlChar *tagtype; // struct owns this memory
	xmlChar *name; // struct owns this memory
	int width;
	int dpos;
	xmlChar just; 
} psvTableEntry;

extern int psvTableLen;
extern psvTableEntry *psvTable;



void printAdesTables();

void adesReadTables(const char *adesmaster, const char *tableades);



#ifdef __cplusplus
}
#endif /* __cplusplus */
#endif /* __ADESTABLES_H__ */
