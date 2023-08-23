# !/usr/bin/env python
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

import adesutility

#
# codes and translations
#
#   codeDict for optical type
#   programCodeSites for station codes
#   catCodes for astcAT translation
# 
codeDict = {  # converts code to mode for optical type
 # 'A': 'PHA', # sets subFrm to 'B1950.0' maps to 'PHO'

  'P': 'PHo', # P is obsolete MPC conversion for photographic -- see Xx
  ' ': 'PHO', # blank means photographic
  'e': 'ENC',
  'C': 'CCD',
  'B': 'CMO',
  'T': 'MER',
  'M': 'MIC',
  'c': 'ccd',
  'E': 'OCC',
  'O': 'OFF',
  'H': 'PMT', # hipparcos
  'N': 'NOR',
  'n': 'VID',

 #  'X': 'Pho',  # maps to CCD
 #  'x': 'pho',  # maps to CCD

 # 'V': 'CCD', # by type
 # 'S': 'CCD', # by type
}
reverseCodeDict = { codeDict[i] : i for i in codeDict }  # no duplicates

validCodes = "A PeCBTMcEOHNnRrSsVvXx"+"0"  # 0 is special for header lines
validNotes = ' AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345vzjeL16789'
validProgramCodes = ' AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345016789=#$%"&\+-![]`!|(){}.?@,^;:_/~*<>eLvzjZ'"'"
programCodesArray = "0123456789!\"#$%&'()*+,-./[\]^_`{|}~:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
programCodeSites = \
set([ "010",
      "012",
      "084",
      "089",
      "094",
      "095",
      "121",
      "260",
      "261",
      "262",
      "266",
      "267",
      "268",
      "269",
      "290",
      "309",
      "413",
      "561",
      "568",
      "658",
      "673",
      "675",
      "688",
      "689",
      "695",
      "696",
      "705",
      "807",
      "809",
      "950",
      "A84",
      "B35",
      "D90",
      "E03",
      "E10",
      "E26",
      "F65",
      "G40",
      "G73",
      "G83",
      "H06",
      "I03",
      "I05",
      "I11",
      "I89",
      "J13",
      "N50",
      "Q62",
      "U69",
      "V07",
      "W84",
      "W88",
      "Z18",
      "Z19",
      "Z20",
      "249",
      "C49",
      "C50 ", ])

catCodes = { ' ': 'UNK',
             'a': 'USNOA1',
             'b': 'USNOSA1',
             'c': 'USNOA2',
             'd': 'USNOSA2',
             'e': 'UCAC1',
             'f': 'Tyc1',
             'g': 'Tyc2',
             'h': 'GSC1.0',
             'i': 'GSC1.1',
             'j': 'GSC1.2',
             'k': 'GSC2.2',
             'l': 'ACT',
             'm': 'GSCACT',
             'n': 'SDSS8',
             'o': 'USNOB1',
             'p': 'PPM',
             'q': 'UCAC4',
             'r': 'UCAC2',
             's': 'USNOB2',  # USNOB2 missing on ADES web page
             't': 'PPMXL',
             'u': 'UCAC3',
             'v': 'NOMAD',
             'w': 'CMC14',
             'x': 'Hip2',
             'y': 'Hip1',
             'z': 'GSC',
             'A': 'AC',
             'B': 'SAO1984',
             'C': 'SAO',
             'D': 'AGK3',
             'E': 'FK4',
             'F': 'ACRS',
             'G': 'LickGas',
             'H': 'Ida93',
             'I': 'Perth70',
             'J': 'COSMOS',
             'K': 'Yale',
             'L': '2MASS',
             'M': 'GSC2.3',
             'N': 'SDSS7',
             'O': 'SSTRC1',
             'P': 'MPOSC3',
             'Q': 'CMC15',
             'R': 'SSTRC4',
             'S': 'URAT1',
             'T': 'URAT2',  # URAT2 missing on ADES web page
             'U': 'Gaia1',
             'V': 'Gaia2',
             'W': 'Gaia3',
             'X': 'Gaia3E',  
             'Y': 'UCAC5',  # UCAC5 mission on ADES web page
             'Z': 'ATLAS2', 
             '0': 'IHW', 
             '1': 'PS1_DR1', 
             '2': 'PS1_DR2', 
             '3': 'Gaia_Int', 
             '4': 'GZ', 
             '5': 'UBSC', 
             '6': 'Gaia_2016', 
           }

rCatCodes = { catCodes[i]:i for i in catCodes }

#
# see https://minorplanetcenter.net/iau/info/References.html
# for a description of how references are packed and unpacked
# for cols 72-77 in the 80-col format
#
# This only handles cases A, B, C, D and E for now. The reference
# to journals are just clumsily copied
#
def packRef(ref):
   #
   # first is "MPC"
   #
   newref = ref
   if ref[0:3] == "MPC":  # cases A-C on the web page
      s = int(ref.split()[1] )
      if s < 100000:  # case A: a 5-digit number
         newref = str(s + 100000)[1:] # with leading zeroes
      elif s < 200000: # case B: @ + 4-digit number
         newref = '@' + str(s-100000+10000)[1:] # with leading zeroes
      else: # case C:  # + radix62_4
        newref = '#' + radix62_4(s - 110000)[1:]
   elif ref[0:3] == "MPS":
      s = int(ref.split()[1] )
      if s < 259999: # digit as letter and 4 digits case D
        c = "abcdefghijklmnopqrstuvwxyz"[int(s/10000)]
        newref = c + str(int(s%10000)+10000)[1:] # with leading zeroes
      else:  # tilde and base-62 -- case E in the web page
        newref = radix62_4(s - 260000)

   packedref = "{0:<5s}".format(newref[-5:])
   return packedref

def unpackRef(packedref):
   if packedref[0] in '0123456789': # MPC case A
      packedref = "MPC  " + str(int(packedref)) # <5-digit number>
   elif packedref[0] == '@': # MPC case B
      packedref = "MPC  " + str(100000 + int(packedref[1:])) # @<4-digit number>
   elif packedref[0] == '#': # MPC case C
      print ("packedref = ", '~'+packedref[1:])
      n = 110000 + unRadix62_4(packedref) # ~<4-digit radix 62>
      packedref = "MPC  " + str(n)
  
   elif packedref[0] in 'abcdefghijklmnopqrstuvwxyz':  # MPS case D
      n = int(packedref[1:]) + 10000*'abcdefghijklmnopqrstuvwxyz'.index(packedref[0])
      packedref = "MPS  " + str(n) # <letter + 4-digit base 10>
   elif packedref[0] == '~': # MPS case E
      n = 260000 + unRadix62_4(packedref) # ~<4-digit radix 62>
      packedref = "MPS  " + str(n)
     
   return packedref


def packProgID(c): # for program code id -- must be alpha
   # should be radix-52 with 0-1 first
   try:
      codeIndex = programCodesArray.index(c)
   except:
      raise RuntimeError("Illegal program code " + c)
   
   if codeIndex > 51:
      first = '1'
   else:
      first = '0' 

   second = packLetters[codeIndex%52]

   return  first + second 

