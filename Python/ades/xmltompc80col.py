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
import io
from collections import OrderedDict
import sys
import argparse
from ades import adesutility
from ades import packUtil
from ades import sexVals
from ades import convertutility


def setFromElementDictList(element,allowedElementDict):
   """ makes a set from the allowedElementDict list for elemnt """
   return set([t for t in allowedElementDict[element]])

def processDataElement(first, element):
   global dataDicts
   global headerInfo
   global headerDict # need to preserve across calls to this routine
                     # only used to find i in headerInfo first element
                     # of tuple quickly ( hash vs. O(n) )

   subDict = [element.tag, {}]
   for i in element:
      (childtag, childtext) = adesutility.getElementTagText(i)
      if childtext:      # add to dict if child has text -- this excludes localUse
                         # because localUse has no text
         subDict[1][childtag] = childtext
 
   if first:
     dataDicts = []  # store subDicts
   dataDicts.append(subDict) # add to the list


def processObsBlock(element,allowedObsBlockSet,allowedObsDataSet):
   first = True
   for child in element:
      tag = child.tag

      if tag not in allowedObsBlockSet:
        raise RuntimeError("Cannot have tag " + tag + " in obsBlock");

      elif tag == "obsContext" and not noHeader:
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
def processAdesElement(element,allowedObsDataSet,allowedAdesSet,allowedObsBlockSet):
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
   # no header with version
   #
   #sline = "# version=2017"
   #print (sline, file=encodedout)

   for child in element:
      tag = child.tag
      if tag not in allowedAdesSet: 
         raise RuntimeError("tag " + tag + " not allowend in ades")

      if tag == "obsBlock":
         printDataDicts()
         lastDataTagType = None
         processObsBlock(child,allowedObsBlockSet,allowedObsDataSet)  # do not print data dicts inside
         lastDataTagType = tag

      else: # must be allowed non-obsBlock data element
        if tag != lastDataTagType:
          printDataDicts()
          lastDataTagType = tag
          first = True;
        processDataElement(first, child)
        first = False

   printDataDicts()   # push out the last one

def hasKeyOrVal(d, key, val):
   """ regularize missing keys for xml
       Inputs:
          d: a dictionary
          key: a key
          val: if key is not present
       Output:
          either d[key] or val if key not in d
       Errors:  RuntimeError if types are wrong
   """
   if key in d:
     return d[key]
   else: 
     return val

# from https://bitbucket.org/mpcdev/xmlto80/src/master/
bandconv = {'Vj': 'V',
            'Rc': 'R',
            'Ic': 'I',
            'Bj': 'B',
            'Uj': 'U',
            'Sg': 'g',
            'Sr': 'r',
            'Si': 'i',
            'Sz': 'z',
            'Pg': 'g',
            'Pr': 'r',
            'Pi': 'i',
            'Pz': 'z',
            'Pw': 'w',
            'Ao': 'o',
            'Ac': 'c',
            'Gb': 'G',
            'Gr': 'G'}

