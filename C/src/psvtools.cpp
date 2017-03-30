#include <ades.h>


//-------------------------------------------------------------------------
//    Routines to write nodes in PSV format.
//-------------------------------------------------------------------------
//
//  write a valid obsContext in PSV format
//    elements with no text are  # <name>
//    elements with text are     ! <name> <text>
//    It is so, but not used here, that the 
//    # nodes all are direct children and the ! nodes
//    are children of a # node.  The validation 
//    ensures this beforehand.
//
//    The input node is assumed to be a obsContext node
//  
//    


#define MAX_ADES_WIDTH 200
// go heaad and count them:
static char spaces[] = "                                        " 
                       "                                        " 
                       "                                        " 
                       "                                        " 
                       "                                        ";
// need the trailing null too
static const int nspaces=MAX_ADES_WIDTH; // maximum field width in ades.
static const char decimalPoint[] = ".";
static const char pipestr[] = "|"; // avoid conflict with man (2) pipe
static const char colon[] = ":";

static int lineNo = 0; // for PSV parsing


//----------------------------------------------------------------------
//
// Process a list of data nodes, all of the same type.  This is the 
// meat of the action
//
//
// This helper function modifies its argument to replace trailing " " 
// with "\0" in place.  It modifies memory owned by someone else
// but is fairly safe in context.  Don't use this if you are not
// about to to release the memory anyway.  
//
// A safer version would make a copy like regularizeWhhiteSpace.
//
static void removeTrailingWhiteSpace(xmlChar *textstr) {
        xmlChar *end ;
	//printf("%d %s\n", xmlStrlen(textstr), textstr);
        if (textstr == NULL) return; // nothing gets nothing
        for (end=textstr + xmlStrlen(textstr) - 1; end != textstr; end--) {
		//printf ("The end is %d\n", *end);
                if (*end != ' ') {
                        break;
                } else {
			*end = '\0'; // replace trailing ' ' with EOS
		}
        }
	//printf("%d %s\n", xmlStrlen(textstr), textstr);
}

//-----------------------------------------------------------------------
//
// ElementStack class implementation
//

//typedef std::pair<std::string, std::string> PropPair;
//typedef std::vector<PropPair> PropVec;

//class ElementStackException: public std::exception {
	ElementStackException::ElementStackException(const char *s):msg(s) {}
	const char * ElementStackException::what() const throw() { // need override for c++11
		return msg.c_str();
	}
	ElementStackException::~ElementStackException() throw() {}

//class ElementStack {
//private:
	//ElementStack &operator=(const ElementStack &) = delete;
	//ElementStack(const ElementStack &) = delete;
	ElementStack &ElementStack::operator=(const ElementStack &a) { return *this; }
	ElementStack::ElementStack(const ElementStack &) {}
	void ElementStack::_addProperties(xmlNode *node, const PropVec &properties) {
		for (PropVec::const_iterator i=properties.begin(); 
				i!=properties.end(); i++) {
			xmlNewProp(node, BAD_CAST i->first.c_str(), 
					 BAD_CAST i->second.c_str());
		}
	}
//public:
	ElementStack::ElementStack() {}
	ElementStack::ElementStack(const xmlChar *tag, const xmlChar *text) {
		_elementStack.push_back(xmlNewNode(NULL, tag));
	}
	ElementStack::ElementStack(const xmlChar *tag, const xmlChar *text, const PropVec &properties) {
		_elementStack.push_back(xmlNewNode(NULL, tag));
		_addProperties(_elementStack.back(), properties);
	}
	void ElementStack::print(const char *description) {
		printf ("elementStack %s: ", description);
		for (std::vector<xmlNode *>::const_iterator i = _elementStack.begin();
				i!= _elementStack.end(); i++) {
			//printf(" %p %s", *i, (*i)->name);
			printf(" %s",  (*i)->name);
		}
		printf("\n");
	}
	void ElementStack::pop() {
		if (_elementStack.size() < 2) {
			throw ElementStackException("ElemenStack is too short to pop\n");
		}
		_elementStack.pop_back();
	}
	void ElementStack::addElement(xmlNode *element) { // ElementStack owns the memory
		if (_elementStack.size() == 0) {
			throw ElementStackException("zero elementStack in addElement\n");
		}
		xmlAddChild(_elementStack.back(), element);
	}
	void ElementStack::addElementList(std::vector<xmlNode *> elements) { // ElementStack owns all the memory
		for (std::vector<xmlNode *>::const_iterator i= elements.begin();
				i!=elements.end(); i++) {
			addElement(*i);
		}
	}
	xmlNode *ElementStack::add(const xmlChar *tag, const xmlChar *text) {
		if (_elementStack.size() == 0) {
			throw ElementStackException("zero elementStack in add\n");
		}
		return xmlNewTextChild(_elementStack.back(), NULL, tag, text);
	}
	xmlNode *ElementStack::add(const xmlChar *tag, const xmlChar *text, const PropVec &properties) {
		if (_elementStack.size() == 0) {
			throw ElementStackException("zero elementStack in add\n");
		}
		xmlNode *n =  xmlNewTextChild(_elementStack.back(), NULL, tag, text);
		_addProperties(n, properties);
		return n;
	}
	void ElementStack::addPush(const xmlChar *tag, const xmlChar *text) {
		if (_elementStack.size() == 0) {
			_elementStack.push_back(xmlNewNode(NULL, tag));
			return;
		}
		xmlNode *x = add(tag, text);
		_elementStack.push_back(x);
	}
	void ElementStack::addPush(const xmlChar *tag, const xmlChar *text, const PropVec &properties ) {
		if (_elementStack.size() == 0) {
			_elementStack.push_back(xmlNewNode(NULL, tag));
			_addProperties(_elementStack.back(), properties);
			return;
		}
		xmlNode *x = add(tag, text, properties);
		_elementStack.push_back(x);
	}
	void ElementStack::addPopPush(const xmlChar *tag, const xmlChar *text) {
		pop();
		addPush(tag, text);
	}
	void ElementStack::addPopPush(const xmlChar *tag, const xmlChar *text, const PropVec &properties) {
		pop();
		addPush(tag, text, properties);
	}
	xmlDocPtr ElementStack::copyDoc(unsigned int n) {
		//
		// creates a new doc with a copy of <node>
		// as the root element.  <node> is copied
		// recursively.  The returned xmlDoc owns
		// all the memory.   This is a deep copy 
		// of node, and the input node may be freed
		// afterwards with no consequences.
		//
		if (n>_elementStack.size()) {;
			throw ElementStackException("no such n in copyDoc");
		}
		xmlDocPtr newDoc;
		xmlNodePtr copyNode = xmlCopyNode(_elementStack[n], 1); // 1 is deep copy;
		xmlUnlinkNode(copyNode);                    // remove copy from old doc (none)
		newDoc = xmlNewDoc(BAD_CAST "1.0");         // version 1.0 document
		xmlDocSetRootElement(newDoc, copyNode);    // set as root
		return newDoc;
	}
	xmlDocPtr ElementStack::takeDocAndClear() {
		xmlDocPtr newDoc;
		newDoc = xmlNewDoc(BAD_CAST "1.0");         // version 1.0 document
		xmlDocSetRootElement(newDoc, _elementStack[0]);    // set as root
		_elementStack.clear(); // you own it now
		return newDoc;
	}
	const xmlNode *ElementStack::pointToNode(unsigned int n) { // ElementStack still owns memory after this
		if (n>_elementStack.size())  {
			throw ElementStackException("no such n in pointToNode");
		}
		return _elementStack[n];
	}
	void ElementStack::clear() {
		if (_elementStack.size()) {
			xmlFreeNode(_elementStack[0]); // always present; free recursively
		}
	}
	ElementStack::~ElementStack() {
		_elementStack.clear();
	}