def unpackProgID(s): # for program code id -- must be alpha
   # should be radix-52 with 0-1 first
   if len(s) != 2 or s[0] not in "01":
      raise RuntimeError ("Illegal packed prog ID " + s + " in xml")
  
   try:
      codeIndex = unpackLetters[s[1]]
      if s[0] == 1:
        codeIndex += 52
      packed = programCodesArray[codeIndex]
   except:
      raise RuntimeError ("Illegal packed prog ID " + s + " in xml")

   return packed

#
# packed implicit decimal converter
#
def packImplicitDecimal(value, width, decimal):
   """ packs a float into a string of width 
       with an implicit decimal point in column decimal
   """
   v = float(value)
   digits = width - decimal 
   fmt = '{0:'+ repr(width) + '.' + repr(digits) + 'f}'
   #print (fmt, v)
   ret = fmt.format(v)
   return ret

def unpackImplicitDecimal(s, decimal):
   """ unpacks a string with an implicit decimal point
       in column decimal """
   return s

#
# packSigned and unpackSigned handles case
# where where the first character is + or -
# and there may be spaces before the digits. 
# This is turned into a signed number for XML
#
def packSigned(value):
   """ packed a number with spaces after the sign
      
       This is a text-only maniuplation

       Inputs:
         value:  A signed number, such as "+   0.32"

       Return Value:
                 The packed string for xml: "+0.32"              
   
       Errors:  None for inputs matching regex

   """
   s = value[0] #  '+', '-' or ' '
   ret = value[1:].strip()  # remove leading and trailing spaces
   if s != ' ':
     ret = s + ret
   return ret
  
def unPackSigned(value, outLen, nDecimal):
   """ unpacks a number into a signed format
       possibly with spaces after the sign.

       This is a text-only maniuplation

       Inputs:
         value:  from packedSign such as "+32.3"
         outLen:    total length of field
         nDecimal: position of decimal point in field

       Return Value:
         The field in in unpacked format, such as "+  32.3   "

       Errors: RuntimeError for values that don't fit

   """

   s = value[0]
   #
   # adjust if there is no leading '+' since mpc 80-col needs one
   #
   # s must be all digits but the regex ensures that
   #
   if s in "0123456789":
      value = '+' + value # add leading +
      s = '+'

   if s not in "+-":
      ret = adesutility.applyPaddingAndJustification(value,
                                           outLen, 'D', nDecimal)[0]
   else:
      ret = s + adesutility.applyPaddingAndJustification(value[1:],
                                           outLen-1, 'D', nDecimal-1)[0]
   return ret
      



# PermID and ProvID pack/unpack
#
# PermID for a minor planet is a postive integer
# PermID for a comet is a positive integer followed by P or D
#   Comets may have fragments
# PermID for a natural satellite is "Jupiter VIII" or J8 ?
#
# ProvID for a minor planet is 
# ProvID for a comet is 
#   Comets may have fragments
# ProvID for a natual satellite is 
#
# a Packed PermID for a minor planet may use A-Z or a-z to encode
# the first digit of the integer for numbers > 10000
#
# a Packed ProvID for a minor planet
#     J95X00A -> 1995 XA
#     J95X01A -> 1995 XA1
#     J95Xa1A -> 1995 XA361
#  unless it is a survey
#     2050 P-L -> PLS2040
#     3138 T-1 -> T1S2040
#        There may be minor planets which become comets.
# a Packed ProvID for a comet
#   Comets may have fragments
# a Packed ProvID for a natural satellite

#minorplanetPackedPermIDRegex = re.compile('^([0-9A-Za-z])(\d{4})$')
#cometPackedPermIDRegex = re.compile('^(\d{4})([PD])$')
#satellitePackedPermIDRegex = re.compile('^([JSUN])(\d{3})S$')

#minorplanetPackedProvIDRegex = re.compile('^ ([I-K])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)([A-HJ-Z])$')
#minorplanetSurveyPackedProvIDRegex = re.compile('^ (PL|T1|T2|T3)S(\d{4})$')
#cometPackedProvIDRegex = re.compile('^([ACDPX])([0-9A-Za-z])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)([0A-Z])$')
#cometfragmentPackedProvIDRegex = re.compile('^([CDPX])([0-9A-Za-z])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)([a-z])$')
#satellitePackedProvIDRegex = re.compile('^S([0-9A-Za-z])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)0$')

minorplanetProvIDRegex = re.compile('^(\d{2})(\d{2}) ([A-HJ-Y])([A-HJ-Z])(\d+)?$')
minorplanetSurveyProvIDRegex = re.compile('^(\d{4}) (P-L|T-1|T-2|T-3)$')
cometProvIDRegex = re.compile('^([ACDPX])/(\d{4}) ([A-Z])([A-Z])?(\d*)$')
cometfragmentProvIDRegex = re.compile('^([CDPX])/(\d{4}) ([A-Z])(\d*)-([A-Z])$')
satelliteProvIDRegex = re.compile('^S/(\d{4}) ([JSUN]) (\d+)$')

minorplanetPermIDRegex = re.compile('^(\d+)$')
cometPermIDRegex = re.compile('^(\d+)([PDI])$') # add I for interstellar objects
cometfragmentPermIDRegex = re.compile('^(\d+)([PDI])-([A-Z]{1,2})$') # like this will happen for interstellar objects
satellitePermIDRegex = re.compile('^(Jupiter|Saturn|Uranus|Neptune) (\d+)$')
asteroidsatellitePermIDRegex = re.compile('^\((\d+|\d{4} [A-Z]{2}\d+)\) (\d+)$')

