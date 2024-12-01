#!/usr/bin/env python3
#
# python module to read in adesmaster.xml and 
# provide tables of both xml ordering and psv 
# ordering.  This is imported by the psvtoxml.py
# and xmltopsv.py scripts
#
# Some routines, such as readXML, are general.
# and we may want to create a adesUtil.py 
# module with this sort of thing in it.
#
#
# This module uses lxml, which is not part of
# the default python installation and so must
# be installed separately
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

###from lxml import etree as XMLTree
###from lxml.etree import Element as XMLElement

#import xml.etree.ElementTree as XMLTree
#from xml.etree.ElementTree import Element as XMLElement

#from xml.dom import minidom

#-------------------------------------------------------------------
# XML utilities
#-------------------------------------------------------------------
from ades.xmlutility import readXML
from ades.xmlutility import XMLtoXSLT
from ades.xmlutility import transformViaXSLT
from ades.xmlutility import transformFileViaXSLT
from ades.xmlutility import XMLtoSchema
from ades.xmlutility import XMLtoSchemaViaXSLT
#-------------------------------------------------------------------
# Element utilities
#-------------------------------------------------------------------
from ades.xmlutility import getElementTagTextTail
from ades.xmlutility import getElementTagText
from ades.xmlutility import newElement
from ades.xmlutility import makeTree
from ades.xmlutility import makeElementList
#-------------------------------------------------------------------
# ElementStack utility class
#-------------------------------------------------------------------
from ades.xmlutility import ElementStack
#-------------------------------------------------------------------


from collections import OrderedDict  # to do list duplicate removal

import io # io.open works in python 2 and 3 the same way
import os
import inspect
from ades import adesutility # circular imports are allowed -- used for inspect

#-------------------------------------------------------------------
# Variables for external consumption
#   adesmaster.xml     -- master ades XML file containing schemas and doc
#   schemaxslts        -- XSLT files to transform master into XSD schemas
#   latexxslts         -- XSLT files to transform master into latex doc source
#
# XML utilities
#   readXML              -- reads XML file from fileName into tree
#   transformViaXSLT     -- transforms XML tree by another interpreted as XSLT
#   transformFileViaXSLT -- same as above but takes two fileNames as inputs
#
# PSV utilities
#   getAdesTables        -- table of PSV order, default widths, and justifications
#
#-------------------------------------------------------------------

mypath = os.path.dirname(os.path.abspath(__file__)) # where am I?

xmlpath = os.path.join(mypath, 'data', 'xml')
xsltpath = os.path.join(mypath, 'data', 'xslt')
adesmaster = os.path.join(xmlpath, "adesmaster.xml")

# transforms master a form 
# python can parse for tables
adestablexslt = os.path.join(xsltpath, "util", "tableades.xslt")  

xsdpath = os.path.join(xsltpath, 'xsd')
schemaxslts = {'submit': os.path.join(xsdpath,  "submitxsd.xslt"),
               'submithuman': os.path.join(xsdpath, "submithumanxsd.xslt"),
               'general': os.path.join(xsdpath, "generalxsd.xslt"),
               'generalhuman': os.path.join(xsdpath, "generalhumanxsd.xslt") }

latex = os.path.join(xsltpath, 'latex')
latexxslt = { 'docades': os.path.join(latex, "docades.xslt"),
              'docelementstable': os.path.join(latex, "docelementstable.xslt"),
              'docsimpletypestable': os.path.join(latex, "docsimpletypestable.xslt"),
              'docgrouptypestable': os.path.join(latex, "docgrouptypestable.xslt") }




def makeADESElement(tag, elements):
   """ makeADESElement(tag, elements)
       Creates an element from an iterable of sub-elements,
       checking against the required and optional element 
       tables.

       Input:
         tag     :  Name of the element to create
         elements:  iterable of elements

       Output:
         element filled in proper order from elements. 


       This routine uses allowedElementDict and 
       requiredElementDict to put elements in order
       and make sure everything present is allowed and
       everything required is present.

       Each element in elements must have a unique tag.
   """
   global allowedElementDict
   global requiredElementDict
   #
   # make a dictionary indexed by element tags in elements 
   #
   eDict = { elem.tag: elem for elem in elements }
   #
   # check to see if all required elements are present
   # and all elements are allowed
   #
   s = set(eDict.keys())
   if not s.issubset(allowedElementDict[tag]):
     raise RuntimeError('tag ' + tag + ' has extra elements' + \
                         repr(s - set(allowedElementDict[tag])))
   if not s.issuperset(requiredElementDict[tag]):
     raise RuntimeError('tag ' + tag + ' is missing required elements ' + \
                         repr(set(requiredElementDict[tag]) - s))
   #
   # make a new element using tag and inserting all the
   # elements in the order required by allowedElementsDict
   #
   ADESElem = newElement(tag)  # no text, tail or attrib 
   #
   # add in the order of the allowedElementDict list
   # for this tag.  Loop over allowedElementDict[tag]
   # is what enforces the order
   #
   for e in allowedElementDict[tag]: 
      if e in s:
        ADESElem.append(eDict[e])
   return ADESElem
   




