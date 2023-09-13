#
# xmlutility.py
# python module to handle all the XML reads, writes
# and transformations.  The routines in this
# file are all completely general in intended
# to be use as the base xml/xsd/xslt interface.
#
#
#
# This impolementaiton uses lxml, which is not part of
# the default python installation and so must
# be installed separately. 
#
#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#

#
# Use the names XMLTree and XMLElement to easily find
# all references to the xml library object ctors
#

from lxml import etree as XMLTree
from lxml.etree import Element as XMLElement

#import xml.etree.ElementTree as XMLTree
#from xml.etree.ElementTree import Element as XMLElement

#from xml.dom import minidom

#
# XMLTree interface:
#   static methods:
#      XMLTree.parse(file)  # reads in an xml File and returns an <xmltree>
#      XMLTree.XSLT(XMLTree) # returns an XSLT transformer from an XML Tree
#      XMLTree.XMLSchema(XMLTree) # returns a schema from n XML Tree
#      XMLTree.XML(string) # parses a str into an XML tree
#      XMLTree.ElementTree(<element>) # returns an XLMTree with <element> 
#                                       as root
#
#   string method:
#      str(<xmltree>) returns a string suitable for parsing.  See 
#                     XMLtoSchemaViaXSLT for why this is needed sometimes
#
#   methods:
#      <xmltree>.write(...): writes xml tree to stream
#
#
# XMLElement interface:
#   ctor's
#     <element> = XMLElement(tag, attrib):  elemnent ctor
#   members:
#     <element>.tag     : element tag str 
#     <element>.text    : element text str 
#     <element>.tail    : element tail str 
#     <element>.attrib  : element attrib as python dict *no order*
#   methods:
#     <element>.extend  : add a list of elements to <element>
#
#
# XML schema methods:
#   <schema>.assertValid(XMLTree)
#
# XML XSLT transformer methods:
#   <xslt>(xml_tree) : call method transforms <xml_tree> into the 
#                      transformed xml tree
#
#


#-------------------------------------------------------------------
# XML utilities
#-------------------------------------------------------------------

def readXML(xmlFile):
   """ reads in xml file -- this is encoding agnostic.

       Input:  xml file name

       Return: xml tree of xslFile

       Errors:  
         The xmlFile might not be readable or might not
         be a valid XML document
   """
   return XMLTree.parse(xmlFile)

def XMLtoXSLT(xslt_tree):
   """ makes an XSLT transformer out of an xml tree

       Inputs:
          xslt_tree:  an xml tree t be used as xslt

       Return Values: an XSLT transformer object

       Errors:  
          The xslt_tree might not be a valid xslt
          transformation
   """
   return XMLTree.XSLT(xslt_tree)
     

def transformViaXSLT(xml_tree, xslt_tree):
   """ Transforms xml_tree via an xslt_tree

       Inputs:
          xml_tree:  an xml tree
          xslt_tree:  an xml tree

       Return Values: the resulting transformed xml tree
   """
   return XMLtoXSLT(xslt_tree)(xml_tree)

def transformFileViaXSLT(xml_file, xslt_file):
   """ Transforms an xml file by another xml file
       interpreted as xslt

       Inputs:
          xml_file:  name of xml file to transform
          xslt_file:  name of xslt file

       Return Values: the resulting transformed xml tree

       Errors:  
          Either file might not be readable
          Either file might not be xml
          The xslt file might not be valid
   """
   return transformViaXSLT(readXML(xml_file), readXML(xslt_file))

def XMLtoSchema(xml_tree):
   """ Re-interprets and xml_tree as a schema
       Inputs:
          xml_tree:  an xml tree 

       Return Values: the xml tree interpreted as a schema

       This works with xml files read in from files, but
       see XMLtoSchemaViaXSLT below for a caveat if an XSLT
       transform is used to make the xml_tree.


       Errors:
          The xml_tree might not be usable as a schema
       
   """
   return XMLTree.XMLSchema(xml_tree) # now parsed as schema