//};
//
//-----------------------------------------------------------------------
//

//
//-----------------------------------------------------------------------
//Routines for psvtoxml conversion
//

enum PSVLineType {
	TOP_HEADER_LINE,     // # <element> <restoflineisusuallyblank>
	SECOND_HEADER_LINE,  // # <element> <restofline>
	KEYWORD_RECORD_LINE, // PSV list of keywords
	DATA_RECORD_LINE,    // PSV list of data
	BLANK_LINE,
	ILLEGAL_LINE
};

//
// KEYWORD_RECORD_LINE has a StringVector whose entries are the 
// psv entries and the last element it the identified tag
//

//
// DATA_RECORD_LINE has a StringVector whose entries are the
// psv entries.  Its length is one less than the StringVector
// for the KEYWORD_RECORD_LINE
//
// Heuristic:  Every valid data record line has a ':'.  No
//             keyword record line has a ':'



enum PSVState {
	EMPTY_STATE,
	OBSCONTEXT_STATE,
	FIRST_OBSDATA_STATE,
	OBSDATA_STATE,
	FIRST_DATA_STATE,
	DATA_STATE
};

typedef struct {
	StringVector words;
	PSVLineType linetype;
} PSVLineStruct;

//-----------------------------------------------------------------------
//
// state tables for psv state machine
//

typedef PSVState ActionFunc(const PSVState &state, 
			    const PSVState &nextstate, 
		            const PSVLineType &record, 
			    const StringVector &fields,
			    int action); // action is really a pointer to an overloaded 
                                         // member function but I'm too lazy right now
					 // to figure out how to make that work the way
					 // it does in python and there are only a couple
					 // of cases anyway
ActionFunc errorAction;

ActionFunc firstObsBlockAction;
ActionFunc closeObsBlockOpenObsBlockAction;
ActionFunc closeDataOpenObsBlockAction;
ActionFunc obsContextAction;
ActionFunc subObsContextAction;
ActionFunc keywordHeaderAction;
ActionFunc openDataKeywordHeaderAction;
ActionFunc closeDataKeywordHeaderAction;
ActionFunc closeObsBlockKeywordHeaderAction;
ActionFunc dataAction;
ActionFunc firstObsDataAction;
ActionFunc firstDataAction;


typedef std::pair<PSVState, ActionFunc *> StatePair;
typedef std::vector<StatePair>  StateEntry;
typedef std::vector<StateEntry> StateTable;

StateTable initializeStateTable() { // C++ makes thie initialization hard
	StateTable table(6); // six entries

	table[EMPTY_STATE] = StateEntry(4);
	table[EMPTY_STATE][TOP_HEADER_LINE]     = StatePair(OBSCONTEXT_STATE, firstObsBlockAction);
	table[EMPTY_STATE][SECOND_HEADER_LINE]  = StatePair(EMPTY_STATE,      errorAction);
	table[EMPTY_STATE][KEYWORD_RECORD_LINE] = StatePair(FIRST_DATA_STATE, openDataKeywordHeaderAction);
	table[EMPTY_STATE][DATA_RECORD_LINE]    = StatePair(EMPTY_STATE,      errorAction);
	
	table[OBSCONTEXT_STATE] = StateEntry(4);
	table[OBSCONTEXT_STATE][TOP_HEADER_LINE]     = StatePair(OBSCONTEXT_STATE,    obsContextAction);
	table[OBSCONTEXT_STATE][SECOND_HEADER_LINE]  = StatePair(OBSCONTEXT_STATE,    subObsContextAction);
	table[OBSCONTEXT_STATE][KEYWORD_RECORD_LINE] = StatePair(FIRST_OBSDATA_STATE, keywordHeaderAction);
	table[OBSCONTEXT_STATE][DATA_RECORD_LINE]    = StatePair(EMPTY_STATE,         errorAction);
	
	table[FIRST_OBSDATA_STATE] = StateEntry(4); // obsData inside obsBlock
	table[FIRST_OBSDATA_STATE][TOP_HEADER_LINE]     = StatePair(EMPTY_STATE,   errorAction);
	table[FIRST_OBSDATA_STATE][SECOND_HEADER_LINE]  = StatePair(EMPTY_STATE,   errorAction);
	table[FIRST_OBSDATA_STATE][KEYWORD_RECORD_LINE] = StatePair(EMPTY_STATE,   errorAction);
	table[FIRST_OBSDATA_STATE][DATA_RECORD_LINE]    = StatePair(OBSDATA_STATE, firstObsDataAction);
	
	table[OBSDATA_STATE] = StateEntry(4); // obsData inside obsBlock
	table[OBSDATA_STATE][TOP_HEADER_LINE]     = StatePair(OBSCONTEXT_STATE, closeObsBlockOpenObsBlockAction);
	table[OBSDATA_STATE][SECOND_HEADER_LINE]  = StatePair(EMPTY_STATE,      errorAction);
	table[OBSDATA_STATE][KEYWORD_RECORD_LINE] = StatePair(FIRST_DATA_STATE, closeObsBlockKeywordHeaderAction);
	table[OBSDATA_STATE][DATA_RECORD_LINE]    = StatePair(OBSDATA_STATE,    dataAction);
	
	table[FIRST_DATA_STATE] = StateEntry(4); // outside obsBlock
	table[FIRST_DATA_STATE][TOP_HEADER_LINE]     = StatePair(EMPTY_STATE, errorAction);
	table[FIRST_DATA_STATE][SECOND_HEADER_LINE]  = StatePair(EMPTY_STATE, errorAction);
	table[FIRST_DATA_STATE][KEYWORD_RECORD_LINE] = StatePair(EMPTY_STATE, errorAction);
	table[FIRST_DATA_STATE][DATA_RECORD_LINE]    = StatePair(DATA_STATE,  firstDataAction);
	
	table[DATA_STATE] = StateEntry(4); // outside obsBlock
	table[DATA_STATE][TOP_HEADER_LINE]     = StatePair(OBSCONTEXT_STATE, closeDataOpenObsBlockAction);
	table[DATA_STATE][SECOND_HEADER_LINE]  = StatePair(EMPTY_STATE,      errorAction);
	table[DATA_STATE][KEYWORD_RECORD_LINE] = StatePair(FIRST_DATA_STATE, closeDataKeywordHeaderAction);
	table[DATA_STATE][DATA_RECORD_LINE]    = StatePair(DATA_STATE,       dataAction);
	
	return table;
};

