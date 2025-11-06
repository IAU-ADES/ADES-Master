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
import argparse
import io

from collections import OrderedDict

from ades import convertutility

#
# write encoded output for psv.  Default encoding
# for psv is utf-8
#
encodedout = None

#
# sys.argv[1]: input xml file
# sys.argv[2]: output psv file
# example: ./psvtoxml.py <xml file> <psv file>
#
import sys

from ades import adesutility
from ades.adesutility import applyPaddingAndJustification

def setFromElementDictList(element):
   """ makes a set from the allowedElementDict list for elemnt """
   return set([t for t in allowedElementDict[element]])

def processDataElement(first, element):
   global dataDicts
   global headerInfo
   global headerDict # need to preserve across calls to this routine
                     # only used to find i in headerInfo first element
                     # of tuple quickly ( hash vs. O(n) )
   global psvList    # need to preserve across calls

   subDict = {}
   for i in element:
      (childtag, childtext) = adesutility.getElementTagText(i)
      if childtext:      # add to dict if child has text -- this excludes localUse
                         # because localUse has no text
         subDict[childtag] = childtext

   #
   # see if we already have a header for the type
   #
   if first:
     #
     # name, width, length, and justification
     #
     headerInfo =  []
     headerDict = {}
     tag = element.tag
     psvList = []
     #
     # headerItem entries are:
     #
     #             [name   width     fmt   dpos  seen]
     #  headerItem[0]: name of the field
     #  headerItem[1]: width of the field (may expand)
     #  headerItem[2]: fmt is 'L', 'R', or 'D'
     #  headerItem[3]: dpos the decimal point location for 'D' (integer)
     #  headerItem[4]:  True/False, whether this has been seen.  Only
     #                  headerItems from the psvList may have seen=False,
     #                  since the other are geneerated when seen.
     #
     #
     for j in psvFormatDict[tag]:
       #             [name   width     fmt   dpos  seen]
       psvList.append(j[0])  # keep for adding other elements
       headerItem = [ j[0], int(j[1]), j[2], j[3], False ]
       headerInfo.append(headerItem)
       headerDict[j[0]] = headerItem # reference semantics is your friend

     #
     # adjust lengths if header doesn't fit
     #
     for headerItem in headerInfo:
        if len(headerItem[0]) > headerItem[1]: # too wide
          headerItem[1] = len(headerItem[0])

     #
     # add in the rest of the allowed elements between notes and remarks
     #
     for j in allowedElementDict[tag]:  # allowed elements
        if j not in psvList:      # not already in list
            #
            # Insert before "remarks", which is the last item
            #
            headerItem = [j, len(j), 'R', 0, False ]
            headerInfo.insert(-1, headerItem)
            headerDict[j] = headerItem


     dataDicts = []  # store subDicts


   for i in subDict:  # now adjust headerInfo
      if i in headerDict:  # apply justification and extend if needed
         headerItem = headerDict[i]  # reference semantics means update headerInfo
         #
         # if not in psvList and not seen and just == 'R' or 'L' then maybe adjust
         #
         if not (headerItem[0] in psvList) and not headerItem[4] and headerItem[2] in 'RL':
            #
            # justification is unchanged unless there is a '.' character.
            # This heuristic is not fool-proof but works for our
            # typical cases.
            just = headerItem[2]
            n = 0
            try:  # check for '.' and set D<n> using it
               n = subDict[i].index('.') + 1
               just = 'D'
            except:
               pass
            headerItem[2] = just
            headerItem[3] = n

         headerItem[4] = True # this has been seen
         (stemp, width, dposnew) = applyPaddingAndJustification(subDict[i],
                                                                headerItem[1],
                                                                headerItem[2],
                                                                headerItem[3])
         #if len(stemp) > headerItem[1]:  # check just takes extra time
         headerItem[1] = width
         #if dposnew != headerItem[3]:
         headerItem[3] = dposnew
      else: # not seen -- insert before "remarks" which is last item -- should not happen now
         #print ( 'bong', i )
         #print (psvList)
         #
         # length is max of len(i) and len(subDict[i])
         #
         l = len(subDict[i])
         if l < len(i):
           l = len(i)

         #
         # justification is 'R' unless there is a '.' character.
         # This heuristic is not fool-proof but works for our
         # typical cases.
         just = 'R'
         n = 0
         try:  # check for '.' and set D<n> using it
            n = subDict[i].index('.') + 1
            just = 'D'
         except:
            pass
         #
         # Insert before "remarks", which is the last item
         #
         # This has just been seen, so the last item is True
         #
         headerItem = [i, l, just, n, True ]
         headerInfo.insert(-1, headerItem)
         headerDict[i] = headerItem

   dataDicts.append(subDict) # add to the list