#
# trkSub matches any 7 characters starting with a letter except anything
# matching a minorplanetPackedProvIDRegex or a minorplanetSurveyRegex
#
# note minor planet centuries are restricted to [I-K] (1800 - 2099; maybe allow 2199?)
# Also we must exclude PLS and T[1-3]S for the surveys
#
# Use the extra outside parentheses to add comments to the continuation
#
# This is a mess because it's hard to exclude things in regex
#
trksubRegexHelp = ( '([A-Za-z][A-Za-z0-9]{0,5}' +         # anything six characters
                    '|[A-HL-OQ-SU-Z][A-Za-z0-9]{0,6}' +   # anything seven not starting with I-K,P or T
                    '|[I-K][A-Za-z0-9]{5}[a-z1-9]' +      # anything starting with I-K not ending in A-Z or 0
                    '|[I-K][A-Za-z][A-Za-z0-9]{4}[0A-Z]' + # anything starting with I-K ending in [A-Z] with not digit as second character
                    '|[I-K][0-9][A-Za-z][A-Za-z0-9]{3}[0A-Z]' + # anything starting with [I-K]<digit> ending in [A-Z] with not digit as third character
                    '|[I-K][0-9][0-9][Ia-z0-9][A-Za-z0-9]{2}[0A-Z]' + # anything starting with [I-K]<digit> ending in [A-Z] with not [A-Z] as fourth character
                    '|[I-K][0-9][0-9][A-HJ-Z][A-Za-z0-9][A-Za-z][0A-Z]' + # anything with [I-K]\d\d[A-HJ-Z][A-Za-z0-9]<not digit> [A-Z]
                    '|P[A-KM-Za-z0-9][A-Za-z0-9]{5}' +   # anything seven starting with P<not L>
                    '|T[A-Za-z04-9][A-Za-z0-9]{5}' +   # anything seven starting with T<not 1-3>
                     '|(?:PL|T1|T2|T3)[A-RT-Za-z0-9][A-Za-z0-9]{4}' + # anything starting PL|T1|T2|T3 not followed by S 
                     '|(?:PL|T1|T2|T3)S[A-Za-z][A-Za-z0-9]{3}' + # anything starting PL|T1|T2|T3 followed by S with not digit in 4
                     '|(?:PL|T1|T2|T3)S[A-Za-z0-9][A-Za-z][A-Za-z0-9]{2}' + # anything starting PL|T1|T2|T3 followed by S with not digit in 5
                     '|(?:PL|T1|T2|T3)S[A-Za-z0-9]{2}[A-Za-z][A-Za-z0-9]' + # anything starting PL|T1|T2|T3 followed by S with not digit in 6
                     '|(?:PL|T1|T2|T3)S[A-Za-z0-9]{3}[A-Za-z]' + # anything starting PL|T1|T2|T3 followed by S with not digit in 7
                    ')' )
#trksubRegex = re.compile('^([A-Za-z][A-Za-z0-9]{0,7})$')
trksubRegex = re.compile('^' + trksubRegexHelp + '$')


#
# Minor Planet groups: 
#   PermID:  None if not present
#      1: <letnum>
#      2: 4 digits
#   Normal ProvID: None if not present
#      3: <letnum> 
#      4: <yy> 
#      5: <halfmonth> 
#      6: <letnum> 
#      7: digit 
#      8: order -- is None if matches 0 for comet id
#   Survey ProvID: None if not present
#      9: PL | T1 | t3 | T3  
#      10: 4 digits
#   trkSub:  None if not present
#      11: six characters starting with a letter
#
minorplanetPackedIDRegex = re.compile('^(?: {5}|([0-9A-Za-z])(\d{4})|(~[0-9A-Za-z]{4}))'+ 
                                      '(?:' + '([I-K])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)(?:([A-HJ-Z])|0)' + '|'
                                            + '(PL|T1|T2|T3)S(\d{4})' + '|'
                                            + trksubRegexHelp + ' *|'
                                            + ' *'
                                       + ')$')

#
# Comet groups:
#
#  PermID:  
#    1: 4 digits  -- None if no PermID
#    2: PCDX  -- used by provID too.  Only PD for PermID.  Is A allowed????
#  ProvID:  None if not present
#    3: <letnum>
#    4: <yy>
#    5: <halfmonth>
#    6: <letnum>
#    7: <digit>
#    8: A-Z; comet coded as asteroid
#    9: a-z; comet fragment 
# fragment marker for permID only (blanks in cols 6-10)
#   10: a-z; comet fragment first letter or blank
#   11: a-z; comet fragment 
#
# Add "I" for interstellar objects
#
cometPackedIDRegex = re.compile('^(?: {4}|(\d{4}))([APCDXI])'
                                  + '(?:' + '([0-9A-Za-z])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)(?:0|([A-Z])|([a-z]))' + '|'
                                          + '     ([a-z ])([a-z])'  + '|'
                                          + ' *$'
                                  + ')$')

#
# Satellite groups:
#
#  PermID:  None if not present
#    1: [JSUN]
#    2: 3 digits
#  ProvID:  None if not present
#    3: <letnum>
#    4: <yy>
#    5: JSUN
#    6: <letnum>
#    7: <digit>
#
satellitePackedIDRegex = re.compile('^(?: {4}|([JSUN])(\d{3}))S'  
                                       + '(?:' + '([0-9A-Za-z])(\d{2})([JSUN])([a-zA-Z0-9])(\d)0$' + '|'
                                               + ' *$'
                                       + ')$')

#
# A dictionary for unpacking planet names
#
planetNameDict = {
     'J': 'Jupiter',
     'S': 'Saturn',
     'U': 'Uranus',
     'N': 'Neptune',
}

#
# A dictionary for unpacking letters as numbers
#
packLetters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
unpackLetters = {}

def _initpackLetters():
   global packLetters, unpackLetters
   for i in range(len(packLetters)):
     unpackLetters[packLetters[i]] = i

_initpackLetters()

def radix62_4(mp): # pack a number in 4 digits of radix62 with leading ~
   packed = ''
   for i in range(1,5):
     digit = mp % 62
     mp = mp//62
     packed = packLetters[digit] + packed
   return '~' + packed

def unRadix62_4(s): # unpack a number in radix62 with leading ~ assumed
   n = (((unpackLetters[s[1]]*62 +
          unpackLetters[s[2]])*62 +
          unpackLetters[s[3]])*62 +
          unpackLetters[s[4]])
   return n

        