def printOpticalLine(item):
   """ printOpticalLine decodes and prints an optical element
       Input:
          item:  a dictionary of optical sub-elements
       Output: None
       Side Effects:  prints mpc 80-column line on encoded-out
   """
   permID = hasKeyOrVal(item, 'permID', None)
   provID = hasKeyOrVal(item, 'provID', None)
   trkSub = hasKeyOrVal(item, 'trkSub', None)
   artSat = hasKeyOrVal(item, 'artSat', None)
   if artSat != None:
       packedID = artSat.rjust(12, str(' ')) # If artSat is present then ignore other designation info
   else:
       packedID = packUtil.packTupleID( (permID, provID, trkSub) )
   disc = hasKeyOrVal(item, 'disc', ' ')
   notes = hasKeyOrVal(item, 'notes', ' ')
   notes = notes[0] # restrict to length of 1
   precTime = float(hasKeyOrVal(item, 'precTime', defaultPrecTime) )
   precRa = float(hasKeyOrVal(item, 'precRA', defaultPrecRA) )
   precDec = float(hasKeyOrVal(item, 'precDec', defaultPrecDec) )
   sexDate = sexVals.isoToSexDate(item['obsTime'], precTime)
   if(item['stn'] == '275'):
      sexRa = sexVals.decRaToSexRa(item['raStar'], precRa)
      sexDecl = sexVals.degDeclToSexDecl(item['decStar'], precDec)  
   elif(item['stn'] == '244'): #This has not been tested because at the moment we don't have any data 
      sexRa = sexVals.decRaToSexRa(item['raStar']+item['deltaRA'], precRa)
      sexDecl = sexVals.degDeclToSexDecl(item['decStar']+item['deltaDec'], precDec)
   else:
      sexRa = sexVals.decRaToSexRa(item['ra'], precRa)
      sexDecl = sexVals.degDeclToSexDecl(item['dec'], precDec)
   #mag = "{0:5s}".format(hasKeyOrVal(item, 'mag', ''))
   mag = adesutility.applyPaddingAndJustification(hasKeyOrVal(item, 'mag', ''), 5, 'D', 3)[0]
   mag = mag[0:5] # restrict to length of 5
   band = hasKeyOrVal(item, 'band', ' ')
   # NEW APPROACH: USE 1ST CHARACTER
   if len(band) > 1:
      band = band[1]
   
   #This won't work
   #if len(band) > 1: band = '!' # Don't truncate the band, but instead write a nonsense character

   # OLD APPROACH: USE 2ND CHARACTER IF IN BANDCONV HASH ABOVE...
   #   if len(band) > 1:
   #      #band = band[1] # take the second character for 2-character band.  This does not invert
   #      if band in bandconv:
   #          band = bandconv[band]
   #      else:
   #          band = ' '

   #
   # map astCat to single-character packing
   #
   astCat = item['astCat']
   if astCat.strip() not in packUtil.rCatCodes:
      astCat = ' '
   else:
      astCat = packUtil.rCatCodes[item['astCat']]
   #packedref = "{0:<5s}".format(hasKeyOrVal(item, 'ref', ' ')[-5:])
   packedref = packUtil.packRef(hasKeyOrVal(item, 'ref', ' '))

   deprecated = hasKeyOrVal(item, 'deprecated', None)
   if deprecated:
      code = deprecated  # right now just X
   
   prog = hasKeyOrVal(item, 'prog', None)
   if prog:  # This changes the meaning of the notes field
      notes = packUtil.unpackProgID(prog)

   if deprecated:
      code = deprecated  # right now just X
   elif 'pos1' in item: # this is a rover or satellite so write second line
      if item['sys'] == 'WGS84':
         code = 'V'
      elif item['sys'] == 'ICRF_AU':
         code = 'S'
      elif item['sys'] == 'ICRF_KM':
         code = 'S'
      else: # illegal for 80-column format
         raise RuntimeError("Illegal sys " + item['sys'] + ' for MPC 80-Col')
   elif 'subFrm' in item:
      code = 'A'
   else:
      code = packUtil.reverseCodeDict[item['mode']]

   sline =  packedID + disc + notes + code + \
            sexDate + sexRa + sexDecl + \
            '         ' + mag + band + \
            astCat + packedref + item['stn']
   print (sline, file= encodedout)
   if 'pos1' in item: # this is a rover or satellite so write second line
      if item['sys'] == 'WGS84':
         pos1 = adesutility.applyPaddingAndJustification(item['pos1'], 11, 'D', 4)[0]
         pos2 = adesutility.applyPaddingAndJustification(item['pos2'], 11, 'D', 4)[0]
         pos3 = "{0:>5s}".format(item['pos3']) + ' '
         pos1 = pos1[0:11]
         pos2 = pos2[0:11]
         sline =  packedID + disc + notes + 'v' + \
                  sexDate + '1 ' + pos1 +  pos2 +  pos3 + \
                  '         ' + astCat + packedref + item['stn']
      elif item['sys'] == 'ICRF_AU':
         pos1 = packUtil.unPackSigned(item['pos1'], 11, 3)
         pos2 = packUtil.unPackSigned(item['pos2'], 11, 3)
         pos3 = packUtil.unPackSigned(item['pos3'], 11, 3)
         pos1 = pos1[0:11]
         pos2 = pos2[0:11]
         pos3 = pos3[0:11]
         sline =  packedID + disc + notes + 's' + \
                  sexDate + '2 ' + pos1 +  ' ' + pos2 +  ' ' + pos3 + ' ' + \
                  '  '+ packedref + item['stn']
      elif item['sys'] == 'ICRF_KM':
         pos1 = packUtil.unPackSigned(item['pos1'], 11, 7)
         pos2 = packUtil.unPackSigned(item['pos2'], 11, 7)
         pos3 = packUtil.unPackSigned(item['pos3'], 11, 7)
         pos1 = pos1[0:11]
         pos2 = pos2[0:11]
         pos3 = pos3[0:11]
         sline =  packedID + disc + notes + 's' + \
                  sexDate + '1 ' + pos1 +  ' ' + pos2 +  ' ' + pos3 + ' ' + \
                  '  '+ packedref + item['stn']
      else: # illegal for 80-column format but already checked
         pass
      print (sline, file= encodedout)
    