StateTable stateTransitions = initializeStateTable();
PSVState psvState = EMPTY_STATE;

ElementStack stateMachineElementStack;

//
// end of state tables for psv state machine
//
//-----------------------------------------------------------------------
//
// ActionFunc's for state machine
//
std::string stackStateHeaderType;
StringVector stackStateHeaderVals;
std::vector<int> stackStateHeaderIndex;

//#define DEBUG_PRINT(s) printf("%d %d ", state, nextstate); stateMachineElementStack.print("s");
#define DEBUG_PRINT(s)


PSVState errorAction(const PSVState &state, 
		     const PSVState &nextstate, 
		     const PSVLineType &record, 
		     const StringVector &fields,
		     int action) {

	DEBUG_PRINT("errorAction called") ;
	return nextstate;
}
PSVState firstObsBlockAction(const PSVState &state, 
		             const PSVState &nextstate, 
		             const PSVLineType &record, 
		             const StringVector &fields,
			     int action) {

	DEBUG_PRINT("firstObsBlockAction called");
	stateMachineElementStack.addPush(BAD_CAST "obsBlock");
	stateMachineElementStack.addPush(BAD_CAST "obsContext");
	return obsContextAction(state, nextstate, record, fields, 1);
}
PSVState closeObsBlockOpenObsBlockAction(const PSVState &state, 
		             		 const PSVState &nextstate, 
		             		 const PSVLineType &record, 
		             		 const StringVector &fields,
			     	 	 int action) {

	DEBUG_PRINT("closeObsBlockOpenObsBlockAction called");
	stateMachineElementStack.pop(); // close last element
	stateMachineElementStack.pop(); // close ObsData
	stateMachineElementStack.pop(); // close obsBlock
	return firstObsBlockAction(state, nextstate, record, fields, 0);
}
PSVState closeDataOpenObsBlockAction(const PSVState &state, 
		             	     const PSVState &nextstate, 
		             	     const PSVLineType &record, 
		             	     const StringVector &fields,
			     	     int action) {

	DEBUG_PRINT("closeDataOpenObsBlockAction called");
	stateMachineElementStack.pop(); // close last element
	return firstObsBlockAction(state, nextstate, record, fields, 0);
}
PSVState obsContextAction (const PSVState &state, 
		           const PSVState &nextstate, 
		           const PSVLineType &record, 
		           const StringVector &fields,
			   int action) {

	DEBUG_PRINT("obsContextAction called");
	if (action == 1) {
		if (fields[1].length() == 0) {
			stateMachineElementStack.addPush(BAD_CAST fields[0].c_str());
		} else {
			stateMachineElementStack.addPush(BAD_CAST fields[0].c_str(),
					                 BAD_CAST fields[1].c_str());
		}
		//stateMachineElementStack.addPush(BAD_CAST fields[0].c_str(), BAD_CAST fields[1].c_str());
	} else {
		if (fields[1].length() == 0) {
			stateMachineElementStack.addPopPush(BAD_CAST fields[0].c_str());
		} else {
			stateMachineElementStack.addPopPush(BAD_CAST fields[0].c_str(),
					                    BAD_CAST fields[1].c_str());
		}
		//stateMachineElementStack.addPopPush(BAD_CAST fields[0].c_str());
	}
	return nextstate;
}
PSVState subObsContextAction(const PSVState &state, 
		             const PSVState &nextstate, 
		             const PSVLineType &record, 
		             const StringVector &fields,
			     int action) {

	DEBUG_PRINT("subObsContextAction called");
	if (fields[1].length() == 0) {
		stateMachineElementStack.add(BAD_CAST fields[0].c_str());
	} else {
		stateMachineElementStack.add(BAD_CAST fields[0].c_str(), BAD_CAST fields[1].c_str());
	}
	//stateMachineElementStack.add(BAD_CAST fields[0].c_str(), BAD_CAST fields[1].c_str());
	return nextstate;
}
PSVState keywordHeaderAction(const PSVState &state, 
		             const PSVState &nextstate, 
		             const PSVLineType &record, 
		             const StringVector &fields,
			     int action) {

	DEBUG_PRINT("keywordHeaderAction called");
	std::string oldHeaderType = stackStateHeaderType;
	stackStateHeaderType = fields.back();
	if ( (oldHeaderType.size() != 0) && (oldHeaderType != stackStateHeaderType))  {
		// error, but this path can't be reached with the new 
		// semantics.  A new keyword header closes the obsblock;
	}
	stackStateHeaderVals = fields;
	stackStateHeaderVals.pop_back(); // take off last element
	//
	// now get order right
	//     This is an n^2 algorithm but it only happens on header
	//     lines, which happen once or twice.
	//
	stackStateHeaderIndex = std::vector<int>();
	const StringVector &a = allowedElementDict[stackStateHeaderType];
	for (StringVector::const_iterator i = a.begin(); i!=a.end()  ; i++) {
                unsigned int pos = std::find(fields.begin(), fields.end(), *i) - fields.begin();
		//printf (" pos is %d for %s\n",pos,i->c_str());
		if (pos < fields.size()) {
			stackStateHeaderIndex.push_back(pos);
		}
	}
	return nextstate;
}
PSVState openDataKeywordHeaderAction(const PSVState &state, 
		        	     const PSVState &nextstate, 
		        	     const PSVLineType &record, 
		        	     const StringVector &fields,
			     	     int action) {

	DEBUG_PRINT("openDataKeywordHeaderAction called");
	stackStateHeaderType = fields.back();
	stackStateHeaderVals = fields;
	stackStateHeaderVals.pop_back(); // take off last element
	stackStateHeaderIndex = std::vector<int>(fields.size());
	//
	// now get order right
	//     This is an n^2 algorithm but it only happens on header
	//     lines, which happen once or twice.
	//
	stackStateHeaderIndex = std::vector<int>();
	const StringVector &a = allowedElementDict[stackStateHeaderType];
	for (StringVector::const_iterator i = a.begin(); i!=a.end()  ; i++) {
                unsigned int pos = std::find(fields.begin(), fields.end(), *i) - fields.begin();
		//printf (" pos is %d for %s\n",pos,i->c_str());
		if (pos < fields.size()) {
			stackStateHeaderIndex.push_back(pos);
		}
	}
	return nextstate;
}
PSVState closeDataKeywordHeaderAction(const PSVState &state, 
		        	      const PSVState &nextstate, 
		        	      const PSVLineType &record, 
		        	      const StringVector &fields,
			     	      int action) {

	DEBUG_PRINT("closeDataKeywordHeaderAction called");
	stateMachineElementStack.pop();
	return openDataKeywordHeaderAction(state, nextstate, record, fields, 0);
}
PSVState closeObsBlockKeywordHeaderAction(const PSVState &state, 
		      			  const PSVState &nextstate, 
		      			  const PSVLineType &record, 
		      			  const StringVector &fields,
			     	          int action) {

	DEBUG_PRINT("closeObsBlockKeywordHeaderAction called");
	stateMachineElementStack.pop(); // close last element
	stateMachineElementStack.pop(); // close obsData
	stateMachineElementStack.pop(); // close obsBlock
	return openDataKeywordHeaderAction(state, nextstate, record, fields, 0);
}
PSVState dataAction(const PSVState &state, 
		    const PSVState &nextstate, 
		    const PSVLineType &record, 
		    const StringVector &fields,
		    int action) { // addPopPush is 0, addPush is 1

	DEBUG_PRINT("dataAction called");
	if ( stackStateHeaderVals.size() < fields.size() ) {
		// mismatch between records; throw exception
	}
	if (action) { // 1 just opens new
		stateMachineElementStack.addPush(BAD_CAST stackStateHeaderType.c_str());
	} else { // closes old and opens new
		stateMachineElementStack.addPopPush(BAD_CAST stackStateHeaderType.c_str());
	}
	// add in order
	for (unsigned int i=0; i<fields.size(); i++) {
		int j = stackStateHeaderIndex[i];
		stateMachineElementStack.add(BAD_CAST stackStateHeaderVals[j].c_str(),
					     BAD_CAST fields[j].c_str());
	}
	
	return nextstate;
} 
PSVState firstObsDataAction(const PSVState &state, 
			    const PSVState &nextstate, 
			    const PSVLineType &record, 
			    const StringVector &fields,
			    int action) {

	DEBUG_PRINT("firstObsDataAction called");
	stateMachineElementStack.pop(); // close last element in obsContext
	stateMachineElementStack.pop(); // close obsContext
	stateMachineElementStack.addPush(BAD_CAST "obsData");
	// same as dataAction but use addPush
	return dataAction(state, nextstate, record, fields, 1);
}
PSVState firstDataAction(const PSVState &state, 
			 const PSVState &nextstate, 
			 const PSVLineType &record, 
			 const StringVector &fields,
		         int action) {

	// same as dataAction but use addPush instead of addPopPush
	DEBUG_PRINT("firstDataAction called");
	return dataAction(state, nextstate, record, fields, 1);
}
//
// ActionFunc's for state machine
//
//-----------------------------------------------------------------------