def unpackPackedID(packedID):
   """ unpackePackedID unpacks an MPC 80-column ID
       Input:
          packedID: The 12-character packed ID
       Output:
          (permID, provID, trkSub)
   """
   permID = None
   provID = None
   trkSub = None
   #
   # groups:
   #   permID: None if not present
   #        may be all spaces, which is None
   #        five digits  ( to 99999 )
   #        a letter and four digits  (to Z9999  or 619999)
   #        a tilde and four [0-9A-Za-z] in base 62
   #   provID: None if not present
   #   trkSub: None if not present
   #
   m = minorplanetPackedIDRegex.match(packedID)
   if m: 
      if m.group(1) or m.group(3):  # check for permID presence
         if m.group(1):
           n = int(m.group(2)) + 10000*unpackLetters[m.group(1)]
         elif m.group(3):
           n = 620000 + (((unpackLetters[m.group(3)[1]]*62 +
                           unpackLetters[m.group(3)[2]])*62 +
                           unpackLetters[m.group(3)[3]])*62 +
                           unpackLetters[m.group(3)[4]])
         if (n == 0):
            raise RuntimeError("Can't unpack because minor planet number for " 
                                + packedID + " is zero")
         permID = str(n)
      
      if m.group(4): # check for normal provID presence
         y = unpackLetters[m.group(4)] * 100 + int(m.group(5))
         y = "{0:0d}".format(y)
         n = unpackLetters[m.group(7)] * 10 + int(m.group(8))
         if n==0:
            ns = ''
         else:
            ns = str(n)
         if m.group(9):  # normal asteroid provid
             provID =  y + ' ' + m.group(6) + m.group(9) + ns
         else:           # comet ID -- use A/
             provID =  'A/' + y + ' ' + m.group(6) + ns

      if m.group(10): # check for survey provID presence
         provID =  m.group(11) + ' ' + m.group(10)[0] + '-' + m.group(10)[1]

      if not permID and m.group(12): # check for trkSub -- can't be provID may not have permID
         trkSub = m.group(12).strip()

   #
   # Comet groups:
   #
   #  PermID:  
   #    1: 4 digits  -- None if no PermID
   #    2: PCDX  -- used by provID too.  Only PD for PermID.  Is A allowed????
   #  ProvID:  None if not present
   #    3: <letnum>
   #    4: <yy>
   #    5: <halfmonth>
   #    6: <letnum>
   #    7: <digit>
   #    8: A-Z; comet coded as asteroid
   #    9: a-z; comet fragment 
   # fragment marker for permID only (blanks in cols 6-10)
   #   10: a-z; comet fragment first letter or blank
   #   11: a-z; comet fragment 
   #
   m = cometPackedIDRegex.match(packedID)
   if m:
     cometType = m.group(2)
     if m.group(1):
        n = int(m.group(1))
        if (n == 0):
           raise RuntimeError("Can't unpack because comet number for " 
                               + packedID + " is zero")
        if (cometType != 'P' and cometType != 'D'):
           raise RuntimeError("Can't unpack because comet type for " 
                               + packedID + " must be P or D")
        permID = str(n) + cometType
        #
        # now check for fragments
        #
        if m.group(9):
          permID = permID + '-' + m.group(9).upper()
        if m.group(11):
          frag = (m.group(10) + m.group(11)).strip().upper()
          permID = permID + '-' + frag

     if m.group(3):
        y = unpackLetters[m.group(3)] * 100 + int(m.group(4))
        y = "{0:0d}".format(y)
        n = unpackLetters[m.group(6)] * 10 + int(m.group(7))
        if n==0:
           ns = ''
        else:
           ns = str(n)
        extra = ''
        if m.group(8): # m.group(8) changes nothing 
           extra = m.group(8) # adds order

        frag = ''
        if m.group(9): # fragment letter
           frag = '-' + m.group(9).upper()

        provID =  m.group(2) + '/' + y + ' ' + m.group(5) + extra + ns + frag

   #
   # Satellite groups:
   #
   #  PermID:  None if not present
   #    1: [JSUN]
   #    2: 3 digits
   #  ProvID:  None if not present
   #    3: <letnum>
   #    4: <yy>
   #    5: JSUN
   #    6: <letnum>
   #    7: <digit>
   #
   m = satellitePackedIDRegex.match(packedID)
   if m:
     if m.group(1):
        n = int(m.group(2))
        if (n == 0):
           raise RuntimeError("Can't unpack because satellite number for " 
                               + packedID + " is zero")
        permID =  planetNameDict[m.group(1)] + " " +  str(n)
     if m.group(3):
        y = unpackLetters[m.group(3)] * 100 + int(m.group(4))
        y = "{0:0d}".format(y)
        n = unpackLetters[m.group(6)] * 10 + int(m.group(7))
        if n==0:
           ns = ''
        else:
           ns = str(n)
        provID =  'S/' + y + ' ' + m.group(5) + ' ' + ns

   if not permID and not provID and not trkSub: # oops -- nothing here
      raise RuntimeError("Can't unpack " + repr(packedID) + " because this does not match a valid packed ID")

   return (permID, provID, trkSub)


