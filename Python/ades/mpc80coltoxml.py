#!/usr/bin/env python3
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#
#Usage: mpc80coltoxml [--nosplit] <inmpcfile> [<outxmlfile>]
#
#
import sys
import os
import re
import io
import math
import argparse

from ades import adesutility
from ades import packUtil
from ades import sexVals
from ades import convertutility

#
# ignore blanks lines everywhere
#
blankRegex = re.compile( '^ *$' )
#
# header lines
#
# groups:
#   1: header keyword
#   2: header content
#   code is set to '0' as this does not conflict with data codes
#
# COD appears in data but not on MPC page
# ACK appears in data but not on MPC page
#
headerRegex = re.compile( '(ACK|COD|CON|OBS|MEA|TEL|NET|BND|COM|NUM|AC2) (.*)$' )

#
# matches optical line; also V and S and X
#
# groups: first seven are for all types
#   1: id group
#   2: discovery
#   3: notes -- notes can be anything; valid Notes is wrong
#   4: codes  and RvSsVvXx
#   5: yyyy  from obsDate
#   6: blank or a-e for asteroid satellites (embedded in obsDat)
#   7: rest of obsDate

commonRegexHelp1 = ( '([ A-Za-z0-9~][A-Za-z0-9 ]{11})'    # id group 1-12
                     + '([ *+])'                # discovery group 13 may be ' ', '*' or '+'
                     #+ '( AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345vzjeL16789])' # notes group 14
                     + '(.)'                 # notes can be anything
                     )
commonRegexHelp2 = ( r'(\d{4})'            # yyyy from obsDate 16-19
                     + '([ a-e])'            # asteroid satellite embedded in date 20
                     + '([0-9 .]{12})'       # rest of obsDate loosely checked 21-32 
                     )


# ----------- remainder depends on type.  This is for optical and SV
#   8: Ra
#   9: Dec
#  10: doc says blank but stuff is here
#  11: mag
#  12: band
#  13: packedref and astCode as first character
#  14: 3-character obs stn code
#
normalLineRegex = re.compile( ( '^' 
                                   + commonRegexHelp1  
                                   + '([A PeCBTMcEOHNnSVXx])' # codes group -- include SVXx but not Rrsv 15
                                   + commonRegexHelp2  
                                   + '([0-9 .]{12})'       # Ra loosely checked 33-44
                                   + '([-+ ][0-9 .]{11})'  # Dec loosely checked 45-56
                                   + '(.{9})'              # mpc doc says blank but not 57-65
                                   + '(.{5})'              # mag 66-70
                                   + '(.{1})'              # band 71
                                   + '(.{6})'              # packedref 72-77.  72 by itself is astCode
                                   + '(.{3})'              # obs stn 78-80
                                   + '$' )  )
#
# matches Radar first line (R)
#
# ----------- 1-7 as per optical
#   8: delay 33-47
#   9: shift 48-62
#  10: tfreq 63-68
#  11: tobs  69-71
#  12: packedref 72-77
#  13: obs stn   78-80
#
radarFirstLineRegex = re.compile( ( '^' 
                                   + commonRegexHelp1
                                   + '(R)'                 # code is Radar first line
                                   + commonRegexHelp2
                                   + '([0-9 .]{15})'     # Delay loosely checked 33-47
                                   + '([ +-][0-9 .]{14})'     # Shift loosely checked 48-62
                                   + '([0-9 .]{6})'      # tfreq loosely checked 63-68
                                   + '(.{3})'              # tobs loosely checked 69-71
                                   + '(.{6})'              # packedref 72-77
                                   + '(.{3})'              # obs stn 78-80
                                   + '$' )  )
#
# matches Radar second line (r)
#
# ----------- 1-7 as per optical
#   8: column 33 must be S(?)
#   9: delay uncertainty 34-47
#  10: shift uncertainty 48-62
#  11: tfreq uncertainty 63-68
#  12: tobs  69-71
#  13: packedref 72-77
#  14: obs stn  78-80
radarSecondLineRegex = re.compile( ( '^' 
                                   + commonRegexHelp1
                                   + '(r)'                 # code is Radar second line
                                   + commonRegexHelp2
                                   + '([SC])'              # column 33 must be S or C
                                   + '([0-9 .]{14})'     # Delay uncertainty loosely checked 33-47
                                   + '([0-9 .]{15})'     # Shift uncertainty loosely checked 48-62
                                   + '([0-9 .]{6})'      # tfreq uncertainty loosely checked 63-68
                                   + '(.{3})'              # tobs loosely checked 69-71
                                   + '(.{6})'              # packedref 72-77
                                   + '(.{3})'              # obs stn 78-80
                                   + '$' )  )