def XMLtoSchemaViaXSLT(xml_tree, xslt_tree):
   """ Transforms xml_tree via xslt_tree and interprets
       the result as an xml schema.  This requires an
       intermediate step if the xslt transform makes a 
       text XML tree.  Otherwise, this would just be
       return xml_tree.XMLSchema(xslt_tree)
    
       Inputs:
          xml_tree:  an xml tree
          xslt_tree:  an xml tree representing an xslt file

       Return Values: the transformation interpreted as a schema
   """
   schema = transformViaXSLT(xml_tree, xslt_tree)
   ## 
   ##  extra stutter step if we use a text-based 
   ##  schema xslt such as submithumanxsd.xslt, because
   ##  those schema write <!--- comments --> and other
   ##  text nodes the xml tree.  Going out to text and back
   ##  eliminates those comment nodes and makes the 
   ##  other nodes xml nodes instead of text nodes with
   ##  xml text.
   ## 
   ##  If the xslt wrote xml nodes directly this step
   ##  is harmless but unnecessary.
   ## 
   st = str(schema)         # text nodes into text
   st2 = XMLTree.XML(st)    # out again into xml
   return XMLtoSchema(st2) # now parse as schema



#-------------------------------------------------------------------
# XML Element utilities
#-------------------------------------------------------------------
#
# Utility function for whitespace. 
# Sometimes a text or tail value is None; 
# sometimes it is all whitespace of various
# sorts, when it has a value it must be
# interpreted as stripped.  Anyway, return
# '' if all ws or None.
#
# Strips all leading and trailing blanks
#
def regularizeWhiteSpace(text):
   """ regularizeWhiteSPace(text)
       
       Input: a string value or None

       Output:  '' if text is None
                otherwise text.strip()

       Errors:  text must be a string
   """
   rtext = ''
   if text:  # may be None or ''; both become ''
     rtext = text.strip()
   return rtext

def getElementTagTextTail(element):
   """ getElementTagTextTail(element) 
       Returns (tag, text tail)

       Input: 
         element: the element to examine

       Return Value:
         (teg, text, tail) 
         where text and tail are '' if not present
         and stripped if present
   """

   return (element.tag,
           regularizeWhiteSpace(element.text),
           regularizeWhiteSpace(element.tail) )

def getElementTagText(element):
   """ getElementTagText(element) 
       Returns (tag, text)

       Input: 
         element: the element to examine

       Return Value:
         (teg, text) 
         where text is '' if not present
         and stripped if present
   """

   return (element.tag,
           regularizeWhiteSpace(element.text))

def newElement(tag, text=None, attrib={}, tail=None):
   """ newElement(tag, text, attrib, tail)
       returns a new element with values set
 
       Inputs:
          tag:   element tag name
          text:  element text (defaults to None)
          attrib:  dictionary of attributes (defaults to {})
          text:  element tail (defaults to None)

       Return Value:  new element
  
   """
   #
   # Note: element.attrib can't be set with
   # if attrib: 
   #    element.attrib = attrib
   #
   # however, element.attrib['foo'] = 11
   # is perfectly fine later. 
   #
   # Put in the empty dict for later expansion
   #
   element = XMLElement(tag, attrib)
   if text:  # None is default but '' is None too
      element.text = text
   if tail:  # None is default but '' is None too
      element.tail = tail
   return element

def makeElementList(eList):
   """ makeElementList(eList)
 
       Input: a list of {tag, value} tuples

       Output: a list of elements with those tags
               and values. 
               
       Duplicates are explicitly allowed, such as in 
       a list of names.  The order is preserved.
   """
   return [newElement(tag, value) for tag, value in eList]



def makeTree(element):
   """ makeTree(element)
         makes a Tree with element as the root

       Input:
         element: root element for new element

       Return Value: 
         ELementTree object with element as root
              
  
   """
   return XMLTree.ElementTree(element)



#------------------------------------------------------

