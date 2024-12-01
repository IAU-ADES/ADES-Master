#!/usr/bin/env python3
#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#

import sys
import re
import io
import argparse
#

#
# sys.argv[1]: input psv file
# sys.argv[2]: output xml file
# sys.argv[3]: input psv file encoding if not utf-8
# sys.argv[4]: output xml file encoding if not utf-8
# example: ./psvtoxml.py <psv file> <xml file>
#
import sys

from ades import adesutility
from ades import convertutility


#
# read in allowedElementDict, requiredELementDict,  and psvFormatDict
# psvFormatDict is not used by this conversion
#
(allowedElementDict, requiredElementDict, psvFormatDict) = \
                                           adesutility.getAdesTables()



#
# PSV file BNF:
#
#   This is very permissive.  Checks will be done on the
#   resulting xml with an xslt validator
#
#   blank line
#   TopHeaderine     = # <level 1 xml thing>
#   SecondHeader  = ! <level 2 xml thing>
#   KeywordRecord = <any line containing only xml element names>
#   DataRecord    = <any other line>
#
#   blank lines are ignored
#   leading and trailing whitespace is ignored
#


#
# header sections are a set of lines starting with
# either '#' or '!'.  The lines starting with
# '#' are xml level 1 lines and the lines starting
# with '!' are xml level 2 lines.
#
#   # observers
#   ! name P. Villa
#   ! name F. Madero
#   # telescope


#
# Enum of PSV lines.  This is really an enum type but using
# strings helps debugging in Python and helps detect using
# the wrong type (since it can't be confused with a STATE
# and all comparisons can copies are by address in Python)
#
TOP_HEADER_LINE = 'TopHeaderLine'
SECOND_HEADER_LINE = 'SecondHeaderLine'
KEYWORD_RECORD_LINE = 'KeywordRecordLine'
DATA_RECORD_LINE = 'DataRecordLine'
#
# Enum of PSV States.  This is really an enum type but using
# strings helps debugging in Python and helps detect using
# the wrong type (since it can't be confused with a LINE
# and all comparisons can copies are by address in Python)
#
EMPTY_STATE = 'EntryState'                  # beginning and after errors
OBSCONTEXT_STATE = 'ObsContextState'        # open # line ready to add ! lines
FIRST_OBSDATA_STATE = 'FirstObsDataState'   # ready to write header and element in obsBlock
OBSDATA_STATE = 'ObsDataState'              # ready to element in obsBlock
FIRST_DATA_STATE = 'FirstDataState'         # outside obsBlock
DATA_STATE = 'DataState'                    # outside obsBLock
#
# create regular expression matching a string with no
# character other than [A-Za-z_]. The first character
# of all keywords must match this set.  That means
# we don't have any strange characters in keywords
#
allAlpha = re.compile("^[A-Za-z_]*$")

def parsePSVLine(line):
    """ parsePSVLine classifies the PSV lines into 
          blank line:
            returns None
          TopHeader:
            returns (TOP_HEADER_LINE, [<name>, <reast of line>])
          SecondHeader:
            returns (SECOND_HEADER_LINE, [<name>, <reast of line>])
          KeywordRecord:
            returns (KEYWORD_RECORD_LINE, [<fields>, tag])
          DataRecord:
            returns (DATA_RECORD_LINE, [<fields>])
    """
    l = line.strip()  # strip leading and trailing whitespace

    if len(l) == 0:              # empty ines
       return None

    if l[:1] == '#':             # TopHeaderLine starts with '#' character
       return (TOP_HEADER_LINE, l[1:].split(None, 1))

    if l[:1] == '!':             # SecondHeaderLine starts with '!' character
       return (SECOND_HEADER_LINE, l[1:].split(None, 1))

                                 # pipe-separated fields with leading
                                 # and trailing whitespace removed
    fields = [ a.strip() for a in l.split('|') ]

                                 # Must be keyword header or data line
                                 # Classify using the requirement that 
                                 # all xml element names must start with
                                 # letters or an underscore (like C identifiers)
                                 #
                                 # note obsTime, a required field, must start
                                 # with a digit, so all valid keyword and data
                                 # lines may be distingusished this way
                                 #
                                 # The above is subtle because it only works
                                 # since obsTime is alwyas required.  This is
                                 # a hard-coded requirement on the ades standard
                                 #

    #if fields[:1] == ["permID"]: # If so, must be header not data.  This is a less
                                  # subtle way of distinguishing, but sometimes the
                                  # permID fields are all blank.  
                                  #

    firstChars = ''.join([ x[:1] for x in fields])  # first characgter from all fields
    if allAlpha.match(firstChars): # If so, must be header not data.  
       #
       # first determine the type tag and append to fields
       #
       #
       # the tag is identified from elements in header
       #   It is identified by the fields it contains
       #   It must match all the required elements and
       #   have no extra elements for 'optical', 'offset', 
       #   'occultation' or 'radar' -- these are the allowed 
       #   under 'obsBlock'
       #
       #  Need to check if no match occurs (None flags this)
       #
       s = set(fields)
       tag = None
       for possible in allowedElementDict['ades']:
          #
          # obsBlock is in this list but will never match
          #
          # no extra but all required elements must in s
          #
          if (s.issubset(allowedElementDict[possible]) and
              s.issuperset(requiredElementDict[possible])):
                tag = possible
       if (not tag):
          raise RuntimeError("No matching header type")

       fields.append(tag) # the last one is the tag

       return (KEYWORD_RECORD_LINE, fields)
    else:                          # if not header record, must be data
       return (DATA_RECORD_LINE, fields)