def processObsBlock(element):
   first = True
   for child in element:
      tag = child.tag

      if tag not in allowedObsBlockSet:
        raise RuntimeError("Cannot have tag " + tag + " in obsBlock");

      elif tag == "obsContext":
        processObsContext(child)

      elif tag == "obsData": # an empty obsData is not allowed in PSV
         for grandchild in child:
            tag = grandchild.tag
            if first:
               obsDataType = tag
               if tag not in allowedObsDataSet:
                  raise RuntimeError("Cannot have tag " + tag + " in obsData");
            elif tag != obsDataType:
               raise RuntimeError("Cannot mix tag " + tag + " with tag " +
                                  obsDataType + "in obsData")
            processDataElement(first, grandchild)
            first = False

#
#
#
def processAdesElement(element):
   """ processAdesElement (element)

       Inputs:
          element:  element of a tree

   """
   global dataDicts
   if element.tag != "ades":
      raise RuntimeError("Root element must be ades for PSV conversion");

   dataDicts = []   # printDataDicts won't print anything if empty
   lastDataTagType = None  # logic here is to print the dataDict when
                           # the next block is found.
   #
   # write header with same version found in XML input
   #
   ades_ver = element.attrib['version'];
   sline = "# version=" + ades_ver
   print (sline, file=encodedout)

   for child in element:
      tag = child.tag
      if tag not in allowedAdesSet:
         raise RuntimeError("tag " + tag + " not allowend in ades")

      if tag == "obsBlock":
         printDataDicts()
         lastDataTagType = None
         processObsBlock(child)  # do not print data dicts inside
         lastDataTagType = tag

      else: # must be allowed non-obsBlock data element
        if tag != lastDataTagType:
          printDataDicts()
          lastDataTagType = tag
          first = True;
        processDataElement(first, child)
        first = False

   printDataDicts()   # push out the last one


def printDataDicts():
   global dataDicts
   global headerInfo

   if (dataDicts):  # don't print anything if no entries ([])
      #
      # first print headers
      #
      first = True
      sline = ''
      for headerItem in headerInfo:
         if headerItem[4]:  # don't print if not seen ever
            if not first:
               sline += '|'
            first = False
            (stemp, w, dposnew) = applyPaddingAndJustification(headerItem[0],
                                                               headerItem[1],
                                                               'L',
                                                                0)
            sline +=  stemp
      sline = sline.rstrip()  # remove trailing whitespace from remarks
      print (sline, file= encodedout)
      #
      # now print data records
      #
      for subDict in dataDicts :
        sline = ''
        first = True
        for headerItem in headerInfo:
          if headerItem[4]:  # don't print if not seen ever
            if not first:
               sline += '|'
            first = False
            if headerItem[0] in subDict:
              (stemp, w, dposnew) = applyPaddingAndJustification(subDict[headerItem[0]],
                                                                 headerItem[1],
                                                                 headerItem[2],
                                                                 headerItem[3])
            else:
              stemp = headerItem[1] * ' '  # blanks
            sline +=  stemp
        sline = sline.rstrip()  # remove trailing whitespace from remarks
        print (sline, file= encodedout)



def processObsContext(element):
  for i in element:
    (tag, text) = adesutility.getElementTagText(i)
    # check for tag being allowed
    sline = "# " + tag + ' ' + text # in python2, unicode + bytes -> unicode
    sline = sline.rstrip() # remove trailing whitespace
    print (sline, file=encodedout)
    for j in i:
      (childtag, childtext) = adesutility.getElementTagText(j)
      # check for tag being allowed
      sline = "! " + childtag + ' ' + childtext  # in python2, unicode + bytes -> unicode
      sline = sline.rstrip() # remove trailing whitespace
      print (sline, file=encodedout)


#
# read in allowedElementDict, requiredElementDict  and psvFormatDict
#

# Important note: it is very complicated and time consuming to change this routine.
# I will keep it as it is and we can only call it through command line

(allowedElementDict, requiredElementDict, psvFormatDict) = \
                                       adesutility.getAdesTables()

allowedObsDataSet = setFromElementDictList('obsData')
allowedObsBlockSet = setFromElementDictList('obsBlock')
allowedAdesSet = setFromElementDictList('ades')

def xmltopsv(xmlfile, psvfile, psvencoding="UTF-8"):
   global encodedout
   inputTree = adesutility.readXML(xmlfile)
   with open(psvfile, 'w', encoding=psvencoding) as encodedout:
      processAdesElement(inputTree.getroot())
   
def main():
   # construct argument parser for a conversion tool
   parser = convertutility.conversion_parser(description="Convert ADES XML to PSV")
   args = parser.parse_args()
   # create callable
   call = lambda i, o : xmltopsv(i, o, psvencoding=args.output_encoding)
   # call function with filename arguments
   convertutility.call_with_files(call, args)

if __name__ == "__main__":
   main()