#
# class ElementStack is for creating an xml
# tree using stack-like operations. 
#
# Notice elementStack has nothing to do
# with the tree of elements being built by the
# psv parser; the stack just remembers which
# element should be extended.
#
# The final element tree is just from any
# element in the stack, but usually the 0 one:
#    treeTop = makeTree(elementStack[0])
#
class ElementStack():
   """
       class ElementStack manages a stack of xml
       elements.   This is intended to be a helper
       to build xml trees.  The basic idea here
       is that as new elements come in, the element
       at the top of the tree is extended.

       Sometimes a new element is added which has
       sub-elements, in that case the top of the
       stack is extended and the new sub-element
       is also pushed.

       When the new element is finished it is popped.

       The addPush and addPopPush operations are
       natural if new elements are acquired using
       a state machine, such as when reading a PSV
       file.  In that case, the end of an element
       is signalled by the beginning of the next
       element.


       The stack is pushed and popped
       XML elements are created and extended

   """
   def _print(self, description):
     """ _print prints the stack with a description
         Inputs:
           description:  a string

         Printing the elementStack elements in lxml
         prints the tag of the element, which is handy
         for development.
     """
     print (description, self.elementStack)


   def __init__(self, tag=None, text=None, attrib={}):
     """ ElementStack(self, tag, text=None, attrib={})
         Inputs:
             tag:  tag of root element
             text: text of root element
             attrib: attributes of root element

     """
     if (tag):
       elem = newElement(tag, text, attrib)
       self.elementStack = [ elem ]
       #self._print('init')
     else:
       self.elementStack = []

   def pop(self):
     """ ElementStack.pop()
         pops the stack

     """
     if (len(self.elementStack) < 2):
        raise RuntimeError("ElemenStack is too short to pop")
     #self._print('begin pop')
     self.elementStack.pop()
     #self._print('end pop')

   def addElementList(self, elementList):
     """ ElementStack.addElmeent(self, elementList)
         add elements to the element on top of the stack

         Inputs:
             elementList:  a list of elements
     """
     if (len(self.elementStack) == 0):
        raise RuntimeError("zero ElementStack in addElementList")
     #self._print('begin addElementList')
     self.elementStack[-1].extend(elementList)
     #self._print('end addElementList')

   def addElement(self, element):
     """ ElementStack.addElmeent(self, element)
         adds a new element to the element on top of the stack

         Inputs:
             element:  a previously created element to extend
                       the top element of the stack
     """
     if (len(self.elementStack) == 0):
        raise RuntimeError("zero ElementStack in addElement")
     #self._print('begin addElement')
     self.elementStack[-1].extend([element])
     #self._print('end addElement')

   def add(self, tag, text=None, attrib={}):
     """ ElementStack.add(self, tag, text=None, attrib={})
         creates a new element and extends the element on top of the stack

         Inputs:
             tag:  tag of new element
             text: text of new element
             attrib: attributes of new element

     """
     if (len(self.elementStack) == 0):
        raise RuntimeError("zero ElementStack in add")
     #self._print('begin add('+tag+')')
     elem = newElement(tag, text, attrib)
     self.elementStack[-1].extend([elem])
     #self._print('end add('+tag+')')

   def addPush(self, tag, text=None, attrib={}):
     """ ElementStack.addPush(self, tag, text=None, attrib={})
         creates a new element, extends the element on top of the stack,
         and pushes the new element onto the stack.  If the stack
         is empty it makes a new stack of length one

         Inputs:
             tag:  tag of new element
             text: text of new element
             attrib: attributes of new element

     """
     if (len(self.elementStack) == 0):
        elem = newElement(tag, text, attrib)
        self.elementStack = [ elem ]
     else:
        #self._print('begin addPush('+tag+')')
        elem = newElement(tag, text, attrib)
        self.elementStack[-1].extend([elem])
        self.elementStack.append(elem)
        #self._print('end addPush('+tag+')')

   def addPopPush(self, tag, text=None, attrib={}):
     """ ElementStack.addPush(self, tag, text=None, attrib={})
         Pops the stack and then
         creates a new element; extendes the element on top of the stack
         and pushes the new element onto the stack

         Inputs:
             tag:  tag of new element
             text: text of new element
             attrib: attributes of new element

     """
     #self._print('begin addPopPush('+tag+')')
     self.pop()
     self.addPush( tag, text, attrib)
     #self._print('end addPopPush('+tag+')')


   def copyTree(self, n=0):
     """ makeTree(n) returns an xml tree rooted at the nth
         element of the stack.   The default is to return
         the whole tree, but it will also return subTrees.

         It is especially convenient that n=-1 will return
         a tree using the top element on the stack, which
         is useful for validating sub-elements as they are
         added.
     """
     #self._print('copyTree('+repr(n)+')')
     if (n<0 or n > len(self.elementStack)):
        raise RuntimeError("no such n in copyTree")
     return makeTree(self.elementStack[n])

   def takeTreeAndClear(self):
     """ takeTreeAndClear ) returns an xml tree rooted at 
         root element of the stack.  It returns the whole
         tree and clears the stack 

     """
     tree =  makeTree(self.elementStack[0])
     self.elementStack = []
     return tree

   def clear(self):
     """ clear() sets the elementStack to zero.  Python
         handles the memory management.
     """
     self.elementStack = []
  