#
# State tables, actions, and global variables
#
# Notice there is some global communication
#   headerVals is the list of PSV header names in order
#
headerVals = []   # communication of header anmes




#
# State machine actions
#
def actionStatus(state, nextState, record, fields):
   """ helper function to print state machine status for
       better error reporting.
   """
   global lineNumber
   global stack
   return "line " + str(lineNumber) + " state: " +  str(state) + " nextState: " + str(nextState) \
        + " record: " + str(record) + "\n stack: " + str(stack) + " \nfields: " + str(fields)

def errorAction(state, nextState, record, fields):
   """ errorAction raises exceptions on error conditions
   """
   raise RuntimeError("ILLEGAL " + actionStatus(state, nextState, record, fields))


def firstObsBlockAction(state, nextState, record, fields):
   """ firstObsBlockAction Inserts new obsBlock and obsContext object 
       and adds the first obsContext element to it.
   """
   #
   # clear any old headerType since this a new obsBlock
   #
   global stack
   global headerType
   headerType = None
   #
   # put in obsBlock
   #
   stack.addPush('obsBlock')
   #
   # make new ObservationContext node
   # set stack to obsContext node; must be top
   #
   stack.addPush('obsContext')
   # 
   # make new fields[0] node with fields[1] data 
   # append new node to stack top level
   #
   return obsContextAction(state, nextState, record, fields, action=adesutility.ElementStack.addPush)


def closeObsBlockOpenObsBlockAction(state, nextState, record, fields):
   """ closeObsBlockOpenObsBlockAction closes an obsBlock and opens
       a new obsBlock
   """
   global stack
   global headerType
   headerType = None
   stack.pop() # close last element (optical/offset/occultation/radar)
   stack.pop() # close obsData
   stack.pop() # close obsBlock
   return firstObsBlockAction(state, nextState, record, fields)


def closeDataOpenObsBlockAction(state, nextState, record, fields):
   """ closeObsBlockOpenObsBlockAction closes an obsBlock and opens
       a new obsBlock
   """
   global stack
   stack.pop() # close last data element (optical/offset/occultation/radar)
   return firstObsBlockAction(state, nextState, record, fields)

def obsContextAction(state, nextState, record, fields, action=adesutility.ElementStack.addPopPush):
   """ obsContextAction Inserts next first-level item into XML obsContext
   """
   global stack
   #
   # create regular new node  -- may or may not have children.
   # PopPush closes old node
   #
   if (len(fields) < 2):  # may not have text -- don't crash 
      action(stack, fields[0], None)
   else:
      action(stack, fields[0], fields[1])
   return nextState

def subObsContextAction(state, nextState, record, fields):
   """ subObsContextAction Inserts secondLevel item into XML obsContext.  Must
       be after some obsContext item
   """
   global stack
   # make new fields[0] node with fields[1] data to top of stack node
   ###print ("sublevel node added to tree", fields[0], 'is', fields[1])
   if (len(fields) < 2):  # may not have text -- don't crash 
      stack.add(fields[0], None)
   else:
      stack.add(fields[0], fields[1])

   return nextState

def keywordHeaderAction(state, nextState, record, fields):
   """ keywordHeaderAction stores keyword header in headerVals
       No elements are added in this method; the keyword
       header will be written by the first DataAction routine
   """
   global headerType
   global headerVals
   headerVals = fields[:-1] # tag is the last element
   ###print ("keyword header found.  Verify type ")
   #
   #  Need to check if match has changed from one header
   #    to another, since the obsBlock must be
   #    all of the same type.
   #
   oldHeaderType = headerType
   headerType = fields[-1] # found by parser
   if oldHeaderType and (headerType != oldHeaderType):
      raise RuntimeError(
               "Only one header type allowed per obsBlock: " + 
               headerType + " vs. " + oldHeaderType 
            )
   return nextState

