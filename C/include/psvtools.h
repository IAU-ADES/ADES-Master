/*
 * include file for psv tools
 *
 *
 */

#ifndef __PSVTOOLS_H__
#define __PSVTOOLS_H__

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

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
void obsContextToPsv(xmlNodePtr node, FILE *outfile);

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
void adesGetBeginAndEnd(xmlNodePtr start, xmlNodePtr *begin, xmlNodePtr *end);

//
// Process a list of data nodes, all of the same type
//
void likeTypeDataNodesToPsv(xmlNodePtr begin, xmlNodePtr end, FILE *outfile) ;

//
// writes an obsData node to PSV format.  An
// obsData node contains a number of children
// all of the same type
//
void obsDataToPsv(xmlNodePtr node, FILE *outfile) ;

//
// writes an obsBlock node to PSV format
// and obsBlock has one obsContext child and
// one obsData child, with the obsContext
// child first.  This is not checked because
// the node has already been validated.
//
//
void obsBlockToPsv(xmlNodePtr node, FILE *outfile);

//
// write a validated ADES xml xmlDocPtr in
// PSV format.
// 
void adesDocToPsv(xmlDocPtr doc, FILE *outfile) ;

//
// save doc to a file
//
int saveXmlDoc(xmlDocPtr doc, const char *fname, const char *encoding, int format);

//
//-------------------------------------------------------------------------



typedef struct {
	xmlChar *str;
	int dpos;
	int width;
} paddedStruct;

paddedStruct *adesApplyPaddingAndJustification(const xmlChar *instring, int width, xmlChar jtype, int dpos) ;

void testApplyPadding(xmlChar *s, int width, xmlChar just, int dpos) ;


int convertPsvToXml(const char *psvfile, const char *xmlfile, const char *psvencding, const char *xmlencoding);
int convertXmlToPsv(const char *xmlfile, const char *psvfile);

#ifdef __cplusplus
}
#endif /* __cplusplus */


#ifdef __cplusplus
//-----------------------------------------------------------------------
//
// ElementStack class
//

typedef std::pair<std::string, std::string> PropPair;
typedef std::vector<PropPair> PropVec;
class ElementStackException: public std::exception {
	private:
		std::string msg;
	public:
		ElementStackException(const char *s);
		virtual const char * what() const throw();
		virtual ~ElementStackException() throw();
};
class ElementStack {
	private:
		//
		// Don't free on pop operations.  The only free should
		// be done by the destructor.  makeTree makes a copy
		// of all the nodes for the doc
		//
		std::vector<xmlNode *> _elementStack;
		//ElementStack &operator=(const ElementStack &) = delete;
		//ElementStack(const ElementStack &) = delete;
		ElementStack &operator=(const ElementStack &a);
		ElementStack(const ElementStack &);
		void _addProperties(xmlNode *node, const PropVec &properties);
	public:
			// a new empty stack
		ElementStack();    
			// a new stack with tag and text
		ElementStack(const xmlChar *tag, const xmlChar *text=NULL);  
			// a new stack with tag, text and properties
		ElementStack(const xmlChar *tag, const xmlChar *text, const PropVec &properties);  
			// prints the stack with desription on a single line
		void print(const char *description = "");
			// pops the stack
		void pop();
			// extends the back element by a new element
		void addElement(xmlNode *element); // ElementStack owns the memory
			// extends the back element by a vector of new element
		void addElementList(std::vector<xmlNode *> elements); // ElementStack owns all the memory
			// extends the back element with a new node with (tag, text)
		xmlNode *add(const xmlChar *tag, const xmlChar *text = NULL);
			// extends the back element with a new node with (tag, text, properties)
		xmlNode *add(const xmlChar *tag, const xmlChar *text, const PropVec &properties);
			// extends the back element with a new node and pushes a pointer to the new node onto the stack
		void addPush(const xmlChar *tag, const xmlChar *text = NULL);
			// extends the back element with a new node and pushes a pointer to the new node onto the stack
		void addPush(const xmlChar *tag, const xmlChar *text, const PropVec &properties );
			// pops the stack and then calls addPush with a new element (makes sibling)
		void addPopPush(const xmlChar *tag, const xmlChar *text = NULL);
			// pops the stack and then calls addPush with a new element (makes sibling)
		void addPopPush(const xmlChar *tag, const xmlChar *text, const PropVec &properties);
			//
			// creates a new doc with a copy of <node>
			// as the root element.  <node> is copied
			// recursively.  The returned xmlDoc owns
			// all the memory.   This is a deep copy 
			// of node, and the input node may be freed
			// afterwards with no consequences.
			//
		xmlDocPtr copyDoc(unsigned int n=0);
			// 
			// makes a Doc from the top node (and all children)
			// and clears the stack.  The existing memory is now owned
			// by the caller.
			//
			// n is from the root node down
			//
		xmlDocPtr takeDocAndClear();
			// returns a pointer to the node at position n 
			// in the stack, from the root node down
		const xmlNode *pointToNode(unsigned int n=0);
			// frees all the xmlNodes and sets the stack to
			// zero length
		void clear();
			// class destructor calls clear() first.
		~ElementStack();
};
#endif /* __cplusplus */



#endif /* __PSVTOOLS_H__ */