#
# matches Satellite second line (s)
#
#
# ----------- 1-7 as per optical
#   8: column 33 must be '1' or '2'
#   9: x 35-45
#  10: y 47-57
#  11: z 59-69
#  12: packedref 72-77
#  13: obs stn  78-80
satelliteSecondLineRegex = re.compile( ( '^' 
                                   + commonRegexHelp1
                                   + '(s)'                 # code is satellite second line
                                   + commonRegexHelp2
                                   + '([12])'              # column 33 must be parallax type 1 or 2
                                   + '.'                   # column 34 is unpsecified
                                   + '([+-][0-9 .]{10})'  # x columns 35-45
                                   + '.'                   # column 46 is unpsecified
                                   + '([+-][0-9 .]{10})'  # y columns 47-57
                                   + '.'                   # column 58 is unpsecified
                                   + '([+-][0-9 .]{10})'  # z columns 59-69
                                   + ' {2}'                # colunms 70-72 must be blank but 72 is astCode for packedref
                                   + '( .{5})'             # packedref 72-77 but 72 must be blank
                                   + '(.{3})'              # obs stn 78-80
                                   + '.*$' )  )
#
# matches Rover second line (v)
#
# ----------- 1-7 as per optical
#   8: E longitude  35-44
#   9: latitude 46-55
#  10: altitude 57-61
#  11: packedref 72-77
#  12: obs stn  78-80 must be 247
roverSecondLineRegex = re.compile( ( '^' 
                                   + commonRegexHelp1
                                   + '(v)'                 # code is rover second line
                                   + commonRegexHelp2
                                   + '1 '                  # column 33 must be 1, column 34 must be blank
                                   + '([-+0-9 .]{10})'     # E longitude columns 35-44
                                   + ' '                   # column 45 is space
                                   + '([-+0-9 .]{10})'     # latitude columns 46-55; N is + S is -
                                   + ' '                   # column 55 is blank
                                   + '([-+0-9 .]{5})'      # altitude is 57-61
                                   + ' {10}'                # colunms 62-71 must be blank
                                   + '(.{6})'             # packedref 72-77
                                   + '(247)'              # obs stn 78-80 must be 247
                                   + '.*$' )  )


def error80(msg, l):
   badLineMsg = 'Invalid MPC80COL line ('
   #print (badLineMsg, msg)
   raise RuntimeError(badLineMsg + msg + ') in line \n' + l)

def valueError(s, line, c1, c2, value=None):
   """ valueError raises an exception if s is not empty.
       Inputs:
          s: string to check for emptiness
          line: input line
          c1: first column in format
          c2: second column in format
          value:  if None must be all spaces.  Otherwise
                  must in the value tuple

       Return Value: None
       Exceptions:  RuntimeError if s is not empty
   """
   if value:
      if s not in value:
        if (c1 != c2):
           error80('columns ' + repr(c1) + '-' + repr(c2) + 
                  ' must be "' + repr(value) + '" not "' + s + '"', line)
        else:
           error80('column ' + repr(c1) +  
                   ' must be "' + repr(value) + '" not "' + s + '"', line)
   else:
      if not s.isspace():
        if (c1 != c2):
           error80('columns ' + repr(c1) + '-' + repr(c2) + 
                  ' must be blank not "' + s + '"', line)
        else:
           error80('column ' + repr(c1) +  
                   ' must be blank not "' + s + '"', line)



def prettyPrintDict(title, d):
   print (title,":")
   for i in sorted(d):
     print ("  ", i, d[i])