//
// psvSpitPipe splits a psv pipe into a StringVector.
// Beginning and ending white space is squeezed out
//
// "||" is two words "" and ""
// "| |" is two words "" and ""
// "  rs |  sd   |" is two words "rs" and "sd"
// "  rs ||  sd   |" is three  words "rs", "", and "sd"
//
StringVector psvSplitPipe(const xmlChar *line) {
	const xmlChar *ptr;
	const xmlChar *ptr2;
	xmlChar *temp;
	xmlChar *wstemp;
	StringVector words;
	ptr = line;
	while (ptr) {
		ptr2 = xmlStrstr(ptr, BAD_CAST pipestr);
		//printf ("%s %p %p\n", ptr, ptr, ptr2);
		if (ptr2) {
			temp = xmlStrndup(ptr, ptr2 - ptr);
			wstemp = regularizeWhiteSpace(temp);
			ptr = ptr2 + 1;
		} else {
			temp = xmlStrdup(ptr);
			wstemp = regularizeWhiteSpace(temp);
			ptr = ptr2;
		}
		if (wstemp) { // wstemp is NULL for empty strings
			words.push_back((const char *)wstemp);
		} else {
			words.push_back("");
		}
		xmlFree(wstemp);
		xmlFree(temp);
	}
	return words;
}


//
// parsePSVLines identifies line linetype and returns a PSVLineStruct
//