def printRadarLine(item):
   """ printRadarLine decodes and prints a radar element
       Input:
          item:  a dictionary of radar sub-elements
       Output: None
       Side Effects:  prints mpc 80-column line on encoded-out
   """
   permID = hasKeyOrVal(item, 'permID', None)
   provID = hasKeyOrVal(item, 'provID', None)
   trkSub = hasKeyOrVal(item, 'trkSub', None)
   packedID = packUtil.packTupleID( (permID, provID, trkSub) )
   disc = hasKeyOrVal(item, 'disc', ' ')
   notes = hasKeyOrVal(item, 'notes', ' ')
   precTime = 1  # fixed for radar
   sexDate = sexVals.isoToSexDate(item['obsTime'], precTime)
   astCat = ' '
   #packedref = "{0:<5s}".format(hasKeyOrVal(item, 'ref', '      ')[-5:])
   packedref = packUtil.packRef(hasKeyOrVal(item, 'ref', ' '))

   #doppler =     "{0:>15s}".format(hasKeyOrVal(item, 'doppler', ''))
   #rmsDoppler =  "{0:>14s}".format(hasKeyOrVal(item, 'rmsDoppler', ''))
   #delay =     "{0:>15s}".format(hasKeyOrVal(item, 'delay', ''))
   #rmsDelay =  "{0:>15s}".format(hasKeyOrVal(item, 'rmsDelay', ''))
   #frq =     "{0:<6s}".format(hasKeyOrVal(item, 'frq', ''))

   doppler = hasKeyOrVal(item, 'doppler', '               ')
   od = doppler
   doppler = packUtil.unPackSigned(doppler, 16, 12)
   doppler = doppler[0:11] + doppler[12:] # remove '.'

   rmsDoppler = hasKeyOrVal(item, 'rmsDoppler', '               ')
   od = rmsDoppler
   rmsDoppler = adesutility.applyPaddingAndJustification \
                                  (rmsDoppler, 16, 'D', 12)[0]
   rmsDoppler = rmsDoppler[0:11] + rmsDoppler[12:] # remove '.'
   
   delay = hasKeyOrVal(item, 'delay', '               ')
   od = delay
   # delay is in seconds in ADES. So decimal (to be dropped) is 6th character...
   delay = adesutility.applyPaddingAndJustification \
                                  (delay, 16, 'D', 6)[0]
   delay = delay[0:5] + delay[6:] # remove '.'


   rmsDelay  = hasKeyOrVal(item, 'rmsDelay', '              ')
   od = rmsDelay
   rmsDelay = adesutility.applyPaddingAndJustification \
                                  (rmsDelay, 15, 'D', 11)[0]
   rmsDelay = rmsDelay[0:10] + rmsDelay[11:] # remove '.'

   frq = hasKeyOrVal(item, 'frq', '       ')
   od = frq
   frq = adesutility.applyPaddingAndJustification \
                                  (frq, 7, 'D', 6)[0]
   frq = frq[0:5] + frq[6:] # remove '.'

   scval = hasKeyOrVal(item, 'com', '0') # no good default
   if scval == '0':
     sc = 'S'
   if scval == '1':
     sc = 'C'
   # first radar line
   #sline =  packedID + disc + notes + code + \
   #         sexDate + sexRa + sexDecl + \
   #         + item['stn']
   sline = packedID + disc + notes + 'R' + sexDate + \
           delay + doppler + frq +\
           item['trx'] + ' ' + item['ref'] + item['rcv']
   print (sline, file= encodedout)
   # second radar line
   sline = packedID + disc + notes + 'r' + sexDate +\
           sc + rmsDelay + rmsDoppler + '      ' +\
           item['trx'] + ' ' + item['ref'] + item['rcv']
   print (sline, file= encodedout)
   
def printDataDicts():
   global dataDicts
   global headerInfo

   if (dataDicts):  # don't print anything if no entries ([])
      #
      # now print data records -- subDict is [ <element name>, <dictionary>]
      #
      for subDict in dataDicts :
        eType = subDict[0]
        if eType == 'optical' or eType == 'occultation':  # process optical -- may be rover or converted offset or occultation
           printOpticalLine(subDict[1])
        elif eType == 'radar':  # process radar
           printRadarLine(subDict[1])
        else:
           print ("Error: can't process " + subDict[0] + ' elements in mpc80')