def decode80ColumnDataLine(line):
   """ decode80ColumnDataLine reaks an initial 80-col line in MPC
       format into its constituent parts and types.  The type may mean
       the next line is a continuation

       Input:  A line in 80-col format.  This is padded with spaces by 
               the caller

       Output:  A tuple.  If this is an optical first line:
           totalid: permid and provid fields -- used for artsat if not matching packed formats
           permid: unpacked Permanent ID or None
           provid: unpacked Provisional ID or None
           trkSub: trkSub field or None
           disc:   '*" (for discovery) or ''
           note:   1-character note or program code
           code:   This is an overloaded character.  
                   'V/v' means a roving observation with a second record.  
                   'R/r' means a radar observation with a second record.
                   'S/s' means a satellite observation
                   'O' means an offset observation (used only for natural satellites)
                   'E' means an occultation-derived observation
                   other values mean other things.  Black and 'P' mean the same thing
           date:  date of observtion in 'YYYY MM DD.dddddd' format.  The number of 'd's 
                  is important so this is returned as a string.
           ra:    observed j2000.0 ra in 'HH MM SS.ddd' format.  The number if 'd's is
                  so this is returned as a string
           decl:  observed j2000.0 dec in 'sDD MM SS.dd' format.  The 's' is +, -, or 
                  ' ' which means +.  The number of 'd's is important
           mag:   Observed magnitude
           band:  band for observed magnitude
           observatory:   three-character observatory code
       Output:  A tuple.  If this is a radar first line:
           totalid: permid and provid fields -- used for artsat if not matching packed formats
           permid: unpacked Permanent ID or None
           provid: unpacked Provisional ID or None
           disc:   '*" (for discovery) or ''
           note:   1-character note or program code
           code:   This is an overloaded character.  
                   'V/v' means a roving observation with a second record.  
                   'R/r' means a radar observation with a second record.
                   'S/s' means a satellite observation
                   'O' means an offset observation (used only for natural satellites)
                   'E' means an occultation-derived observation
                   other values mean other things.  Black and 'P' mean the same thing
           date:  date of observtion in 'YYYY MM DD.dddddd' format.  The number of 'd's 
                  is important so this is returned as a string.
           delay: delay time
           shfit: doppler shift
           tfreq: transmit frequency
           tobs:  transmit observatory three-character code
           rfreq: receive frequency
           robs:  receive observatory three-character code

       Exceptions:  raises "Invalid MPC80COL line (<reason>): <line> " is the line 
                    is not valid for some reason
   """
   if not line:
      return {}
   if len(line) > 80:
      error80 ( repr(len(line)) + ' columns ) ',line)
   ret  = {}

   m = headerRegex.match(line)
   if m:
      #print (m.groups(), m.group(1))
      ret['headerKeyword'] = m.group(1)
      ret['headerValue'] = m.group(2)
      ret['code'] = '0' # not in conflict with anything else
      return ret

   if len(line) != 80:
      error80 ( repr(len(line)) + ' columns -- only header may be shorter than 80) ',line)

   #ret['totalid'] = line[0:12]   # 1-12.  This is an artsat name if it doesn't match PermiD/ProvID
   #ret['disc'] =   line[12]     # 13  discovery flag is '*' for discovery
   #ret['notes'] =   line[13]     # 14  There is a list of valid notes
   #ret['code'] =   line[14]     # 15
   #ret['date'] =   line[15:32]  # 16-32  but watch for column
   #ret['packedref']  = line[71:77]   # 72-77   # packed reference. Blank for submissions
   if not m:
      ret['subFmt'] = 'M92'  # since were are MPC 80-col format
      m = normalLineRegex.match(line)  # optical, SVXx
      if m:
         #  print (m.groups())
         ret['totalid'] = m.group(1)
         ret['disc'] = m.group(2)
         ret['notes'] = m.group(3)
         ret['code'] = m.group(4)
         ret['date'] = m.group(5) + m.group(6) + m.group(7)

         ret['raSexagesimal']   =   m.group(8)
         ret['decSexagesimal'] =   m.group(9)
         ret['bl1']  =   m.group(10)
         ret['mag']  =   m.group(11)
         ret['band'] =   m.group(12)
         ret['packedref'] = m.group(13)
         ret['stn']  =   m.group(14)
      
         sexVals.checkDate(ret) # check date first
         sexVals.checkRa(ret)
         sexVals.checkDec(ret)

   if not m:
      m = radarFirstLineRegex.match(line)  # R
      if m:
         ret['totalid'] = m.group(1)
         ret['disc'] = m.group(2)
         ret['notes'] = m.group(3)
         ret['code'] = m.group(4)
         ret['date'] = m.group(5) + m.group(6) + m.group(7)
         # For delay, the implied decimal is after 11th col for microsec and after 5th col for sec.
         if m.group(8).strip() != '':  # radar fields are blank half the time
            ret['delay'] = m.group(8)[0:5] + '.' + m.group(8)[5:]
         else:
            ret['delay'] = ''
         if m.group(9).strip() != '':  # shift has sign
            ret['shift'] = m.group(9)[0:11] + '.' + m.group(9)[11:]
            ret['shift'] = packUtil.packSigned(ret['shift'])
         else: 
            ret['shift'] = ''
         if m.group(10).strip != '':
            ret['frq'] = m.group(10)[0:5] + '.' + m.group(10)[5:]
         else:
            ret['frq'] = ''
         ret['trx']  = m.group(11)
         ret['packedref'] = m.group(12)
         ret['stn']  = m.group(13)

   if not m:
      m = radarSecondLineRegex.match(line) # r
      if m:
         ret['totalid'] = m.group(1)
         ret['disc'] = m.group(2)
         ret['notes'] = m.group(3)
         ret['code'] = m.group(4)
         ret['date'] = m.group(5) + m.group(6) + m.group(7)

         ret['sc']  =  m.group(8)
         if m.group(9).strip() != '':  # radar fields are blank half the time
            ret['delay uncertainty'] = m.group(9)[0:10] + '.' + m.group(9)[10:]
         else:
            ret['delay uncertainty'] = ''
         if m.group(10).strip() != '':
            ret['shift uncertainty'] = m.group(10)[0:11] + '.' + m.group(10)[11:]
         else:
            ret['shift uncertainty'] = ''
         ret['frq continuation'] = m.group(11)
         ret['trx']  = m.group(12)
         ret['packedref'] = m.group(13)
         ret['stn']  = m.group(14)
         #print (m.groups())
         pass
   if not m:
      m = satelliteSecondLineRegex.match(line) # s
      if m:
         ret['totalid'] = m.group(1)
         ret['disc'] = m.group(2)
         ret['notes'] = m.group(3)
         ret['code'] = m.group(4)
         ret['date'] = m.group(5) + m.group(6) + m.group(7)

         ret['parallax_type'] = m.group(8)
         ret['ctr'] = '399'
         ret['pos1'] = packUtil.packSigned(m.group(9))
         ret['pos2'] = packUtil.packSigned(m.group(10))
         ret['pos3'] = packUtil.packSigned(m.group(11))
         if ret['parallax_type'] == '1': # ICRF-KM
            ret['sys'] = "ICRF_KM"
            if m.group(9)  != packUtil.unPackSigned(ret['pos1'], 11, 7) or \
               m.group(10) != packUtil.unPackSigned(ret['pos2'], 11, 7) or \
               m.group(11) != packUtil.unPackSigned(ret['pos3'], 11, 7):
                error80("Improper decimal point location", line)
         else: # ret['parallax_type'] == '2' ICRF-AU
            ret['sys'] = "ICRF_AU"
            if m.group(9)  != packUtil.unPackSigned(ret['pos1'], 11, 3) or \
               m.group(10) != packUtil.unPackSigned(ret['pos2'], 11, 3) or \
               m.group(11) != packUtil.unPackSigned(ret['pos3'], 11, 3):
                error80("Improper decimal point location", line)
         ret['packedref'] = m.group(12)
         ret['stn'] = m.group(13)
         #print (m.groups())
         pass
   if not m:
      m = roverSecondLineRegex.match(line) # v
      if m:
         ret['totalid'] = m.group(1)
         ret['disc'] = m.group(2)
         ret['notes'] = m.group(3)
         ret['code'] = m.group(4)
         ret['date'] = m.group(5) + m.group(6) + m.group(7)

         ret['sys'] =  'WGS84'        # always
         ret['ctr'] =  '399'        # always
         ret['pos1'] =  m.group(8)  # E longitude
         ret['pos2'] =  m.group(9)     # latitude
         ret['pos3'] =  m.group(10)    # altitude
         ret['packedref'] = m.group(11)
         ret['stn'] =  m.group(12)
         #print (m.groups())
         pass

   if not m:
      error80 ("no match for line", line)

   # 
   # more value sanity checks
   #
   rdr = 'trx' in ret.keys()
   sexVals.checkDate(ret, rdr) # check date always

   #if ( ret['notes'] == 'X' ): 
   #    print (lineNumber, ":", line)
   # Validate col 15
   if ( ret['code'] not in packUtil.validCodes):
      error80 ("invalid column 14 " + ret['code']+ " in line " +  repr(lineNumber), line)
   # Validate col 14
   if (ret['stn'] in packUtil.programCodeSites):
       if ( ret['notes'] not in packUtil.validProgramCodes):
            error80 ("invalid program code "+ ret['notes']+ " in line "+ repr(lineNumber), line)
   else:
        if ( ret['notes'] not in packUtil.validNotes):
            error80 ("invalid note "+ ret['notes'] +" in line "+ repr(lineNumber), line)
   # This SOHO/STEREO business is now handled a) differently and b) in packUtil.py
   #notesExceptions = {
   #  '249': { '2': 'A',   # SOHO 2->A, 3->B
   #           '3': 'B',
   #         },
   #  'C49': { '4': 'G',   # STEREO A 4->G 5->H
   #           '5': 'H',
   #         },
   #  'C50': { '4': 'O',   # STEREO A 4->O 5->P
   #           '5': 'P',
   #         },
   #}
   #stn = ret['stn']
   #if stn in notesExceptions:
   #   note = ret['notes']
   #   if note in notesExceptions[stn]:
   #      ret['notes'] = notesExceptions[stn][note]

   if ( ret['notes'] not in packUtil.validProgramCodes): # allow any station
       error80 ("invalid program code "+ ret['notes']+ " in line "+ repr(lineNumber), line)

   ret['astCat']   = ret['packedref'][0] # catalog code; 72 - first in packed reference. Blank for submissions

   #
   # compute unpacked ID fields.  This may be only a trkSub
   #
  
   (permID, provID, trkSub) = packUtil.unpackPackedID(ret['totalid'])
   ret['permID'] = permID
   ret['provID'] = provID
   ret['trkSub'] = trkSub
   # print("IDs:", ret['totalid'], permID, provID, trkSub) #DEBUG
   
   try:
     packtest =  packUtil.packTupleID( (permID, provID, trkSub) )
     if packtest != ret['totalid']:
        print ("ID does not round-trip; " + packtest + " vs. " + ret['totalid'])
   except Exception as e:
     print ("fails pack: ", permID, provID, trkSub, e)

   return ret