#define MAX_ERR_SIZE 1024
PSVLineStruct  parsePSVLine(const xmlChar *line) {
	const xmlChar *pos;
	char errBuf[MAX_ERR_SIZE+1]; 
	StringVector words;
	PSVLineStruct retval;
	retval.linetype = BLANK_LINE;

	//
	// return BLANK_LINE if NULL
	//
	if (!line) return retval;

	xmlChar *regline = regularizeWhiteSpace(line);
	//
	// return BLANK_LINE if only spaces
	//
	if (xmlStrlen(regline) == 0) {
		xmlFree(regline);
		return retval;
	}

	switch (regline[0]) {
		case (xmlChar) '#': // TOP_HEADER_LINE is # <string> <restofline>
		                    // returns linetype = TOP_HEADER_LINE
		                    // returns words[1] = <string>
		                    // returns words[2] = <restofline>
			words = adesSplitLine(&regline[1], (xmlChar) ' ');
			if (strlen(words[0].c_str()) == 0) { // real error if line has just #
				snprintf(errBuf, MAX_ERR_SIZE, "Illegal line %d:%s", lineNo, line);
				retval.words.push_back(errBuf);
				retval.linetype = ILLEGAL_LINE;
				xmlFree(regline);
				return retval; // freak out later
			}
			retval.linetype = TOP_HEADER_LINE;
			retval.words.push_back(words[0].c_str());
			// start at character after first word
			pos = (xmlStrstr(&line[1], BAD_CAST words[0].c_str())) + words[0].size();
			while (*pos == (xmlChar) ' ') pos++;
			retval.words.push_back((const char *) pos); // rest of line
			break;
		case (xmlChar) '!': // SECOND_HEADER_LINE is !<string> <restofline>
		                    // returns linetype = SECOND_HEADER_LINE
		                    // returns words[1] = <string>
			words = adesSplitLine(&regline[1], (xmlChar) ' ');
			if (strlen(words[0].c_str()) == 0) { // real error if line has just #
				snprintf(errBuf, MAX_ERR_SIZE, "Illegal line %d:%s", lineNo, line);
				retval.words.push_back(errBuf);
				retval.linetype = ILLEGAL_LINE;
				xmlFree(regline);
				return retval; // freak out later
			}
			retval.linetype = SECOND_HEADER_LINE;
			// start at character after first word
			retval.words.push_back(words[0].c_str());
			pos = (xmlStrstr(&line[1], BAD_CAST words[0].c_str())) + words[0].size();
			while (*pos == (xmlChar) ' ') pos++;
			retval.words.push_back((const char *) pos); // rest of line
			break;
		default:    // either KEYWORD_RECORD_LINE or DATA_RECORD_LINE is psv
			//retval.words = psvSplitPipe(regline);
			//retval.words.push_back ((const char *)regline);
			//
			retval.words = psvSplitPipe(regline);
			retval.linetype = DATA_RECORD_LINE;
			//
			//  now check for KEYWORD_RECORD_LINE
			//  This will add the tag to the end 
			//  It's quite a complicated check
			//
			// first heuristic DATA lines must contain ':'
			// because they must contain obsTime.  
			//
			if (xmlStrstr(line, BAD_CAST colon) == NULL ) { 
				retval.linetype = KEYWORD_RECORD_LINE;
				//
				// now find out the tag name and
				// append it to the end of the fields
				//
				// the record must have all required words
				// and only allowed words.
				// 
				std::string tag;
				StringSet wordSet(retval.words.begin(), 
					  	 retval.words.end());
				StringVector &allowed = allowedElementDict["ades"];
				for (StringVector::const_iterator possible = allowed.begin(); 
						possible != allowed.end(); possible++) {
					//StringSet allowSet(allowedElementDict[*possible].begin(),
					//	           allowedElementDict[*possible].end());
					//StringSet requireSet(requiredElementDict[*possible].begin(),
					//	             requiredElementDict[*possible].end());
					StringSet &allowSet = allowedElementDictSet[*possible];
					StringSet &requireSet = requiredElementDictSet[*possible];
					bool wordsInAllowed = std::includes(allowSet.begin(), allowSet.end(),
									    wordSet.begin(), wordSet.end());
					bool requiredInWords = std::includes(wordSet.begin(), wordSet.end(),
									     requireSet.begin(), requireSet.end());
					if (wordsInAllowed && requiredInWords) {
						//
						//printf("tag is %s\n", possible->c_str());
						//
						tag = *possible;
						//
						// could break here but could also test for
						// multiple matches, which should not happen
					}


					//
					// to see the differences:
					// 
					//StringSet outset; 
					//StringSet outset2; 
					//set_difference(wordSet.begin(), wordSet.end(),
					//	       allowSet.begin(), allowSet.end(), 
					//	       std::inserter(outset, outset.begin()));
					//set_difference(requireSet.begin(), requireSet.end(),
					//	       wordSet.begin(), wordSet.end(), 
					//	       std::inserter(outset2, outset2.begin()));

					//printf("outset.size, outset2.sise = %ld %ld\n", outset.size(), outset2.size());
					//StringSet::const_iterator is;
					//for (is = wordSet.begin(); is !=wordSet.end(); is++) {
					//	printf("  wordSet: %s\n", is->c_str());
					//}
					//for (is = allowSet.begin(); is !=allowSet.end(); is++) {
					//	printf("  allowSet: %s\n", is->c_str());
					//}
					//for (is = requireSet.begin(); is !=requireSet.end(); is++) {
					//	printf("  requireSet: %s\n", is->c_str());
					//}
					//for (is = outset.begin(); is != outset.end(); is++) {
					//	printf("  outset: %s\n", is->c_str());
					//}
					//for (is = outset2.begin(); is != outset2.end(); is++) {
					//	printf("  outset2: %s\n", is->c_str());
					//}
					//printf("possible is %s\n", possible->c_str());
					//if ((outset.size() == 0) && (outset2.size() == 0)) {
					//	printf("tag is %s\n", possible->c_str());
					//	tag = *possible;
					//}
				}
				if (tag.size() == 0) {
					snprintf(errBuf, MAX_ERR_SIZE, "Illegal line %d matches no tag:%s", lineNo, line);
					retval.words = StringVector();
					retval.words.push_back(errBuf);
					retval.linetype = ILLEGAL_LINE;
				}
				retval.words.push_back(tag);
			}

			break;
	}
	xmlFree(regline);
	return retval;
}
#define MAX_PSV_LINE_CHUNK 64
xmlChar *readPsvLineFromFile(FILE *f, const char *encoding) { 
	// encoding is ignored here but we need to do a 
	// conversion if it is now utf8

	// note fgets looks for '\n' which is not a really
	// good thing in EBCDIC encodings

	char buf[MAX_PSV_LINE_CHUNK + 1]; 
	char *result;
	xmlChar *line = xmlCharStrdup(""); 
	while ( (result = fgets(buf, MAX_PSV_LINE_CHUNK, f)) ) {
		int len = strlen(result);
		if (result[len-1]== '\n') {
			result[len-1]=0;
			line = xmlStrcat(line, BAD_CAST result);
			return line;
		}
		line = xmlStrcat(line, BAD_CAST result);
	}
	if (xmlStrlen(line) != 0) return line;
	return NULL;
}

//end of routines for psvtoxml conversion
//-----------------------------------------------------------------------
//

//-----------------------------------------------------------------------
//Routines for xmltopsv conversion