def packTupleID(triplet):
   """ packTupleID packs an (permID, provID, trkSub) into
       MCP 80-column format or raises an exception about why not
       Input:
          (permID, provID, trkSub)  or  [permID, provID, trkSub]
       Output:
          packedID: The 12-character packed ID
   """
   try:
      permID = triplet[0]
      provID = triplet[1]
      trkSub = triplet[2]
   except:
      raise RuntimeError("Can't pack " + repr(triplet) + " because it isn't (permID, provID, trkSub)")
   if len(triplet) != 3:
      raise RuntimeError("Can't pack " + repr(triplet) + "because it is not of length 3")

   #
   # figure out permID type and value using regex
   #
   packedPermID = None # may be None if permID is None
   if permID is not None: # otherwise try to decode it
      #
      # may be a minor planet
      #
      m = minorplanetPermIDRegex.match(permID)
      if m:
         #print (permID, m.groups())
         mp = int(m.group(1))
         if (mp > 0) and (mp < 15396336): # 1 through 15396335 allowed
             if (mp < 620000):
                firstDigit = mp//10000   
                lastDigits = mp - firstDigit * 10000
                packedPermID =  packLetters[firstDigit] + "{0:0d}".format(lastDigits + 10000)[1:]
             else:
                packedPermID = ''
                mp -= 620000 # 620000 is ~0000
                packedPermID = radix62_4(mp)
                #for i in range(1,5):
                #  digit = mp % 62
                #  mp = mp//62
                #  packedPermID = packLetters[digit] + packedPermID
                #packedPermID = '~' + packedPermID
             permIDType = 'A'
         else:
             raise RuntimeError("Can't pack permID " + permID + " because it is not in range 1-15396335")

      #
      # may be a comet
      #
      m = cometPermIDRegex.match(permID)
      if m:
         n = int(m.group(1))
         if n > 9999:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is too large")
         if n == 0:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is zero")
         packedPermID =  "{0:0d}".format(n + 10000)[1:] + m.group(2)
         permIDType = 'C'

      #
      # may be a comet fragmnet
      #
      m = cometfragmentPermIDRegex.match(permID)
      if m:
         n = int(m.group(1))
         if n > 9999:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is too large")
         if n == 0:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is zero")
         packedPermID =  "{0:0d}".format(n + 10000)[1:] + m.group(2)
         permIDType = 'F'
         permIDFragment = m.group(3)
   
   
      #
      # may be a satellite
      #
      m = satellitePermIDRegex.match(permID)
      if m:
         n = int(m.group(2))
         if n > 999:
            raise RuntimeError("Can't pack because satellite number for " 
                                + permID + " is too large")
         if n == 0:
            raise RuntimeError("Can't pack because satellite number for " 
                                + permID + " is zero")
         permIDType = 'S'
         packedPermID = m.group(1)[0]  + "{0:0d}".format(1000 + int(m.group(2)))[1:] + 'S'

      #
      # may not be a satellite of an asteroid
      #
      m = asteroidsatellitePermIDRegex.match(permID)
      if m:
         raise RuntimeError("Can't pack satellites of asteroids: " +  permID)

      if not packedPermID:  # none falls through
          raise RuntimeError("invalid permID " + permID)

   #
   # figure out provID type and value using regex
   #
   packedProvID = None # may be None if provID is None
   if provID is not None:  # otherswise try to decode it
   #
   # minor planets in normal format
   #
      m = minorplanetProvIDRegex.match(provID)
      if m:
         y = int(m.group(1))  # two-digit head of year
         if (y<18) or (y>61):
            raise RuntimeError("Can't pack because minor planet year for " 
                                + provID + " is invalid")
         n = m.group(5)
         if not n: # None is 0
           n = 0  
         else:
           n = int(n)
         if n>619: # can't encode if it's too big
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         n1 = int(n/10)
         nn = packLetters[n1]
         n2 = "{0:0d}".format(n - 10*n1  + 10)[1:]
         
         packedProvID =  ' ' + packLetters[y] + m.group(2) + \
                m.group(3) + nn + n2 + m.group(4)
         provIDType = 'A'
   
      #
      # minor planets from survey
      #
      m = minorplanetSurveyProvIDRegex.match(provID)
      if m:
         n = int(m.group(1))
         s1 = m.group(2)[0]
         s2 = m.group(2)[2]
         packedProvID =  ' ' + s1 + s2 + 'S' + "{0:0d}".format(10000 + n)[1:]
         provIDType = 'A'
   
      #
      # comets
      #
      m = cometProvIDRegex.match(provID)
      if m:
         extra = '0' 
         if m.group(4):  # handle two-letter comets -- these were originally asteroids and can't have fragments
           extra = m.group(4)
         n = int('0' + m.group(5)) # may be ''
         n1 = n//10
         n2 = n - n1*10
         if n1 > 61:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         
         y1 = packLetters[int(m.group(2)[0:2])]
         y2 = m.group(2)[2:4]
         packedProvID =  m.group(1) + y1 + y2 + m.group(3) + packLetters[n1] + packLetters[n2] + extra
         if m.group(1) == 'A': # asteroid in disguise
            provIDType = 'A'
         else:
            provIDType = 'C'
   
      #
      # comet fragments
      #
      m = cometfragmentProvIDRegex.match(provID)
      if m:
         n = int(m.group(4))
         n1 = n//10
         n2 = n - n1*10
         if n1 > 61:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         
         y1 = packLetters[int(m.group(2)[0:2])]
         y2 = m.group(2)[2:4]
         packedProvID =  m.group(1) + y1 + y2 + m.group(3) + packLetters[n1] + packLetters[n2] + m.group(5).lower()
         provIDType = 'F'
         provIDFragment = m.group(5) # single character only
         
      #
      # satellites
      #
      m = satelliteProvIDRegex.match(provID)
      if m:
         n = int(m.group(3))
         n1 = n//10
         n2 = n - n1*10
         if n1 > 61:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         if n == 0:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is zero")
         
         
         y1 = packLetters[int(m.group(1)[0:2])]
         y2 = m.group(1)[2:4]
         packedProvID =  'S' + y1 + y2 + m.group(2) + packLetters[n1] + packLetters[n2]  + '0'
         provIDType = 'S'

      if not packedProvID:  # none falls through
          raise RuntimeError("invalid provID " + provID)


   packedTrkSub = None # may be None if trksub is None
   #
   # figure out trkSub type and value using regex
   # if packedPermID is None don't try this since
   # trkSub will not be used in the packing and may be an 
   # invalid value
   #
   if trkSub is not None and packedPermID is None: # otherwise try to decode it
      #
      # check trksub regex
      #
      m = trksubRegex.match(trkSub)
      if m:
         tmp = m.group(1)
         #print ("m.groups is ", m.groups())
         if len(tmp) > 7:
            raise RuntimeError("Can't pack " + trkSub + " because it it is too long")
         packedTrkSub = m.group(1)

      if not packedTrkSub:  # none falls through
          if packedProvID:  # sometimes trkSub is packedProvID minus a space
              pass          # if both are present trkSub will most likely be illegal
          else:
              raise RuntimeError("invalid trkSub " + trkSub)

   #
   # Now pack it in the final format
   #
   packed = None
   #print ( packedPermID, packedProvID, packedTrkSub )
   if packedPermID:  
      if packedProvID: # must match
        if permIDType != provIDType:
           raise RuntimeError("Can't pack " + repr(triplet) + " because provID and permID types don't match")
        if permIDType == 'F':
           if permIDFragment != provIDFragment:
              raise RuntimeError("Can't pack " + repr(triplet) + " because provID and permID fragments don't match")
        packed = packedPermID + packedProvID[1:]  # works for all cases that match

      else: # no packed provID
        if packedTrkSub:  # is this legal?
           pass
        else:
           packed = packedPermID + '       '
           if permIDType == 'F':  # fragments are special
             if len(permIDFragment) == 1:
                permIDFragment = ' ' + permIDFragment
             packed = packed[:10] + permIDFragment.lower()

   else:  # no packedPermID
      if packedProvID:
        #if packedTrkSub: # this is illegal in mpc80 but ignore it if in xml
        #  raise RuntimeError("Can't pack " + repr(triplet) + " because it has both provID and trksub")
        packed = '    ' + packedProvID # captures column 5

      else:
        if packedTrkSub: 
           packed = '     ' + packedTrkSub  # need to pad to column 12
           packed = '{0:12s}'.format(packed)

   if packed:
      return packed

   raise RuntimeError("Can't pack " + repr(triplet) )


def testConverter(string, expected, converter, stream=sys.stdout):
   """ test the converter, such as packedID -> (permID, provID, trkSub) translation 
       Inputs:
         string: string to be converted
         expected: expected conversion,  or None if invalid
         converter: converter, such as packedTupleID
         stream: streaom on which to print result
       Errors: None

       This routine prints the result on stream
   """
   if expected is None:  # expect error
      try:
         val = converter(string)
         print (val, file=stream)
         raise RuntimeError("BAD")
      except RuntimeError as e:
            if str(e) == "BAD":
               print ("  BAD: EXPECTED ERROR AND GOT NONE FOR", string, file=stream)
            else:
               print ("  OK: ", e, file=stream)
   else:      # expect OK
      try:
         val = converter(string)
         if val != expected:
            print ("  BAD:  expected " + repr(expected) + " and got " + repr(val) + " for " + repr(string), file=stream)
         else:
            print ("  OK: ", string, " -> ", val, file=stream)
      except RuntimeError as e:
            print ("  BAD: ", e, file=stream)

def testPackedRoundTrip(s):  # test for round-trip
    """ testPackedRoundTrip checks to see whether packed ID s round-trips
        Input:
          s:  a packed ID
        Output:
          True
        Errors:
          RuntimeError if s does not round-trip
    """
        
    try:
      t = unpackPackedID(s)
    except:
      t = None
    try:
      u = packTupleID(t)
    except:
      u = None
    if s != u:
      raise RuntimeError("Bad RoundTrip: " + repr(s) + " vs. " + repr(u) + " through " + repr(t))
    return True