#
# Sometimes we have to combine lines in order to make a complete field
# This is the case for Rr, Vv and Ss pairs.  This should be a generator
# but for now it just calls the callBack function
#
def parseFile(f, callBack):
      global lineNumber
      oldCode = 'None' # must not be null for in to work -- valids are all 1 char
      oldDataLine = None
      for l in f:
         if lineNumber%1000000 == 0: print ("at line", lineNumber)
         if blankRegex.match(l[:-1]): # skip empty or blank lines
            #print ("line", lineNumber, "is", len(l[:-1]), 'columms of space')
            continue
         try:
            #print (':' + l[:-1]  + ':')
            badCombo = False
            dataLine = l[:-1]
            line = decode80ColumnDataLine(dataLine)
            newCode = line['code']
   
   
            #
            # check for two-line mismatch
            #
            if (oldCode in 'RSV' and newCode != oldCode.lower()):
               print ()
               print (oldCode + '/' + oldCode.lower() +  " mismatch at" ,lineNumber,"new was " + newCode + ":")
               print ("oldDataLLine", oldDataLine)
               print ("dataLine    ", dataLine)
               badCombo = True
         
            if (newCode in 'rsv' and newCode.upper() != oldCode):
               print ()
               print (newCode + '/' + newCode.upper() +  " mismatch at" ,lineNumber,"old was " + oldCode  + ":")
               print ("oldDataLLine", oldDataLine)
               print ("dataLine    ", dataLine)
               badCombo = True
         
   
            #
            # now yield valid lines and combinations
            #
            nextThing = None
            if not badCombo:
               if (oldCode in 'RSV'):
                  if ( (line['totalid'] != oldLine['totalid']) or \
                     (line['date'] != oldLine['date']) or \
                     (line['stn'] != oldLine['stn']) ):
                     print ("Contintuation line mismatch at",i)
                     print ("oldLine", oldLine)
                     print ("line", line)
                  if (oldCode == 'R'): # radar
                     if (line['trx'] != oldLine['trx']):
                        print ("Radar Contintuation line trx mismatch at",i)
                        print ("oldLine", oldLine)
                        print ("line", line)
                     oldLine['sc'] = line['sc']
                     if line['sc'] == 'S':
                        oldLine['com'] = '0'
                     if line['sc'] == 'C':
                        oldLine['com'] = '1'
                     oldLine['rmsDelay'] = line['delay uncertainty']
                     oldLine['rmsDoppler'] = line['shift uncertainty']
                     oldLine['frq continuation'] = line['frq continuation']
                     oldLine['rcv'] = line['stn'] # for xml
                     oldLine['doppler'] = oldLine['shift'] # for xml
                     oldLine['ref'] = oldLine['packedref'] # for xml?
                     #print ("Rr at",lineNumber,":")
   
                  if (oldCode == 'S'): # satellite
                     oldLine['sys'] = line['sys']
                     oldLine['ctr'] = line['ctr']  # always 399
                     oldLine['pos1'] = line['pos1']
                     oldLine['pos2'] = line['pos2']
                     oldLine['pos3'] = line['pos3']
                     #print ("Ss at",lineNumber,":")
   
                  if (oldCode == 'V'): # rover
                     oldLine['sys'] = line['sys']  # always WGS84
                     oldLine['ctr'] = line['ctr']  # always 399
                     oldLine['pos1'] = line['pos1']  # E long
                     oldLine['pos2'] = line['pos2']   # lat
                     oldLine['pos3'] = line['pos3']   # alt
                     #print ("Vv at",lineNumber,":")
   
               if (newCode in 'rsv'):
                  nextThing = oldLine  # with new fields from line
                  oldCode = None
               else:
                  if (newCode  not in 'RrSsVv'):
                     nextThing = line # all opticals (some Xx)
   
            #
            # save for continuation lines only
            #
            if newCode in "RSV":
               oldLine = line
               oldDataLine = dataLine
               oldCode = newCode
            else:
               oldLine = None
               oldDataLine = None
               oldCode = 'None' # can't be None and still work
   
            if nextThing:  # could yield it up but instead call down -- works in C++
               if callBack:
                  callBack(nextThing, lineNumber)

         except RuntimeError as e:
            print ("Error in line ", lineNumber)
            print (e)