def openDataKeywordHeaderAction(state, nextState, record, fields):
   """ pop stack to close last Data element and then
       update haederType and headervals
   """
   global stack
   global headerType
   global headerVals
   headerVals = fields[:-1] # tag is the last element
   headerType = fields[-1]   # tag is the last element
   return nextState

def closeDataKeywordHeaderAction(state, nextState, record, fields):
   """ pop stack to close last Data element and then
       update haederType and headervals
   """
   global stack
   stack.pop()
   return openDataKeywordHeaderAction(state, nextState, record, fields)

def closeObsBlockKeywordHeaderAction(state, nextState, record, fields):
   """ closeObsBlockKeywordHeaderAction closes an obsBlock and reads
       a new keyword header to open data
   """
   global stack
   stack.pop() # close last element (optical/offset/occultation/radar)
   stack.pop() # close obsData
   stack.pop() # close obsBlock
   return openDataKeywordHeaderAction(state, nextState, record, fields)

def dataAction(state, nextState, record, fields, action=adesutility.ElementStack.addPopPush):
   """ dataAction checks to see if lengths match.  (maybe shorter is OK?)
       if OK, puts data in XML ElementTree
   """
   global stack
   global lineNumber
   global headerType
   if len(headerVals) < len(fields):
      raise RuntimeError("Line " + str(lineNumber) + " Record Mismatch: " + str(len(headerVals)) + " fields expected " \
                         + " but " + str(len(fields)) + " fields found")
   #
   # open element of headerType using action argument
   #
   action(stack, headerType) 

   #
   # add elements in right order for headerType
   #    first make a dict by using zip to make tuples
   #    zip truncates if fewer fields than headers
   d = dict(zip(headerVals, fields)) 
   #
   # now make extend data element in proper order
   #
   # first make a list of all found items in proper order
   #
   things = [item for item in allowedElementDict[headerType] if item in d and d[item] != '']
   #
   # then extend the to ElementStack element
   #
   #for item in things:
   #   stack.add(item, d[item])
   elements = adesutility.makeElementList( [ (item, d[item]) for item in things ] )
   stack.addElementList(elements)

   return nextState


def firstObsDataAction(state, nextState, record, fields):
   """ firstObsDataAction same as dataAction except closes obsContext first
   """
   global stack
   stack.pop()   # close last element in obsContext
   stack.pop()   # close obsContext
   stack.addPush("obsData")
   return dataAction(state, nextState, record, fields, action=adesutility.ElementStack.addPush)

def firstDataAction(state, nextState, record, fields):
   """ firstObsDataAction same as dataAction except it uses addPush instead of addPopPush
   """
   return dataAction(state, nextState, record, fields, action=adesutility.ElementStack.addPush)


#
# Main state table, with transtion and action tuples. 
# Fatal errors transition back to EmptyState since errorAction
# raises RuntimeError which either terminmates or is 
# handled by the caller.
#


stateTransitions = {
   EMPTY_STATE: {
      TOP_HEADER_LINE:         ( OBSCONTEXT_STATE,     firstObsBlockAction ),
      SECOND_HEADER_LINE:      ( EMPTY_STATE,          errorAction ),
      KEYWORD_RECORD_LINE:     ( FIRST_DATA_STATE,     openDataKeywordHeaderAction ),
      DATA_RECORD_LINE:        ( EMPTY_STATE,          errorAction ),
   },
   OBSCONTEXT_STATE: { 
      TOP_HEADER_LINE:         ( OBSCONTEXT_STATE,     obsContextAction ),
      SECOND_HEADER_LINE:      ( OBSCONTEXT_STATE,     subObsContextAction ),
      KEYWORD_RECORD_LINE:     ( FIRST_OBSDATA_STATE,  keywordHeaderAction ),
      DATA_RECORD_LINE:        ( EMPTY_STATE,          errorAction ),
   },
   FIRST_OBSDATA_STATE: {  # obsData inside obsBlock
      TOP_HEADER_LINE:         ( EMPTY_STATE,          errorAction ), # can't have empty obsContext
      SECOND_HEADER_LINE:      ( EMPTY_STATE,          errorAction ),
      KEYWORD_RECORD_LINE:     ( EMPTY_STATE,          errorAction ), # can't have empty obsData
      DATA_RECORD_LINE:        ( OBSDATA_STATE,        firstObsDataAction ),
   },
   OBSDATA_STATE: {        # obsData inside obsBlock
      TOP_HEADER_LINE:         ( OBSCONTEXT_STATE,     closeObsBlockOpenObsBlockAction ), 
      SECOND_HEADER_LINE:      ( EMPTY_STATE,          errorAction ),
      KEYWORD_RECORD_LINE:     ( FIRST_DATA_STATE,     closeObsBlockKeywordHeaderAction ),
      DATA_RECORD_LINE:        ( OBSDATA_STATE,        dataAction ),
   },
   FIRST_DATA_STATE: {  # outside obsBlock
      TOP_HEADER_LINE:         ( EMPTY_STATE,          errorAction ),  # can't have empty elements
      SECOND_HEADER_LINE:      ( EMPTY_STATE,          errorAction ),
      KEYWORD_RECORD_LINE:     ( EMPTY_STATE,          errorAction ),  # can't have empty elements
      DATA_RECORD_LINE:        ( DATA_STATE,           firstDataAction ),
   },
   DATA_STATE: {        # outside obsBlock
      TOP_HEADER_LINE:         ( OBSCONTEXT_STATE,     closeDataOpenObsBlockAction ),
      SECOND_HEADER_LINE:      ( EMPTY_STATE,          errorAction ),
      KEYWORD_RECORD_LINE:     ( FIRST_DATA_STATE,     closeDataKeywordHeaderAction ), 
      DATA_RECORD_LINE:        ( DATA_STATE,           dataAction ),
   },
}