def processObsContext(element):
  """ prints obsContext in MPC 80-col format
      This depends on the tag type and 
      is fragile
  """
  for i in element:
    (tag, text) = adesutility.getElementTagText(i)
    # check for tags we allow
    if tag == 'comment':
       for j in i: # each line is a separate COM entry
         (childtag, childtext) = adesutility.getElementTagText(j)
         if childtag == 'line':
            sline = "COM " + childtext
            print (sline, file=encodedout)

    elif tag == 'observatory':  # right now the mpcCode sub-element is the one that matters
       for j in i: # look for mpcCode -- ignore <name> for now
         (childtag, childtext) = adesutility.getElementTagText(j)
         if childtag == 'mpcCode':
            sline = "COD " + childtext
            print (sline, file=encodedout)

    elif tag == 'telescope':  # right now the name sub-element is the one that matters
       for j in i: # The name element has the original text
         (childtag, childtext) = adesutility.getElementTagText(j)
         if childtag == 'name':
            sline = "TEL " + childtext
            print (sline, file=encodedout)

    elif tag == 'submitter':
       names = []
       for j in i: # a list of names
         (childtag, childtext) = adesutility.getElementTagText(j)
         if childtag == 'name':  # only one allowed if valid
            names.append(childtext)
         if childtag == 'institution': # optional but must be after <name>
            names.append(childtext)

       sline = "CON " + ', '.join(names)
       print (sline, file=encodedout)

    elif tag == 'observers':
       names = []
       for j in i: # a list of names
         (childtag, childtext) = adesutility.getElementTagText(j)
         if childtag == 'name':
            names.append(childtext)

       sline = "OBS " + ', '.join(names)
       print (sline, file=encodedout)

    elif tag == 'measurers':
       names = []
       for j in i: # a list of names
         (childtag, childtext) = adesutility.getElementTagText(j)
         if childtag == 'name':
            names.append(childtext)

       sline = "MEA " + ', '.join(names)
       print (sline, file=encodedout)

    else:  # not an orignal entry so just do stuff or ignore it
       pass
       #sline = "# " + tag + ' ' + text # in python2, unicode + bytes -> unicode
       #sline = sline.rstrip() # remove trailing whitespace
       #print (sline, file=encodedout)
       #for j in i:
       #  (childtag, childtext) = adesutility.getElementTagText(j)
       #  # check for tag being allowed
       #  sline = "! " + childtag + ' ' + childtext  # in python2, unicode + bytes -> unicode
       #  sline = sline.rstrip() # remove trailing whitespace
       #  print (sline, file=encodedout)
  
#----------------------------------------------------------------------
#Main routine
def xmltompc80col(xmlfile, mpcencdoing='utf-8'):
   global encodedout
   #
   # read in allowedElementDict, requiredElementDict  and psvFormatDict
   #
   (allowedElementDict, requiredElementDict, psvFormatDict) = \
      adesutility.getAdesTables()

   # Let's do this!
   inputTree = adesutility.readXML(xmlfile)

   allowedObsDataSet = setFromElementDictList('obsData',allowedElementDict)
   allowedObsBlockSet = setFromElementDictList('obsBlock',allowedElementDict)
   allowedAdesSet = setFromElementDictList('ades',allowedElementDict)

   processAdesElement(inputTree.getroot(),allowedObsDataSet,allowedAdesSet,allowedObsBlockSet)

noHeader = False
# Set obs80 precision constants
defaultPrecTime = '1'
defaultPrecRA = '0.001'
defaultPrecDec = '0.01'

def main():
   # Input arguments
   # construct argument parser for a conversion tool
   parser = convertutility.conversion_parser(
      description='Convert ADES XML to MPC obs80 format.', 
      input_help="XML file name", 
      output_help="obs80 file name",
   )
   parser.add_argument("--lowPrec", action='store_true', \
                       help= "Export Time, RA, and DEC in lower precision.")
   parser.add_argument("--noHeader", action='store_true', \
                       help = "Do not export ADES obsContext information to obs80 header.")
   args = parser.parse_args()
   
   global noHeader
   noHeader = args.noHeader

   if args.lowPrec:
      global defaultPrecTime
      defaultPrecTime = '10'
      global defaultPrecRA
      defaultPrecRA = '0.01'
      global defaultPrecDec
      defaultPrecDec = '0.1'

   # create callable
   def call(i, o):
      global encodedout
      with open(o, "w", encoding=args.output_encoding) as encodedout:
         xmltompc80col(i)
   
   # call function with filename arguments
   convertutility.call_with_files(call, args)

# --- Start executable code -----------------------------
if __name__ == '__main__':
   main()