#
# callback functions (or None if only syntax check is wanted)
#
# printit:  classifies and prints the found items
# toXML:    classifies and puts items in xml tree
#
# This really needs to use the generator model since there are
# things to finalize and intermediate states.
#
headerCodes = "0"  # header lines
roverCodes = "V"   # rover lines
radarCodes = "R"   # radar lines
satelliteCodes = "S" # satellite lines
opticalCodes = "A PeCBTMcHNnXs"   # optical codes are also detector types, and include Xx
offsetCodes = "E"       # offset -- how to process?
occultationCodes = "O"  # occultation -- how to process?
codeTable = {}

def _initCodeTable():
   global codeTable;
   for i in opticalCodes:
     codeTable[i] = 'Optical'
   for i in offsetCodes:
     codeTable[i] = 'Offset'
   for i in occultationCodes:
     codeTable[i] = 'Occultation'
   for i in roverCodes:
     codeTable[i] = 'Rover'
   for i in radarCodes:
     codeTable[i] = 'Radar'
   for i in satelliteCodes:
     codeTable[i] = 'Satellite'
   for i in headerCodes:
     codeTable[i] = 'Header'

_initCodeTable()


#
# print the parsed lines
#
def printit(item, lineNumber):
  code = item['code']
  try:
     codeType = codeTable[code]
  except:
     codeType = None

  print ('line ', lineNumber,'code is', code, ', type is ', codeType)
  prettyPrintDict("Found code " + code + ' at line ' + repr(lineNumber), item);