// be careful with memory management for the points in these types
typedef std::map<std::string, xmlChar *> SubDict; // maps from tag to data AS POINTER
typedef std::vector<SubDict> DataDictList;
void likeTypeDataNodesToPsv(const xmlNodePtr begin, const xmlNodePtr end, FILE *outfile) {
	xmlNode *c_node;
	if (begin == end) return; // not supposed to be this way
	std::string headerType((const char *) begin->name);

	// initilize headerInfo and headerDict to point into it
	std::vector<HeaderStruct> headerInfo = BaseHeaderInfoMap[headerType]; // make a copy
	std::map<std::string, HeaderStruct*> headerDict; // reference semantics is your friend
	for (size_t i=0; i<headerInfo.size(); i++) { // point into our copy
		headerDict[headerInfo[i].name] = &headerInfo[i];
	}

        DataDictList dataDictList;

	//
	// now pick up all the data in the list
	//
	for (c_node=begin; c_node != end; c_node = c_node->next) {
		if (c_node->type == XML_ELEMENT_NODE) { // will all be the same type here
			SubDict subDict;
			for (xmlNode *e_node = c_node->children; e_node; e_node = e_node->next) {
				if (e_node->type == XML_ELEMENT_NODE) {
					xmlChar *text = xmlNodeGetRegularizedText(e_node); 
					if (text) {
						if (xmlStrlen(text)) {
							subDict[(const char *)e_node->name] = text;
							//xmlFree(text);  // subDict owns memory
						} else {
							xmlFree(text);  // ignore LocalUse
						}
					}
				}
			}
			// 
			// adjust the headerInfo if a new item is found
			// 
			for (SubDict::iterator i=subDict.begin(); i!=subDict.end(); i++) {
				//
				// if a new tag is found, add to headerInfo and headerDict
				//
				std::map<std::string, HeaderStruct*>::iterator j = headerDict.find(i->first);
				if (j == headerDict.end()) { // we have a new one
					HeaderStruct newOne;
					newOne.name = i->first; // its name is easy
					                        // width is UTF8 longest of name, value 
					int w = xmlUTF8Strlen(BAD_CAST i->first.c_str()); //blech
					if (w < xmlUTF8Strlen(i->second)) w = xmlUTF8Strlen(i->second);
					newOne.width = w;

					int n = xmlUTF8Strloc(i->second, BAD_CAST decimalPoint);
					if (n < 0) { // no decimal point so chose 'R'
						newOne.dpos = 0;
						newOne.fmt = 'R';
					} else {     // decimal point (or period??? but choose D
						newOne.dpos = n;
						newOne.fmt = 'D';
					}
					newOne.seen = true; // we just saw it

					std::vector<HeaderStruct>::iterator it = headerInfo.end() - 1;
					headerInfo.insert(it, newOne);
					for (size_t i=0; i<headerInfo.size(); i++) { // update our pointers
						headerDict[headerInfo[i].name] = &headerInfo[i];
					}
				//
				// and existing tag is marked as seen and its justification is checked
				// 
				} else {                     // mark as seen (probably already is)
					char format = j->second->fmt;
					if (!j->second->seen && (format == 'R' || format == 'L')) {  // check format
						int n = xmlUTF8Strloc(i->second, BAD_CAST decimalPoint);
						if (n >= 0) { // decimal point (or period??) so chose 'D'
							j->second->dpos  = n;
							j->second->fmt  = 'D';
						}
					}
					j->second->seen = true;
					//
					// now see if it's wider than it was
					// 
					paddedStruct *p = adesApplyPaddingAndJustification (
							   i->second,    // xmlChar *name in SubDict
							   j->second->width,
							   j->second->fmt,
							   j->second->dpos
							);
					j->second->width = p->width;
					j->second->dpos  = p->dpos;
					free(p->str); // hard to use C++ since xmlChar *
					free(p);

				}
			}
			dataDictList.push_back(subDict); // dataDictList owns memory
		}
	}
	//
	// now print out the data lines
	//
	
	//
	// first print the header, unless there are no data elements
	//
	if (dataDictList.begin() != dataDictList.end()) {
		//
		// print the header
		//
		xmlChar *sline = xmlCharStrdup("");
		int first = true;
		for (std::vector<HeaderStruct>::iterator j=headerInfo.begin();
				j!=headerInfo.end(); j++) {
			if (j->seen) { // don't print if never seen
				if (first) {
					first = false;
				} else {
					sline = xmlStrcat(sline, BAD_CAST pipestr);
				}
				paddedStruct *p = adesApplyPaddingAndJustification (
						   BAD_CAST j->name.c_str(),  
						   j->width,
						   'L',
						   j->dpos
						);
				sline = xmlStrcat(sline, p->str); 
				free(p->str);
				free(p);
			}
		}
		// remove trailing whitespace from sline first
		removeTrailingWhiteSpace(sline); // mutates sline
		fprintf(outfile, "%s\n", sline);
		xmlFree(sline); // sline is a temp
	}
	for (DataDictList::iterator i = dataDictList.begin(); i != dataDictList.end(); i++) {
		xmlChar *sline = xmlCharStrdup("");
		int first = true;
		for (std::vector<HeaderStruct>::iterator j=headerInfo.begin();
				j!=headerInfo.end(); j++) {
			if (j->seen) { // don't print if never seen
				if (first) {
					first = false;
				} else {
					sline = xmlStrcat(sline, BAD_CAST pipestr);
				}
				//
				// find position in subDict.  If not present,
				// apply spaces instead
				//

				SubDict::iterator k = i->find(j->name);
				const xmlChar *temp;
				if (k != i->end()) {
					temp = k->second; // k->second still owns memory
				} else {
					temp = BAD_CAST &spaces[nspaces]; // 
				}
				paddedStruct *p = adesApplyPaddingAndJustification (
						   temp,
						   j->width,
						   j->fmt,
						   j->dpos
						);
				sline = xmlStrcat(sline, p->str); 
				free(p->str);
				free(p);
			}
		}
		// remove trailing whitespace from sline first
		removeTrailingWhiteSpace(sline); // mutates sline
		fprintf (outfile,"%s\n", sline );
		xmlFree(sline); // sline is a temp
	}

	//
	// finally  return xmlChar memory
	// 
	for (DataDictList::iterator i=dataDictList.begin(); i!=dataDictList.end(); i++) {
		for (SubDict::iterator j=i->begin(); j!=i->end(); j++) {
			//fprintf(outfile, "%s %s\n",j->first.c_str(), j->second);
			xmlFree(j->second);
		}
		//fprintf (outfile,"\n" );
	}
}
//----------------------------------------------------------------------

void obsContextToPsv(xmlNodePtr node, FILE *outfile) {
	xmlNode *c_node;  // C declaration not inside for loop
	//printf("obsContext node is %s\n", node->name);
        for (c_node = node->children; c_node; c_node = c_node->next) {
		if (c_node->type == XML_ELEMENT_NODE) {
			xmlNode *g_node; // C declaration node inside for loop
			// only # fundingSource has text
			xmlChar *text = xmlNodeGetRegularizedText(c_node);
			if (text) {
				fprintf(outfile, "# %s %s\n", c_node->name, text);
			} else {
				fprintf(outfile, "# %s\n", c_node->name);
			}
			xmlFree(text);
			// go through sub-nodes, which are '!' elements (all should have text_
        		for (g_node = c_node->children; g_node; g_node = g_node->next) {
				if (g_node->type == XML_ELEMENT_NODE) {
					xmlChar *text = xmlNodeGetRegularizedText(g_node);
					if (text) {
						fprintf(outfile, "! %s %s\n", g_node->name, text);
					} else {
						fprintf(outfile, "! %s\n", g_node->name);
					}
					xmlFree(text);
				}
			}
		}
	}
}

//
// adesGetBeginAndEnd returns the beginning and ending xmlNodePtr's 
// in a child list where all the elements have the same type.  Note
// there will be intervening non-element nodes in this list, which
// will be iterated over using node->next.
//
// begin is set to the first element in the children, or NULL if 
// no elements are in the list.
//
// end is set to the last element in the children with the same
// name as the begin element.
//
// The original node list continues to own the memory
//
// end is the next pointer of the last node.  This means we can
// use the normal for structure to loop over nodes
//
void adesGetBeginAndEnd(xmlNodePtr start, xmlNodePtr *begin, xmlNodePtr *end) {
	xmlNode *c_node;
	*begin = NULL;
	*end = NULL;
	for (c_node=start; c_node; c_node = c_node->next) {
		if (c_node->type == XML_ELEMENT_NODE) {
			if (*begin) {
				if (xmlStrEqual((*begin)->name, c_node->name)) {
					*end = c_node; // same name
				} else {
					break; // we are at the end of the same list
				}
			} else {
				*begin = c_node;
				*end = c_node;
			}
		}
	}
	if (*end) *end = (*end)->next; // one past the end, which may be NULL
	return;
}