def testCases(stream=sys.stdout):
   """ testCases is a collection of test cases """
   #
   # demonstrate conversions
   #
   print (file=stream)
   print ("test to demonstrate A-Za-z number conversion", file=stream)
   for i in range(len(packLetters)):
      print(i, packLetters[i], unpackLetters[packLetters[i]], file=stream)

   #
   # test broken test report
   #
   print (file=stream)
   print ("test error handler for good cases marked as bad", file=stream)
   testConverter('00001       ', None, unpackPackedID, stream) # test error handler
   

   #
   # test full packed ID
   #
   print (file=stream)
   print ("test packed ID -> unnpacked", file=stream)
   testConverter("     K14A00A", (None, '2014 AA', None), unpackPackedID, stream)
   testConverter("00001       ", ('1', None, None), unpackPackedID, stream)
   testConverter("12345       ", ('12345', None, None), unpackPackedID, stream)
   testConverter("z9999       ", ('619999', None, None), unpackPackedID, stream)
   testConverter("B0001       ", ('110001', None, None), unpackPackedID, stream)
   testConverter("C1234K14A00A", ('121234', '2014 AA', None), unpackPackedID, stream)
   testConverter("00001K14A00A", ('1', '2014 AA', None), unpackPackedID, stream)
   testConverter("     K14A00A", (None, '2014 AA', None), unpackPackedID, stream)
   testConverter("     K14B01A", (None, '2014 BA1', None), unpackPackedID, stream)
   testConverter("     K14Aa0A", (None, '2014 AA360', None), unpackPackedID, stream)
   testConverter("     K14Az9Q", (None, '2014 AQ619', None), unpackPackedID, stream)
   testConverter("     J97B06A", (None, '1997 BA6', None), unpackPackedID, stream)

   testConverter('     PLS4007', (None, '4007 P-L', None), unpackPackedID, stream)
   testConverter('     T1S4568', (None, '4568 T-1', None), unpackPackedID, stream)
   testConverter('     T2S1238', (None, '1238 T-2', None), unpackPackedID, stream)
   testConverter('     T3S1438', (None, '1438 T-3', None), unpackPackedID, stream)
   testConverter('01234PLS4007', ('1234', '4007 P-L', None), unpackPackedID, stream)
   testConverter('01234T1S4568', ('1234', '4568 T-1', None), unpackPackedID, stream)
   testConverter('01234T2S1238', ('1234', '1238 T-2', None), unpackPackedID, stream)
   testConverter('01234T3S1438', ('1234', '1438 T-3', None), unpackPackedID, stream)

   testConverter("a0001K14A00A", ('360001', '2014 AA', None), unpackPackedID, stream)
   testConverter("07968J96N020", ('7968', 'A/1996 N2', None), unpackPackedID, stream)
   testConverter("     T1S4007", (None, '4007 T-1', None), unpackPackedID, stream)
   testConverter("     I98V00F", (None, '1898 VF', None), unpackPackedID, stream)
   testConverter("     A      ", (None, None, 'A'), unpackPackedID, stream)
   testConverter("     A000   ", (None, None, 'A000'), unpackPackedID, stream)
   testConverter("     A00001 ", (None, None, 'A00001'), unpackPackedID, stream)
   testConverter("     P00001 ", (None, None, 'P00001'), unpackPackedID, stream)
   testConverter("     PL0001 ", (None, None, 'PL0001'), unpackPackedID, stream)
   testConverter("     T10001 ", (None, None, 'T10001'), unpackPackedID, stream)
   testConverter("     A00001X", (None, None, 'A00001X'), unpackPackedID, stream)
   testConverter("     KA0001X", (None, None, 'KA0001X'), unpackPackedID, stream)
   testConverter("     K0A001X", (None, None, 'K0A001X'), unpackPackedID, stream)
   testConverter("     K00001X", (None, None, 'K00001X'), unpackPackedID, stream)
   testConverter("     K0a00", (None, None, 'K0a00'), unpackPackedID, stream)
   testConverter("     K0a00xx", (None, None, 'K0a00xx'), unpackPackedID, stream)
   testConverter("     K00a01X", (None, None, 'K00a01X'), unpackPackedID, stream)
   testConverter("     K00H01X", (None, '2000 HX1', None), unpackPackedID, stream)
   testConverter("     K00001X", (None, None, 'K00001X'), unpackPackedID, stream)
   testConverter("     K00I01X", (None, None, 'K00I01X'), unpackPackedID, stream)
   testConverter("     K00A0AX", (None, None, 'K00A0AX'), unpackPackedID, stream)
   testConverter("     K00001x", (None, None, 'K00001x'), unpackPackedID, stream)
   testConverter("     J000013", (None, None, 'J000013'), unpackPackedID, stream)
   testConverter("     P00001A", (None, None, 'P00001A'), unpackPackedID, stream)
   testConverter("     P00001z", (None, None, 'P00001z'), unpackPackedID, stream)
   testConverter("     P000010", (None, None, 'P000010'), unpackPackedID, stream)
   testConverter("     T000010", (None, None, 'T000010'), unpackPackedID, stream)
   testConverter("     PL0001X", (None, None, 'PL0001X'), unpackPackedID, stream)
   testConverter("     T30001Q", (None, None, 'T30001Q'), unpackPackedID, stream)
   testConverter("     T200010", (None, None, 'T200010'), unpackPackedID, stream)
   testConverter("     PLSa210", (None, None, 'PLSa210'), unpackPackedID, stream)
   testConverter("     PLS2a10", (None, None, 'PLS2a10'), unpackPackedID, stream)
   testConverter("     PLS20x0", (None, None, 'PLS20x0'), unpackPackedID, stream)
   testConverter("     PLS001X", (None, None, 'PLS001X'), unpackPackedID, stream)
   testConverter("     T3S001Q", (None, None, 'T3S001Q'), unpackPackedID, stream)

   testConverter("0073P       ", ('73P', None, None), unpackPackedID, stream)
   testConverter("1234P       ", ('1234P', None, None), unpackPackedID, stream)
   testConverter("0003D       ", ('3D', None, None), unpackPackedID, stream)
   testConverter( '    CJ95A010', (None, 'C/1995 A1', None), unpackPackedID, stream)
   testConverter( '    PJ94P01b', (None, 'P/1994 P1-B', None), unpackPackedID, stream)
   testConverter( '    CJ94P010', (None, 'C/1994 P1', None), unpackPackedID, stream)
   testConverter( '    CK48X130', (None, 'C/2048 X13', None), unpackPackedID, stream)
   testConverter( '    CK33L89c', (None, 'C/2033 L89-C', None), unpackPackedID, stream)
   testConverter( '    CK88AA30', (None, 'C/2088 A103', None), unpackPackedID, stream)
   testConverter( '    CJ99K070', (None, 'C/1999 K7', None), unpackPackedID, stream)
   testConverter( '    DJ99K070', (None, 'D/1999 K7', None), unpackPackedID, stream)
   testConverter( '    PI86S010', (None, 'P/1886 S1', None), unpackPackedID, stream)
   testConverter( '    DJ94P01b', (None, 'D/1994 P1-B', None), unpackPackedID, stream)
   testConverter( '    PJ94P01b', (None, 'P/1994 P1-B', None), unpackPackedID, stream)
   testConverter( '    PJ96J01a', (None, 'P/1996 J1-A', None), unpackPackedID, stream)
   testConverter( '    PJ98Q54P', (None, 'P/1998 QP54', None), unpackPackedID, stream)
   testConverter( '    CJ97B06A', (None, 'C/1997 BA6', None), unpackPackedID, stream)
   testConverter( '    PJ98Q00P', (None, 'P/1998 QP', None), unpackPackedID, stream)
   testConverter( '    PK01ND10', (None, 'P/2001 N131', None), unpackPackedID, stream)
   testConverter( '    PK10V10b', (None, 'P/2010 V10-B', None), unpackPackedID, stream)
   testConverter( '    DI94F010', (None, 'D/1894 F1', None), unpackPackedID, stream)
   testConverter( '    DJ93F02e', (None, 'D/1993 F2-E', None), unpackPackedID, stream)
   testConverter( '    XJ87A020', (None, 'X/1987 A2', None), unpackPackedID, stream)
   testConverter( '    AJ87A020', (None, 'A/1987 A2', None), unpackPackedID, stream)
   testConverter( '0141PJ94P01a', ('141P-A', 'P/1994 P1-A', None), unpackPackedID, stream)
   testConverter( '0001PI35P010', ('1P', 'P/1835 P1', None), unpackPackedID, stream)
   testConverter( '0073P     af', ('73P-AF', None, None), unpackPackedID, stream)
   testConverter( '0073P      g', ('73P-G', None, None), unpackPackedID, stream)

   testConverter("J001S       ", ('Jupiter 1', None, None), unpackPackedID, stream)
   testConverter("S005S       ", ('Saturn 5', None, None), unpackPackedID, stream)
   testConverter("N013S       ", ('Neptune 13', None, None), unpackPackedID, stream)
   testConverter("U101S       ", ('Uranus 101', None, None), unpackPackedID, stream)
   testConverter("J001SG10J010", ('Jupiter 1', 'S/1610 J 1', None), unpackPackedID, stream)

   testConverter("    SG10J010", (None, 'S/1610 J 1', None), unpackPackedID, stream)
   testConverter("    SK10JB10", (None, 'S/2010 J 111', None), unpackPackedID, stream)
   testConverter('    SK01U090', (None, 'S/2001 U 9', None), unpackPackedID, stream)
   testConverter('    SK01S310', (None, 'S/2001 S 31', None), unpackPackedID, stream)
   testConverter('    SK01JD10', (None, 'S/2001 J 131', None), unpackPackedID, stream)
   testConverter('    SK01ND10', (None, 'S/2001 N 131', None), unpackPackedID, stream)

   testConverter("    SAab102 ", None, unpackPackedID, stream)
   testConverter("0a001K14A00A", None, unpackPackedID, stream)

   testConverter( '    Pbb12   ', None, unpackPackedID, stream)
   testConverter("0a001K14A00A", None, unpackPackedID, stream)
   testConverter("1234C       ", None, unpackPackedID, stream)
   testConverter("1234X       ", None, unpackPackedID, stream)
   testConverter("1234A       ", None, unpackPackedID, stream)
   testConverter("00000       ", None, unpackPackedID, stream)
   testConverter("0000P       ", None, unpackPackedID, stream)
   testConverter("U000S       ", None, unpackPackedID, stream)
   testConverter("K221S       ", None, unpackPackedID, stream)
   testConverter("_0000       ", None, unpackPackedID, stream)
   testConverter("     A00 01 ", None, unpackPackedID, stream)  # bogus
   testConverter("            ", None, unpackPackedID, stream)

   #
   # test packing ID
   #
   print (file=stream)
   print ("test unpacked ID -> packed", file=stream)
   testConverter( (None, '2014 AA', None), "     K14A00A", packTupleID, stream)
   testConverter( ('1', None, None), "00001       ", packTupleID, stream)
   testConverter( ('121234', '2014 AA', None), "C1234K14A00A", packTupleID, stream)
   testConverter( ('1', '2014 AA', None), "00001K14A00A", packTupleID, stream)
   testConverter( ('360001', '2014 AA', None), "a0001K14A00A", packTupleID, stream)
   testConverter( ('7968', 'A/1996 N2', None), "07968J96N020", packTupleID, stream)

   testConverter( (None, '4007 T-1', None), "     T1S4007", packTupleID, stream)
   testConverter( (None, None, 'A'), "     A      ", packTupleID, stream)
   testConverter( (None, None, 'A000'), "     A000   ", packTupleID, stream)
   testConverter( (None, None, 'A00001'), "     A00001 ", packTupleID, stream)

   testConverter( ('73P', None, None), "0073P       ", packTupleID, stream)
   testConverter( ('3D', None, None), "0003D       ", packTupleID, stream)
   testConverter( (None, 'C/1995 A1', None), '    CJ95A010', packTupleID, stream)
   testConverter( (None, 'P/1994 P1-B', None), '    PJ94P01b', packTupleID, stream)
   testConverter( (None, 'C/1994 P1', None), '    CJ94P010', packTupleID, stream)
   testConverter( (None, 'C/2048 X13', None), '    CK48X130', packTupleID, stream)
   testConverter( (None, 'C/2033 L89-C', None), '    CK33L89c', packTupleID, stream)
   testConverter( (None, 'C/2088 A103', None), '    CK88AA30', packTupleID, stream)
   testConverter( (None, 'C/1999 K7', None), '    CJ99K070', packTupleID, stream)
   testConverter( (None, 'D/1999 K7', None), '    DJ99K070', packTupleID, stream)
   testConverter( (None, 'P/1886 S1', None), '    PI86S010', packTupleID, stream)
   testConverter( (None, 'D/1994 P1-B', None), '    DJ94P01b', packTupleID, stream)
   testConverter( (None, 'P/1994 P1-B', None), '    PJ94P01b', packTupleID, stream)
   testConverter( (None, 'P/1996 J1-A', None), '    PJ96J01a', packTupleID, stream)
   testConverter( (None, 'P/1998 QP54', None), '    PJ98Q54P', packTupleID, stream)
   testConverter( (None, 'P/2014 QP', None), '    PK14Q00P', packTupleID, stream)
   testConverter( (None, 'C/1997 BA6', None), '    CJ97B06A', packTupleID, stream)
   testConverter( (None, 'P/2001 N131', None), '    PK01ND10', packTupleID, stream)
   testConverter( (None, 'P/2010 V10-B', None), '    PK10V10b', packTupleID, stream)
   testConverter( (None, 'D/1894 F1', None), '    DI94F010', packTupleID, stream)
   testConverter( (None, 'D/1993 F2-E', None), '    DJ93F02e', packTupleID, stream)
   testConverter( (None, 'X/1987 A2', None), '    XJ87A020', packTupleID, stream)
   testConverter( ('141P-A', 'P/1994 P1-A', None), '0141PJ94P01a', packTupleID, stream)
   testConverter( ('1P', 'P/1835 P1', None), '0001PI35P010', packTupleID, stream)
   testConverter( ('73P-AF', None, None), '0073P     af', packTupleID, stream)
   testConverter( ('73P-G', None, None), '0073P      g', packTupleID, stream)
   testConverter( (None, None, 'bb12'), '     bb12   ',  packTupleID, stream)

   testConverter( ('Jupiter 1', None, None), "J001S       ", packTupleID, stream)
   testConverter( ('Saturn 1', None, None), "S001S       ", packTupleID, stream)
   testConverter( ('Neptune 13', None, None), "N013S       ", packTupleID, stream)
   testConverter( ('Uranus 101', None, None), "U101S       ", packTupleID, stream)
   testConverter( ('Jupiter 1', 'S/1610 J 1', None), "J001SG10J010", packTupleID, stream)

   testConverter( (None, 'S/1610 J 1', None), "    SG10J010", packTupleID, stream)
   testConverter( (None, 'S/2010 J 111', None), "    SK10JB10", packTupleID, stream)
   testConverter( (None, None, 'Aab102'), "     Aab102 ", packTupleID, stream)
   testConverter( (None, None, None), None, packTupleID, stream)

   testConverter( ('0', None, None), None, packTupleID, stream)
   testConverter( ('620000', None, None), None, packTupleID, stream)
   testConverter( "bogus", None, packTupleID, stream)
   testConverter( ('1', 'P/1994 P1-A', None), None, packTupleID, stream)
   testConverter( ('141P', 'P/1994 P1-A', None), None, packTupleID, stream)
   testConverter( ('141P-C', 'P/1994 P1-A', None), None, packTupleID, stream)
   testConverter( ('141P-AB', 'P/1994 P1-A', None), None, packTupleID, stream)
   testConverter( ('12345P', None, None), None, packTupleID, stream)
   testConverter( ('0P', None, None), None, packTupleID, stream)
   testConverter( ('(45) 1', None, None), None, packTupleID, stream)
   testConverter( (None, 'S/1610 J 1', 'Abcde'), None, packTupleID, stream)
   testConverter( (None, 'Invalid88', None), None, packTupleID, stream)
   testConverter( (None, None, 'A1234567'), None, packTupleID, stream)
   testConverter( (None, None, ''), None, packTupleID, stream)
   testConverter( (None, None, 'Ab3%xx'), None, packTupleID, stream)
   testConverter( (None, 'S/2010 J 111'), None, packTupleID, stream)
   testConverter( (None, 'S/2010 J 111', None, "Too long"), None, packTupleID, stream)

   testConverter( (None, '568 T-1', None), None, packTupleID, stream)
   testConverter( (None, '2014 AA620', None), None, packTupleID, stream)
   testConverter( (None, '2014 AA12345', None), None, packTupleID, stream)
   testConverter( (None, 'C/1997 B620', None), None, packTupleID, stream)
   testConverter( (None, 'P/1998 QP54-A', None), None, packTupleID, stream)
   testConverter( (None, '1700 AA', None), None, packTupleID, stream)
   testConverter( (None, '6200 AX', None), None, packTupleID, stream)
   testConverter( (None, '2001 IA', None), None, packTupleID, stream)
   testConverter( (None, '2001 ZA', None), None, packTupleID, stream)
   testConverter( (None, '2001 AI', None), None, packTupleID, stream)
   testConverter( (None, 'S/2001 N 620', None), None, packTupleID, stream)
   testConverter( (None, 'S/2001 N 0', None), None, packTupleID, stream)
   testConverter( (None, 'S/2008 (41) 1', None), None, packTupleID, stream)
   testConverter( (None, 'S/2001 (1998 WW31)) 1', None), None, packTupleID, stream)

   #
   # test packed ID round-trip
   #
   print (file=stream)
   print ("test packed ID roundTrip", file=stream)
   testConverter("     K14A00A", True, testPackedRoundTrip, stream)
   testConverter("00001       ", True, testPackedRoundTrip, stream)
   testConverter("C1234K14A00A", True, testPackedRoundTrip, stream)
   testConverter("00001K14A00A", True, testPackedRoundTrip, stream)
   testConverter("a0001K14A00A", True, testPackedRoundTrip, stream)
   testConverter("07968J96N020", True, testPackedRoundTrip, stream)
   testConverter("    AJ96N020", True, testPackedRoundTrip, stream)
   testConverter("     T1S4007", True, testPackedRoundTrip, stream)
   testConverter("     A      ", True, testPackedRoundTrip, stream)
   testConverter("     A000   ", True, testPackedRoundTrip, stream)
   testConverter("     A00001 ", True, testPackedRoundTrip, stream)
   testConverter("     A00001X", True, testPackedRoundTrip, stream)
   testConverter("     K00001X", True, testPackedRoundTrip, stream)
   testConverter("     K00001x", True, testPackedRoundTrip, stream)
   testConverter("     J000013", True, testPackedRoundTrip, stream)
   testConverter("     P00001A", True, testPackedRoundTrip, stream)
   testConverter("     P00001z", True, testPackedRoundTrip, stream)

   testConverter("0073P       ", True, testPackedRoundTrip, stream)
   testConverter("0003D       ", True, testPackedRoundTrip, stream)
   testConverter( '    CJ95A010', True, testPackedRoundTrip, stream)
   testConverter( '    PJ94P01b', True, testPackedRoundTrip, stream)
   testConverter( '    CJ94P010', True, testPackedRoundTrip, stream)
   testConverter( '    CK48X130', True, testPackedRoundTrip, stream)
   testConverter( '    CK33L89c', True, testPackedRoundTrip, stream)
   testConverter( '    CK88AA30', True, testPackedRoundTrip, stream)
   testConverter( '    CJ99K070', True, testPackedRoundTrip, stream)
   testConverter( '    DJ99K070', True, testPackedRoundTrip, stream)
   testConverter( '    PI86S010', True, testPackedRoundTrip, stream)
   testConverter( '    DJ94P01b', True, testPackedRoundTrip, stream)
   testConverter( '    PJ94P01b', True, testPackedRoundTrip, stream)
   testConverter( '    PJ96J01a', True, testPackedRoundTrip, stream)
   testConverter( '    PJ98Q54P', True, testPackedRoundTrip, stream)
   testConverter( '    CJ97B06A', True, testPackedRoundTrip, stream)
   testConverter( '    PK01ND10', True, testPackedRoundTrip, stream)
   testConverter( '    PK10V10b', True, testPackedRoundTrip, stream)
   testConverter( '    DI94F010', True, testPackedRoundTrip, stream)
   testConverter( '    DJ93F02e', True, testPackedRoundTrip, stream)
   testConverter( '    XJ87A020', True, testPackedRoundTrip, stream)
   testConverter( '0141PJ94P01a', True, testPackedRoundTrip, stream)
   testConverter( '0001PI35P010', True, testPackedRoundTrip, stream)
   testConverter( '0073P     af', True, testPackedRoundTrip, stream)
   testConverter( '0073P      g', True, testPackedRoundTrip, stream)
   testConverter( '     bb12   ', True, testPackedRoundTrip, stream)

   testConverter("J001S       ", True, testPackedRoundTrip, stream)
   testConverter("S001S       ", True, testPackedRoundTrip, stream)
   testConverter("N013S       ", True, testPackedRoundTrip, stream)
   testConverter("U101S       ", True, testPackedRoundTrip, stream)
   testConverter("J001SG10J010", True, testPackedRoundTrip, stream)

   testConverter("    SG10J010", True, testPackedRoundTrip, stream)
   testConverter("    SK10JB10", True, testPackedRoundTrip, stream)

#testCases(sys.stdout)