#
# convert to XML -- note preamble and postamble since we aren't using yield
#
outXMLFile = None
_submission_mode = False
# Elements valid in the general schema but not in the submission schema (submit.xsd)
_non_submission_elements = {'subFmt', 'precTime', 'precRA', 'precDec', 'subFrm', 'deprecated'}

def convertitPreamble(fname, output_encoding='utf-8'):  # set up elementTree
   global outXMLFile
   global stack
   global allowedElementDict
   global firstElement
   global inObsBlock
   global firstObsBlock
   if fname is None:
       return
   #print ("set up elementTree")
   outXMLFile = fname

   (allowedElementDict, requiredElementDict, psvFormatDict)  = adesutility.getAdesTables()
   MPC80OpticalElements = ['permID', 'provID', 'trkSub', 'mode', 'stn',
                           'obsTime', 'ra', 'dec', 'mag', 'band']
   firstElement = True
   firstObsBlock = True
   inObsBlock = False
   # root node has no text or tail and one attribute
   stack = adesutility.ElementStack('ades', None, {'version':'2022'} )
   




def convertitPostamble(fname, output_encoding='utf-8'):
   global outXMLFile
   if outXMLFile is None:
       return
   #print ("write tree on ", outXMLFile)
   # Tested encodings: 'UTF-16' 'UTF-16LE' 'UTF-16BE' 'UCS-4' 'UTF32' 'UTF-32BE' 'UTF-32LE'
   #                   'LATIN1' 'ISO-LATIN-1' 'ISO-8859-1' 'ASCII' 'cp500' 'cp037' 'UTF-7'
   #                   'windows-1252' 'UTF-8'
   treeTop = stack.takeTreeAndClear()
   treeTop.write(fname, pretty_print=True, xml_declaration=True, encoding=output_encoding)