state = EMPTY_STATE # Initial State

firstLine = True

def parsePSV(parsedPSVLine):
   """ parsePSV  is a state machine for
       parsing PSV, validating PSV, and
       creating corresponding XML

   """
   global state
   global stack
   global lineNumber
   global firstLine

   parsedLine = parsePSVLine(parsedPSVLine)
    
   if not parsedLine:  # ignore blank lines
      return;  

   #
   # first non-blank line must be "#version=2017"
   #
   # stuff the attribute into the first node here as well
   # so we can have all this in one place if we want to
   # find things in the future.
   #
   if (firstLine):
      firstLine = False
      l = parsedPSVLine.split('=')
      if len(l) != 2:
        raise RuntimeError("first line of PSV must specify version, e.g., '#version=2017'")
      #
      # strip all white space
      #
      if (''.join(l[0].split()) != '#version') :
        raise RuntimeError("first line of PSV must specify version, e.g., '#version=2017'")
      version_id = ''.join(l[1].split())
      # root node has no text or tail and one attribute
      stack = adesutility.ElementStack('ades', None, {'version':version_id} )
      return

   record = parsedLine[0]
   nextState = stateTransitions[state][record][0]
   #print (state, record, nextState)
   fields = parsedLine[1]
   #print (fields)
   state = stateTransitions[state][record][1](state, nextState, record, fields)
   


#
# psv files encoding should be 'utf-8'
#
#
# The following may be useful for encodings
# which cannot represent the full unicode
# character set:
#
#  import codecs
#  bs = codecs.encode(ustr, 'encoding', 'xmlcharrefreplace')
#  st = u'' + bs # to make a unicode string if desired in python 2
#
#  from HTMLParser import HTMLParser
#  parser = HTMLParser()
#  us = parser.unescape(st)
#
#  and us is now restored, except for those unfortunate cases where
#  the original unicode string contained things like "&#243;".  
#
# Alternatively, use
#  import codecs
#  bs = codecs.encode(ustr, 'encoding', 'backslashreplace')
#  st = u'' + bs # to make a unicode string if desired in python 2
#
#  This has the advantage that it can be decoded with
#  orig = codecs.decod(st, 'encoding', 'backslashreplace')
#
#
#

#
# default input and output encoding is 'UTF-8'
#
# Main routine
def psvtoxml(psvfile, xmlfile, psvencoding="UTF-8", xmlencoding="UTF-8"):

   with open(psvfile, encoding=psvencoding) as f:
      lineNumber = 0
      for line in f:
         try:
            lineNumber += 1
            parsePSV(line[:-1])
         except RuntimeError as e:
            print (e)
            exit (-1)


   # Tested encodings: 'UTF-16' 'UTF-16LE' 'UTF-16BE' 'UCS-4' 'UTF32' 'UTF-32BE' 'UTF-32LE'
   #                   'LATIN1' 'ISO-LATIN-1' 'ISO-8859-1' 'ASCII' 'cp500' 'cp037' 'UTF-7'
   #                   'windows-1252'
   treeTop = stack.takeTreeAndClear()
   treeTop.write(xmlfile, pretty_print=True, xml_declaration=True, encoding=xmlencoding)

def main():
   # construct argument parser for a conversion tool
   parser = convertutility.conversion_parser(
      description='Convert ADES PSV to XML.', 
   )
   args = parser.parse_args()
   # create callable
   call = lambda i, o : psvtoxml(i, o, psvencoding=args.input_encoding, xmlencoding=args.output_encoding)
   # call function with filename arguments
   convertutility.call_with_files(call, args)


#----------------------------------------------------
if __name__ == '__main__':
   main()