#-------------------------------------------------------------------
# ADES table utilities
#
#   readAdesTables() is called as part of import.  
#   getAdesTables() returns the generated tables
#
#-------------------------------------------------------------------

def readAdesTables():

   """ readAdesTables()

       Globals:
          adesmaster:     path to adesmaster.xml file
          adestablexslt:  path to xslt to parse adesmaster
                          for extracting this information

       Return Value:
          a tuple (allowedElementDict, requiredElementDict, psvFormatDict)

          allowedElementDict: a dictionary whose keys are all the
                 elements in adesmaster and whose values
                 are an list of the sub-elements possible
                 for each element.  This list is in the
                 order the elements must appear in the
                 xml file.

          requiredElementDict: a dictionary whose keys are all the
                 elements in adesmaster and whose values
                 are an list of the sub-elements required
                 for each element.  This list is in the
                 order the elements must appear in the
                 xml file.
   
                 This list may be incomplete.  Any element
                 in a choice is considered as not required,
                 even though it is possible for all the choice's
                 to require a sequence with a particular element.
                 However, that case does not appear and may 
                 violate the xsd 1.0 parsing rules unless the
                 element can be moved outside the choice

          psvFormatDict: A dictionary of lists for each psv type.
                  The allowed types are 'optical', 'offset',
                  'occulation' and 'radar' for now, but that's in
                  the adesmaster.xml file.  For each psv type, the
                  dictionary is a list of tuples 
                  (element width, justification)
                  The order of this list is the order
                  of elements in the default psv format
                  with a special case for the last element,
                  which is 'remarks' and which is always last.
                  Elements not in this list always go between
                  the penultimate list item and the last one.
         
                 element: the element tag name
                 width: the minimum width in psv
                 justifcation: A format code
                               R  right justify
                               L  right justify
                               D<n>, (n = 2, 3, 4)
                                  fixed point with <n>
                                  digits to the right
                                  of the decimal point

   """

   global allowedElementDict
   global requiredElementDict
   global psvFormatDict

   masterTree = readXML(adesmaster)
   xsltTree = readXML(adestablexslt)
   
   xsltTransform = XMLtoXSLT(xsltTree)
   transformed = xsltTransform(masterTree)
   lines = str(transformed).split('\n')
  
   #
   # Now create:
   #  allowedElementDict:
   #     A dictionary of lists in the order elements are to
   #     be written in a given structure
   #  requiredelementDict:
   #     A dictionary of lists in the order elements are to
   #     be written in a given structure of only required 
   #     elements -- must check that sequences and groups are
   #     required above elements, which is what the 'open'
   #     and stillRequired test does.
   #  psvFormatDict:
   #     A list of (tag, default width, justification code) tuples
   #     for writing PSV files.  This order is different from the
   #     element ordering in XML.
   #
   allowedElementDict = {}
   requiredElementDict = {}
   psvFormatDict = {}
   
   for l in lines:  
     #print (l)
     if not l:     #  skip empty lines
        continue
     words = l.split()
     if words[0] == 'top':        # 'top means add new entry to allowedElementDict
        currentElement = words[1] # currentElement kept for 'element' 
        allowedElementDict[currentElement] = []
        requiredElementDict[currentElement] = []
        stillRequired = True

     elif words[0] == 'open':    # 'open' may be optional sequence or group, which
                                 # should be ignored for required.  Choice is not
                                 # required even if it is a required choice, because
                                 # there will be no common elements to the choice
                                 # (most of the time, anyway)
        if (words[1] != 'choice') or (words[3] != 'required'):
           stillRequired = False

     elif words[0] == 'close':    # 'close' ends possibly optional block
           stillRequired = True

     elif words[0] == 'element':    # 'element' is under currentElement
        allowedElementDict[currentElement].append(words[1])
        if stillRequired and (words[3] == 'required'):
           requiredElementDict[currentElement].append(words[1])

   
     elif words[0] == 'psv':        # 'psv' is separate to make psv table
        # "tagtype <type> name <name> width <width> justification <j> dpos <dpos>"
        # width and dpos must be int.  justification is "L", "R", "C" or "D"
        # dpos is 0 unless justificaiton is "D"
        if words[2] not in psvFormatDict: # make new list if not yet seen
           psvFormatDict[words[2]] = []
        psvFormatDict[words[2]].append((words[4], int(words[6]), 
                              words[8], int(words[10]))) 
   
   #
   # Now remove duplicates in the table list, working
   # through the list backwards.  This will not accomodate all
   # possible structures (since I can write context-dependent 
   # ordering in the lists arbitrarily with <choice>), but
   # in all of our cases eliminating duplicates working backwards
   # will give an appropriate order.   
   #
   for item in allowedElementDict:
     if allowedElementDict[item]:  # list of length > 0
        allowedElementDict[item].reverse()  # reverse list
        # remove duplicate items from beginning, preserving order
        allowedElementDict[item] = list(OrderedDict.fromkeys(allowedElementDict[item]))
        allowedElementDict[item].reverse()  # reverse back

   for item in requiredElementDict:
     if requiredElementDict[item]:  # list of length > 0
        requiredElementDict[item].reverse()  # reverse list
        # remove duplicate items from beginning, preserving order
        requiredElementDict[item] = list(OrderedDict.fromkeys(requiredElementDict[item]))
        requiredElementDict[item].reverse()  # reverse back

   #print ('allowed')
   #for item in allowedElementDict:
   #  print ( item, ': ', allowedElementDict[item])

   #print ('required')
   #for item in requiredElementDict:
   #  print ( item, ': ', requiredElementDict[item])