def convertit(item, lineNumber):
  global firstElement
  global firstObsBlock
  global inObsBlock
  global stack
  global commentList
  global obsContextList
  global obsContextSeen
  if outXMLFile is None:
      return
  code = item['code']
  try:
     codeType = codeTable[code]
  except:
     codeType = None

  if codeType != 'Header':
    if inObsBlock:
       if obsContextList: # print out other header lines in order
          for obsContextTuple in obsContextList:  # but respect order
             (hkey, hval, hlist) = obsContextTuple
             stack.addPush(hkey, hval)
             for sub in hlist:
                stack.add(sub[0], sub[1]) # sub is (key, value)
             stack.pop()
       if commentList:  # print out comments last
          stack.addPush('comment')
          for commentLine in commentList:
             stack.add('line', commentLine)
          stack.pop()
       stack.addPopPush('obsData') # ends obsContext
       inObsBlock = False

  #
  # how to convert 'Offset' and 'Occultation' values? -- as Optical with 
  # 'OFF' and 'OCC' as the 'mode' field.  This round-trips.
  #
  if codeType == 'Satellite': # same as rover fields for ICRF_AU and ICRF_KM
     pass
  if codeType == 'Offset': # same as optical but code E -> 'OFF'
     pass
  if codeType == 'Occultation': # same as optical but code O -> 'OCC'
     pass
  if codeType == 'Rover':  # same as optical but extra fields
     if item['pos3'].strip() == '':  # this is an error so quit
        print ("skipping line ", lineNumber,
               "because altitude is missing for rover")
        return
     pass
  if codeType == 'Optical' or \
     codeType == 'Rover' or \
     codeType == 'Satellite' or \
     codeType == 'Offset' or \
     codeType == 'Occultation':
     if (firstElement):
         stack.addPush('optical')
         firstElement = False
     else:
         stack.addPopPush('optical')
     #
     # then extend to the ElementStack element in the proper order
     # as determined by MPC80OpticalElements
     #
     # don't add None or '' items.  Note str(item[x]).strip() test after None test
     #
     #for item in things:
     #   stack.add(item, d[item])
   
     if code in 'Xx':  # deprecated with disc flag
        code = 'C' # mode set below
        item['deprecated'] = 'X' # what about x?
     elif code == 'A':  # set subFrm
        item['subFrm'] = 'B1950.0' # PHA mode but set below
        code = 'P'
     elif code == 'V':  # Rover
        code = 'C' # CCD
     elif code == 'S':  # Satellite
        code = 'C' # CCD
     item['mode'] = packUtil.codeDict[code]
     #
     # translate astCat char into IAU ADES value
     #
     astCodeVal = item['astCat']
     if not astCodeVal or astCodeVal not in packUtil.catCodes:
        item['astCat'] = 'UNK'
     else:
        item['astCat'] = packUtil.catCodes[astCodeVal]
     if item['mag']:
        if item['band'].strip() == '':
          item['band'] = 'UNK'  # UNK is default if blank
     if item['band']:  # dump band if no mag
        if item['mag'].strip() == '':
          item['band'] = None

     # For the moment treat col 14 as a program code if this obscode uses them,
     # otherwise leave it as a note. This may be the wrong translation in a few
     # cases:
     # * If the observation was not published by the MPC then the
     # observer may have put a note in column 14, which the MPC will
     # eventually overwrite with the program code.
     # * If the observatory used to not have program codes and then
     # after a certain date it did. Before the switch col 14 will
     # always be a note and after the switch it will always be a
     # program code.
     # * N.B. that there are special cases where the distinction
     # betwenn note and program code is blurry. These are for STEREO
     # and SOHO as discussed here:
     # https://minorplanetcenter.net/iau/info/ObsNote.html The current
     # implementation will leave these cases as notes.
     if (item['notes'] != ' ' and item['stn'] in packUtil.programCodeSites):
         # We have a non-blank col 14 for an obscode that uses program
         # codes. Therefore treat col 14 as 'prog' and clear 'notes'.
         item['prog'] = packUtil.packProgID(item['notes'])  # convert to ADES 2-char base 62
         item['notes'] = ' '

     #item['ref'] = item['packedref'][1:]  # astCat now has first character
     item['ref'] = packUtil.unpackRef(item['packedref'][1:])  # astCat now has first character


     d = allowedElementDict['optical']
     #print ( [x for x in item if x not in d ] )
     skip = _non_submission_elements if _submission_mode else set()
     elements = adesutility.makeElementList( [ (x, str(item[x]).strip())
                for x in d if x in item and item[x] and str(item[x]).strip() and x not in skip] )
     stack.addElementList(elements)

     #prettyPrintDict("Found code " + code + ' at line ' + repr(lineNumber), item);
     pass
  if codeType == 'Radar':
     if (firstElement):
         stack.addPush('radar')
         firstElement = False
     else:
         stack.addPopPush('radar')

     d = allowedElementDict['radar']
     #print ( 'radar', [(x, item[x]) for x in item if x not in d ] )
     skip = _non_submission_elements if _submission_mode else set()
     elements = adesutility.makeElementList( [ (x, str(item[x]).strip())
                for x in d if x in item and item[x] and str(item[x]).strip() and x not in skip] )
     stack.addElementList(elements)
     pass

  if codeType == 'Header':  # headers introduce obsBlocks
     if not inObsBlock:  # open obsBlock
         if firstObsBlock:
              firstObsBlock = False
              stack.addPush('obsBlock')
         else:
              stack.pop()  # end last element in old block (must be data or inObsBlock is True)
              stack.pop()  # end obsData
              stack.addPopPush('obsBlock')  # create new obsBlock
         stack.addPush('obsContext')        # with new obsContext
         commentList = []
         obsContextList = []
         obsContextSeen = []
     inObsBlock = True
     firstElement = True # for later optical/offset/occultation/radar additions

     #
     # now process the elements -- all of them are one line but some turn into
     # more than one line and COM is special
     #
     hkey = item['headerKeyword']
     hval = item['headerValue']
     if hkey == 'COM':  # comment
        commentList.append(hval)
     else:
        if hkey not in obsContextSeen: # ignore multiple lines
           obsContextSeen.append(hkey)
           if hkey == 'COD':  # mpcCode
             subval = ('mpcCode', hval)
             obsContextList.append( ( 'observatory', None, [subval] ) )
           elif hkey == 'CON':  # submitter and institution
             hvals = hval.split(',', 1)
             sub = [ ('name', hvals[0] ) ]
             try:
                sub.append( ('institution', hvals[1] ) )
             except:
                pass
             obsContextList.append( ( 'submitter', None, sub ) )
           elif hkey == 'OBS':  # list of names of observers
             hvals = hval.split(',')
             sub = []
             for i in hvals:
               sub.append ( ('name', i) )
             obsContextList.append( ( 'observers', None, sub ) )
           elif hkey == 'MEA':  # list of names for measurers
             hvals = hval.split(',')
             sub = []
             for i in hvals:
               sub.append ( ('name', i) )
             obsContextList.append( ( 'measurers', None, sub ) )
           elif hkey == 'TEL':  # telescope -- just punt for now
             sub = [ ('name', hval) ]
             sub.append( ( 'design', 'Unknown') )
             sub.append( ( 'aperture', '9999') )
             sub.append( ( 'detector', 'Unknown') )
             obsContextList.append( ( 'telescope', None, sub ) )
           else: # ignore 'NET', 'ACK', 'AC2', 'BND', 'NUM'
             #obsContextList.append( ( hkey, hval, [] ) )
             pass

     #print("Found Header " + hkey + ' at line ' + repr(lineNumber) + ": " + hval, firstObsBlock, inObsBlock, firstElement);


#---------------------------------------------------------------------------
#
# The following generators are for splitting lines or not splitting lines. 
# Each generator is responsible for setting lineNumber
#

#
# generator to just read lines one by one
#

def doNotSplitRadar(fname, input_encoding='utf-8'):
   global nSplit
   global splitLines
   global lineNumber
   nSplit = 0
   splitLines = []
   lineNumber = 0
   with open(fname, "r", encoding=input_encoding) as f:
      for l in f:
         lineNumber += 1
         yield l[0:81]