//
// writes an obsData node to PSV format.  An
// obsData node contains a number of children
// all of the same type
//
void obsDataToPsv(xmlNodePtr node, FILE *outfile) {
	xmlNodePtr begin;
	xmlNodePtr end;
	//fprintf(outfile, "data node %s\n", node->name);
	adesGetBeginAndEnd(node->children, &begin, &end);
	likeTypeDataNodesToPsv(begin, end, outfile);
}

//
// writes an obsBlock node to PSV format
// and obsBlock has one obsContext child and
// one obsData child, with the obsContext
// child first.  This is not checked because
// the node has already been validated.
//
//
void obsBlockToPsv(xmlNodePtr node, FILE *outfile) {
	xmlNode *c_node = node;
	//fprintf(outfile, "obsBlock node is %s\n", node->name);
        for (c_node = node->children; c_node; c_node = c_node->next) {
		if (c_node->type == XML_ELEMENT_NODE) {
			if (xmlStrEqual(c_node->name, BAD_CAST "obsContext")) {
				obsContextToPsv(c_node, outfile);
			}
			if (xmlStrEqual(c_node->name, BAD_CAST "obsData")) {
				obsDataToPsv(c_node, outfile);
			}
		}
	}
}

//
// write a validated ADES xml xmlDocPtr in
// PSV format.
// 
void adesDocToPsv(xmlDocPtr doc, FILE *outfile) {
	xmlNode *adesNode = xmlDocGetRootElement(doc);
	xmlNode *c_node;
	// adesNode is an ades node by construction
	// the name must be ades and the attribute version is probably "2017"
	xmlChar *attribute = xmlGetProp(adesNode, BAD_CAST "version");
	fprintf (outfile, "# version=%s\n", attribute);
	xmlFree(attribute);
        for (c_node = adesNode->children; c_node; c_node = c_node->next) {
		if (c_node->type == XML_ELEMENT_NODE) {
			if (xmlStrEqual(c_node->name, BAD_CAST "obsBlock")) {
				obsBlockToPsv(c_node, outfile);
			} else {
				// need to find the next node of type
				// optical, offset, occultation, radar, ...
				// and find the beginning and end of all 
				// nodes of that type, and then process those
				// as a group.
				xmlNodePtr begin;
				xmlNodePtr end;
				//fprintf (outfile, "Node list of %s outside obsBlock\n", c_node->name);
				adesGetBeginAndEnd(c_node, &begin, &end);
				likeTypeDataNodesToPsv(begin, end, outfile);
				c_node = end;
				// since end is one past last matching
				// we may need to exit the for loop here
				// instead of trying c_node->next
				if (!c_node) break; 
			}
		}
	}
}
//-------------------------------------------------------------------------



paddedStruct *adesApplyPaddingAndJustification(const xmlChar *instring, int width, xmlChar jtype, int dpos) {
	//
	// adesApplyPaddingAndJustification 
	//
	// Inputs:
	//     instring -- the null-terminated input string 
	//     width    -- the integer width (in utf8 characters) of the reutrn string
	//                 The actual return may be longer because the instring was too wide
	//    jtype     -- "L", "R", "C" or "D" for left, right, center or decimal
	//    dpos      -- for "D" justification, the position of the decimal point in the string
	//
	// Outputs:
	//    paddedStruct *   (must be deallocated by caller)
	//       xmlChar *str   The new string.  This must be deallocated by caller
	//       int dpos       Sometimes dpos is adjusted because of the alignment requirements
	//       int width      Sometimes width is adjusted because of the alignment requirements
	//
	//
	
	int i, extra, point, leftpad, rightpad;
	const char *padding;
	xmlChar *sleft;
        const xmlChar *sright;
	paddedStruct *output = (paddedStruct *) malloc(sizeof(paddedStruct));

	int strWidth = xmlUTF8Strlen(instring);  // utf codepoints, not bytes
	extra = width - strWidth;
	if (extra > MAX_ADES_WIDTH) extra = MAX_ADES_WIDTH;
	if (extra < 0) extra = 0;    // used by "L", "R", and "C"
	switch (jtype) {
		case 'R':
			padding = &spaces[nspaces-extra];
			output->str = xmlCharStrdup(padding);
			output->str = xmlStrcat(output->str, instring);
			output->width = xmlUTF8Strlen(output->str);
			output->dpos = dpos;
			break;
		case 'L':
			padding = &spaces[nspaces-extra];
			output->str = xmlStrdup(instring);
			output->str = xmlStrcat(output->str, BAD_CAST padding);
			output->width = xmlUTF8Strlen(output->str);
			output->dpos = dpos;
			break;
		case 'C': 
			i = extra/2;
			padding = &spaces[nspaces-i];
			output->str = xmlCharStrdup(padding);
			output->str = xmlStrcat(output->str, instring);
			if (i*2 != extra) {
				i++;
			}
			padding = &spaces[nspaces-i];
			output->str = xmlStrcat(output->str, BAD_CAST padding);
			output->width = xmlUTF8Strlen(output->str);
			output->dpos = dpos;
			break;
		case 'D':
			point = xmlUTF8Strloc(instring, BAD_CAST &decimalPoint);
			if (point < 0) {
				sleft = xmlStrdup(instring); // note memory copy
				sright = BAD_CAST &spaces[nspaces]; // no memory copy
			} else {
				sleft = xmlUTF8Strndup(instring, point); // note memory copy
				sright = xmlUTF8Strpos(instring, point) + 1; // no memory copy
			}
			leftpad = dpos - 1 - xmlUTF8Strlen(sleft);
			if (leftpad < 0) {     // adjust dpos
				dpos = dpos - leftpad;
				leftpad = 0;   // we still add no spaces on left
			}
			rightpad = (width - dpos) - xmlUTF8Strlen(sright);
			if (point == xmlUTF8Strlen(instring)-1) {
				xmlFree(sleft);
				sleft = xmlStrdup(instring); // note memory copy
				rightpad--;
			}

			output->str = xmlCharStrdup(&spaces[nspaces - leftpad]);
			output->str = xmlStrcat(output->str, sleft);
			if (xmlStrlen(sright) != 0) { // don't add '.' if sright is ""
				output->str = xmlStrcat(output->str, BAD_CAST decimalPoint);
			} else {
				rightpad += 1;
			}
			if (rightpad < 0) rightpad = 0;
			output->str = xmlStrcat(output->str, sright);
			output->str = xmlStrcat(output->str, BAD_CAST &spaces[nspaces - rightpad]);
			output->width = xmlUTF8Strlen(output->str);
			output->dpos = dpos;
			xmlFree(sleft);
			break;
		default: // eventually throw something
			output->str = xmlStrdup(instring);
			output->width = xmlUTF8Strlen(instring);
			output->dpos = dpos;
			break;
	}

        return output; // need to xmlFree(output->str)
}