def getAdesTables():
   """ getAdesTables()
       returns the tables initialized by readAdesTables on import
   """
   global allowedElementDict
   global requiredElementDict
   global psvFormatDict

   return (allowedElementDict, requiredElementDict, psvFormatDict)

#
# PSV formatting routine
#
def applyPaddingAndJustification(s, l, jtype, dpos=0):
   """ applyPaddingAndJustification(s, l, jtype, dpos)

       Inputs:
          s: input string
          l: output length (pad with blanks)
             If string is too long it is returned without change
          jtype: justification type
                L: left
                R: right
             D<n>: decimal point in column <n>
          dpos: decimal point in column <dpos> (for jtype = "D")

       Return Value:
            (padded string, l, dpos)
            l is the achieved width.  It may be longer than l
            dpos is the achieved dpos.  It may be different from dpos

       The width and dpos may be different. These should be used to
       update the headerInfo array if one is trying to achieve alighment
       over multiple lines.
   """

   ll = len(s)
   if jtype == 'L': # negative multipliers result in ''
      outs = s + (l - ll)*' '
      return (outs, len(outs), dpos)
   elif jtype == 'R':
      outs =  (l - ll)*' ' + s
      return (outs, len(outs), dpos)
   elif jtype == 'C':
      i = (l-ll)//2
      j = i
      if i*2 != l-ll: j = j + 1 
      outs =  i*' ' + s + j*' '
      return (outs, len(outs), dpos)
   elif jtype == 'D':  # null strings not allowed
      try:
         if dpos < 0:           
           raise 
      except:
         raise RuntimeError ("Illegal justification string " + jtype)
      #
      # pad only with spaces on both sides
      # and do not change s
      #
      # if s has no decimal point don't add one
      # but line up as if it werre to the right
      # of s.
      #
      # the result may be too wide.  This is OK
      # we will do a fix-up on width in the caller.
      # Note this means we have to do it twice but
      # we never will get wider as a result of the
      # second pass. 
      #
      # Also, we assume s is a decimal for xsd.  If
      # not, validation will fail later.  If there
      # is more than one decimal point, it will fail
      # here.
      #
      sp = s.split('.')
      if (len(sp) == 1):  #No decimal point
         sleft = s
         sright = ''
      elif (len(sp) == 2): #has decimal point
         (sleft, sright) = sp
      else:
         raise RuntimeError('Illegal string ' + s + ' for decimal value')
      #
      # now re-pack with width
      #
      leftpad = dpos - 1 - len(sleft)
      #
      # figure out dpos extension
      #
      if leftpad < 0: # <n> needs adjusting
          ndpos = dpos - leftpad
          rightpad = (l - ndpos)  - len(sright)
          dpos = ndpos
      rightpad = (l - dpos)  - len(sright)
      if (len(s) > 0) and (s[-1] == '.'): # trailing deciaml point adjustment
        sleft = s
        rightpad = rightpad - 1
      #
      # works for negative values of leftpat and rightpad
      # adding no charackers
         #
      if sright:  # don't add '.' if sright is ''
        retval =  leftpad * ' ' + sleft + '.' + sright + rightpad * ' '
      else:
        rightpad += 1
        retval =  leftpad * ' ' + sleft + rightpad * ' '
      return (retval, len(retval), dpos);


   else:
      raise RuntimeError ("Illegal justification string " + jtype)

#
# initialize by reading tables
#
readAdesTables();  