#---------------------------------------------------------------------------
#
# generator and helper function to split radar lines
#
def parseRadarLine(l):
   """ splits a line into compenents needed to
       check flag (column 13) and doppler/delay
       fields. 
   """
   try:
      l1 = l[0:14]
      flag = l[14]
      l2 = l[15:34]
      doppler = l[34:47]
      delay = l[47:61]
      l3 = l[61:]
      return (l1, flag, l2, doppler, delay, l3)
   except:
      raise RuntimeError("Invalid line")
    

def splitRadar(fname, input_encoding='utf-8'):
   """ splitRadar(fname) 

       opens fname and reads it as an 80-col MPC file

       It checks radar entries, which are R/r pairs.  R must
       be followed by r.  It does no other checking.

       If doppler and delay are both specified, it replaces the
       radar with two entries; otherwise it just passes the 
       entries through.

       It raises RuntimeError on any syntax problem.

       It yields line for a normal line, but two Rr pair
       lines if the R line has both doppler and delay

   """
   global nSplit
   global splitLines
   global lineNumber
   nSplit = 0
   splitLines = []

   with open(fname, "r", encoding=input_encoding) as f:
      lineNumber = 1
      l1 = f.readline()[0:81]  # remove trailing newline and/or cr
      try:
         while (l1):  # emulate do .. while structure
            if headerRegex.match(l1):
               yield l1
            else:
               (al1, aflag, al2, adoppler, adelay, al3) = parseRadarLine(l1)
               if aflag != 'R':   # just pass through
                  yield l1
               else:              # need second line
                  l2 = f.readline()[0:81]  # remove trailing newline
                  (bl1, bflag, bl2, bdoppler, bdelay, bl3) = parseRadarLine(l2)
                  if bflag != 'r':
                     raise RuntimeError("flag must be r not "  +  bflag)

                  if (adoppler.strip() and adelay.strip()): # If both are present make two entries
                     nSplit += 1
                     splitLines.append (lineNumber)
                     yield al1 + aflag + al2 + adoppler + 14*' ' + al3
                     lineNumber += 1
                     yield bl1 + bflag + bl2 + bdoppler + 14*' ' + bl3
                     lineNumber -= 1
                     yield al1 + aflag + al2 + 13*' ' + adelay + al3
                     lineNumber += 1
                     yield bl1 + bflag + bl2 + 13*' ' + bdelay + bl3
                  else: # normal case just yield l1 and then l2
                     yield l1
                     lineNumber += 1
                     yield l2
               
            lineNumber += 1
            l1 = f.readline()[0:81]
      except Exception as e:
         raise RuntimeError(repr(e) + " in line " + str(lineNumber))

   lineNumber -= 1 # line number at end should be last line

#---------------------------------------------------------------------------
def mpc80coltoxml(inmpcfile, outxmlfile, nosplit=False, input_encoding='utf-8', output_encoding='utf-8', submission=False):
   global _submission_mode
   _submission_mode = submission
   func = doNotSplitRadar if nosplit else splitRadar
   try:

      #
      # for xml output
      #
      convertitPreamble(outxmlfile, output_encoding=output_encoding)
      parseFile(func(inmpcfile, input_encoding=input_encoding), convertit)
      convertitPostamble(outxmlfile, output_encoding=output_encoding)

   except Exception as e:
      print(e)
      parseFile(func(inmpcfile, input_encoding=input_encoding), None)

   #print()
   #print()
   if nSplit:
      print (nSplit, "radar lines split out of", lineNumber, "lines")
      print ("split lines:")
      for i in splitLines:
         print (i, '/', i+1)
   #print ("Statistics:")
   #sexVals.printCounts()

def main():
   # construct argument parser for a conversion tool
   parser = convertutility.conversion_parser(
      description='Convert MPC obs80 to ADES XML.', 
   )
   parser.add_argument("--nosplit", action="store_true", help="will not split doppler/delay radar into two elements; elements with doppler and delay will not validate")
   parser.add_argument("--submission", action="store_true", help="omit elements not valid in the submission schema (subFmt, precTime, precRA, precDec, etc.)")
   parser.add_argument("--val-only", action="store_true", help="check validity of input obs80, but do not output XML file")

   args = parser.parse_args()

   try:
      # check if only doing validation
      if args.val_only:
         if args.input is not sys.stdin and args.output is not sys.stdout:
            raise Exception("Error: cannot request output file for --val-only")
         else:
            # send output to /dev/null on Unix or null on Window
            args.output = os.devnull
      
      # create callable
      call = lambda i, o : mpc80coltoxml(i, o, nosplit=args.nosplit, input_encoding=args.input_encoding, output_encoding=args.output_encoding, submission=args.submission)
      # call function with filename arguments
      convertutility.call_with_files(call, args)
   except Exception as e:
      print("Error", e)
      parser.print_help()
      exit(-1)


#---------------------------------------------------------------------
if __name__ == '__main__':
   main()