void testApplyPadding(xmlChar *s, int width, xmlChar just, int dpos) {
	paddedStruct *pstruct = adesApplyPaddingAndJustification(s, width, just, dpos);
	printf("len %2d %2d width %2d %2d dpos %2d %2d s=\"%s\"\n",
			xmlUTF8Strlen(s), xmlUTF8Strlen(pstruct->str),
			width, pstruct->width, dpos, pstruct->dpos,
			pstruct->str);
	xmlFree(pstruct->str);
	xmlFree(pstruct);
}



//
//end of routines for xmltopsv conversion
//-----------------------------------------------------------------------


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

int convertXmlToPsv(const char *xmlfile, const char *outputPsvFile) {
	int validFlag = 0;
	int doc_txt_len;
        xmlChar *doc_txt_ptr = NULL;

	int retval;

	// first validate the input xfile

	xmlSchemaValidityErrorFunc errfunc;
	xmlSchemaValidityWarningFunc warnfunc; 

	xmlSubstituteEntitiesDefault(1); // but we do use this

	doc = ADESreadXML(ADES_MASTER);
	if (!doc) return freeForReturn(-2);
	datadoc = ADESreadXML(xmlfile);
	if (!datadoc) return freeForReturn(-2);

	xmlChar *generalxsd = xmlCharStrdup(ADES_XSD_XSLT);
	generalxsd = xmlStrcat(generalxsd, BAD_CAST "generalxsd.xslt");
	cur = xsltParseStylesheetFile(generalxsd);
	xmlFree(generalxsd); // done with name
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
		printf ("%s", errAndWarn);
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

	xmlFree(errAndWarn); // need to free so the next run starts at NULL
	errAndWarn = NULL;

	if (validFlag < 0) {
	        xmlFreeDoc(datadoc);
	        datadoc = NULL;
		printf("Invalid input file %s\n", xmlfile);
		return -1;
	}

	// now start the psv conversion
	FILE *fout = NULL;
	if (strcmp(outputPsvFile,"stdout")) {
		fout = fopen(outputPsvFile, "w");;
	} else {
		fout = stdout;
	}
	adesDocToPsv(datadoc, fout);
	if (strcmp(outputPsvFile,"stdout")) {
		fclose(fout);}


	xmlFreeDoc(datadoc);
	datadoc = NULL;

	return 0;
}

//
// This function converts a psv file to an xml file. The psvencoding must be utf-8
//
int convertPsvToXml(const char *psvfile, const char *xmlfile, const char *psvencoding, const char *xmlencoding) {
	FILE *psv = NULL;
	bool ok = true;
	//printf ("psv file %s\n", psvfile);
	//printf ("xml file %s\n", xmlfile);
	//printf ("psv encoding %s\n", psvencoding);
	//printf ("xml encoding %s\n", xmlencoding);

	psv = fopen(psvfile, "r");
	if (psv == NULL) { 
		fprintf(stderr, "Can't open psv file %s\n", psvfile);
		return (-1);
	}

	// resd in lines and process into document
	//

	bool first = true;
	lineNo = 0; // global for errors
	stateMachineElementStack.clear();
	PropVec property;
	property.push_back(PropPair("version", "2017"));
	stateMachineElementStack.addPush(BAD_CAST "ades", NULL, property );
	while (xmlChar *line = readPsvLineFromFile(psv, psvencoding)) {

		//printf("%d: %s\n", xmlUTF8Strlen(line), line);

		lineNo++; // count blank lines too
		PSVLineStruct record = parsePSVLine(line);

		//printf ("record type = %d:\n", record.linetype);
		//for (StringVector::const_iterator i=record.words.begin(); i!= record.words.end(); i++) {
		//	printf("word %ld:%s:\n", i-record.words.begin() + 1, i->c_str());
		//}

		if (record.linetype == BLANK_LINE) continue; // skip blank lines
		if (record.linetype == ILLEGAL_LINE) { // set bad flag; print message
			fprintf(stderr, "%s\n", record.words[0].c_str());
			ok = false;
			continue;
		}

		if (first) { // first non-blank line must be #version=2017
			// need to check this
			first = false;
		} else {
			PSVState nextState = stateTransitions[psvState][record.linetype].first;
			psvState = stateTransitions[psvState][record.linetype].second(psvState, nextState, record.linetype, record.words, 0);
		}

		xmlFree(line);

	}

	fclose(psv);
	//
	// write and free the document
	//
	//void printXmlDoc(xmlDocPtr doc, FILE *fout, const char *encoding, int verbose);
	xmlDocPtr psvdoc = stateMachineElementStack.takeDocAndClear();
	if (ok) { // if ok write file
		//printXmlDoc(psvdoc, stdout, xmlencoding, 0);
		saveXmlDoc(psvdoc, xmlfile, xmlencoding, 1);
	}
	xmlFreeDoc(psvdoc);

	////PropVec properties;
	////properties.push_back(PropPair("version", "2017"));

	//ElementStack s(BAD_CAST "ades", NULL, properties);
	////ElementStack &s = stateMachineElementStack;

	////s.clear();
        ////s.addPush(BAD_CAST "ades", NULL, properties);
	////s.addPush(BAD_CAST "sub");

	////properties.push_back(PropPair("fooey", "bear"));
	////s.add(BAD_CAST "under", BAD_CAST "foo");
	////s.add(BAD_CAST "under", BAD_CAST "bar", properties);
	////s.addPopPush(BAD_CAST "sub");
	////s.add(BAD_CAST "under", BAD_CAST "bif", properties);
	////s.add(BAD_CAST "under", BAD_CAST "baz");

	////xmlDocPtr doc = s.takeDocAndClear();
	////printXmlDoc(doc, stdout, xmlencoding, 1);
	////xmlFreeDoc(doc);


	return 0;
}
int saveXmlDoc(xmlDocPtr doc, const char *fname, const char *encoding, int format) {
	int n = xmlSaveFormatFileEnc(fname, doc, encoding, format);
	//printf("%s %p %s %d  %d\n",fname, doc, encoding, format, n);
	return n;
}

void printXmlDoc(xmlDocPtr doc, FILE *fout, const char *encoding, int verbose) {
	xmlChar *doc_txt_ptr = NULL;
	int doc_txt_len = 0;

	if (verbose) fprintf(fout, "doc  = %p\n", doc);
	xmlDocDumpFormatMemoryEnc(doc, &doc_txt_ptr, &doc_txt_len, encoding, 1);
	if (verbose) fprintf(fout, "datadoc doc_txt_len = %d, doc_txt_ptr=%p\n",doc_txt_len, doc_txt_ptr);
	if (doc_txt_len) {
		fprintf(fout, "%s\n",doc_txt_ptr);
	} else {
	}
	xmlFree(doc_txt_ptr);
	//xmlDocFormatDump(fout, doc, 1);
}
