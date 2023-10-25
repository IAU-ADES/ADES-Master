#!/usr/bin/env python3
#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#

#
# sexVals decodes and encodes sexagesimal values
#

import sys
import re
import io
import math

#import adesutility


def errorSexVal(msg, l):
   badLineMsg = 'Invalid Sexagesimal string ('
   #print (badLineMsg, msg)
   raise RuntimeError(badLineMsg + msg + ') in string \n' + l)


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
           errorSexVal('columns ' + repr(c1) + '-' + repr(c2) + 
                  ' must be "' + repr(value) + '" not "' + s + '"', line)
        else:
           errorSexVal('column ' + repr(c1) +  
                   ' must be "' + repr(value) + '" not "' + s + '"', line)
   else:
      if not s.isspace():
        if (c1 != c2):
           errorSexVal('columns ' + repr(c1) + '-' + repr(c2) + 
                  ' must be blank not "' + s + '"', line)
        else:
           errorSexVal('column ' + repr(c1) +  
                   ' must be blank not "' + s + '"', line)

#
# Sexagesimal Parsing
#
_checkNormal = re.compile('^(\d\d) (\d\d) (\d\d\.(\d*)) *$')
_checkIntegerSeconds = re.compile('^(\d\d) (\d\d) (\d\d) *$')
_checkMinutesHundredths = re.compile('^(\d\d) (\d\d\.\d\d) *$')
_checkMinutesTenths = re.compile('^(\d\d) (\d\d\.\d) *$')
_checkIntegerMinutes = re.compile('^(\d\d) (\d\d) *$')

_countNormal = 0
_countIntegerSeconds = 0
_countMinutesHundredths = 0
_countMinutesTenths = 0
_countIntegerMinutes = 0
def _actionNormal(m):
   """ action for HH MM SS.ss..."""
   global _countNormal
   hh = int(m.group(1))
   mm = int(m.group(2))
   ss = float(m.group(3))
   prec = 10.0 ** (-len(m.group(4)))
   _countNormal += 1
   return (hh, mm, ss, prec)

def _actionIntegerSeconds(m):
   """ action for HH MM SS"""
   global _countIntegerSeconds
   hh = int(m.group(1))
   mm = int(m.group(2))
   ss = int(m.group(3))
   prec = 1
   _countIntegerSeconds += 1
   return (hh, mm, ss, prec)

def _actionMinutesHundredths(m):
   """ action for HH MM.mm """
   global _countMinutesHundredths
   hh = int(m.group(1))
   mm = float(m.group(2))
   ss = 0
   prec = 0.6
   _countMinutesHundredths += 1
   return (hh, mm, ss, prec)

def _actionMinutesTenths(m):
   """ action for HH MM.m """
   global _countMinutesTenths
   hh = int(m.group(1))
   mm = float(m.group(2))
   ss = 0
   prec = 6
   _countMinutesTenths += 1
   return (hh, mm, ss, prec)

def _actionIntegerMinutes(m):
   """ action for HH MM """
   global _countIntegerMinutes
   hh = int(m.group(1))
   mm = int(m.group(2))
   ss = 0
   prec = 60
   _countIntegerMinutes += 1
   return (hh, mm, ss, prec)

_checks = [ (_checkNormal, _actionNormal),
            (_checkIntegerSeconds, _actionIntegerSeconds),
            (_checkMinutesHundredths, _actionMinutesHundredths),
            (_checkMinutesTenths, _actionMinutesTenths),
            (_checkIntegerMinutes, _actionIntegerMinutes),
          ]


def checkSexagesimal(line):
   """ checkSexagesimal parses a segidecmal value
          line is of the form DD MM SS.sss (or HH MM SS.sss)
          Return is (value, degrees, minutes, seconds, prec)
             degrees (or hours)
             minutes (may be 12.5 or 0)
             seconds (may be 12.5 or 0)
             prec:  sexagesimal precision:
                0.001:  HH MM SS.sss
                0.01:   HH MM SS.ss
                0.1:    HH MM SS.s
                1:      HH MM SS
                6:      HH MM.m
                60:     HH MM
                #360:    HH.h
                #3600:   HH
   """
   for (check, action) in _checks:
      m = check.match(line)
      if m:
        return action(m)
   errorSexVal('sexagesimal date must be "HH MM SS.ss" not ', line)

#checkSexagesimal("12") #bad -- no minutes
#checkSexagesimal("12 ") #bad -- no minutes
#checkSexagesimal("12.1 ") #bad -- no minutes
#checkSexagesimal("12.1 ") #bad -- no minutes
#checkSexagesimal("12 13.1 ")
#checkSexagesimal("12 13   ")
#checkSexagesimal("12 13. ") #bad -- trailing . not allowed
#checkSexagesimal("12 13.12 ") #bad - only tenths digid
#checkSexagesimal("12 13 14")
#checkSexagesimal("12 13 14.5")
#checkSexagesimal("12 13 14x5") # bad -- bad chararcter x
#checkSexagesimal("12 13 14.56")
#checkSexagesimal("12 13 14.56  ")
#checkSexagesimal("12 13 14.567")
#checkSexagesimal("12 13 14.56 x")  # bad -- end in spaces only
#checkSexagesimal(" 13 13 14.56  ") # bad -- must start in first column


      

_checkDate = re.compile('^((16|17|18|19|[2-9]\d)\d\d) (0[1-9]|10|11|12) ((0[1-9]|[12]\d|30|31)\.(\d+)) *$')
#testdate("1800 00 01.333  ")  # bad month
#testdate("1800 01 00.333  ")  # bad day
#testdate("1800 01 01    ")
#testdate("1800 01 01.   ")
#testdate("1800 01 01.3  ")
#testdate("1800 01 01.33  ")
#testdate("1800 01 01.333  ")
#testdate("1800 01 01.3333  ")
#testdate("1800 01 01.33333  ")
#testdate("1800 01 01.333333  ")
#testdate("1800 01 01.3333333 ")
#testdate("1800 01 01.3333333")
#testdate("1920 01 01.3333333")
#testdate("1920 09 01.3333333")
#testdate("1920 10 01.3333333")
#testdate("1920 1030 01.3333333") # bad month
#testdate("1920 102 01.3333333") # bad month
#testdate("1920 11 01.3333333")
#testdate("1920 12 01.3333333")
#testdate("1920 13 01.3333333") # bad month
#testdate("2001 01 01.3333333")
#testdate("2001 01 11.3333333")
#testdate("2001 01 21.3333333")
#testdate("2001 01 28.3333333")
#testdate("2001 01 31.3333333")
#testdate("2001 01 30.3333333")
#testdate("2901 01 01.3333333")
#testdate("2101 01 01.3333333")
#testdate("2101 02 01.3333333")
#testdate("2101 03 01.3333333")
#testdate("2101 03 31.3333333")
#testdate("2101 03 21.3333333")
#testdate("2101 03 32.3333333") #bad day


_countDate1 = 0
_countDate10 = 0
_countDate100 = 0
_countDate1000 = 0
_countDate10000 = 0
_countDate100000 = 0
_countDate1000000 = 0
_countDateBig = 0
_countDateSmall = 0
def twoDigit(t):
   ss = "{0:.0f}".format(t+100.0)[1:]
   return ss

def sexDateToISO(sexDate, intsec=False):
   """ translates date into iso date
       Inputs:
           sexDate:  sexDate string
       Return Value:
           A tuple
            (isoDate, prec, oldfracdd)
            isoDate:  isoDate
            prec:     precision for precTime Fields
            oldfracdd: fractional days from original format
       Errors:
            RuntimeError if not valid

       Global effects:
           updates _countDate variables
   """
   global _countDate1
   global _countDate10
   global _countDate100
   global _countDate1000
   global _countDate10000
   global _countDate100000
   global _countDate1000000
   global _countDateBig
   global _countDateSmall
   m = _checkDate.match(sexDate)
   if m:
     #print (m.groups())
     #print (m.group(1), m.group(3), m.group(4), "prec = ", prec)
     yyyy = int(m.group(1)) # Year
     dd = float(m.group(4)) # Decimal date, e.g., 15.12345
     prec = int( 10.0**(6 - len(m.group(6)))) # >1 for legal mpc
 
     # Count the number of differenent precision values
     if prec == 1: _countDate1 += 1       # This means 1e-6 day precision
     if prec == 10: _countDate10 += 1
     if prec == 100: _countDate100 += 1
     if prec == 1000: _countDate1000 += 1
     if prec == 10000: _countDate10000 += 1
     if prec == 100000: _countDate100000 += 1
     if prec == 1000000: _countDate1000000 += 1 # This means integer day precission
     if prec >  1000000: _countDateBig += 1 # Should not be possible
     if prec < 1: _countDateSmall += 1 # Should not be possible
 
     # Start to disect the decimal day  
     oldfracdd = m.group(4)[2:] # Drop the integer part
     fracdd = float(oldfracdd) * 86400.0 # GH trick to add a millisec?: + 0.001 # 0.001 avoids round-off to <secs>.999999
     hh_int = int(fracdd/3600.0);
     fracdd = fracdd - hh_int*3600.0  # Remaining seconds after stripping off hours
     mm_int = int(fracdd/60.0)
     fracdd = fracdd - mm_int*60.0  # Remaining seconds after stripping off hours and minutes
 
     # Deal with formatting seconds
     if intsec or prec >= 100:

        # Round to integer sec
        ss_int =  int(round(fracdd))
        if ss_int == 60: # Check for illegitimate 60s
           #print("A Fixing: ", ss_int, mm_int, hh_int)
           ss_int = 0
           mm_int += 1
           if mm_int == 60:
              mm_int = 0
              hh_int += 1
              if hh_int == 24:
                 errorSexVal('With integer seconds, fractional portion of date rounds to "24:00:00". ' + \
                                 ' This should not happen. ', sexDate)
                 
        # Get the string            
        ss = "{:02d}".format(ss_int)
       
     elif (prec == 1):

        # Round to two decimal places
        ss = "{:05.2f}".format(fracdd)
        if ss == "60.00":
           #print("B Fixing: " + ss, mm_int, hh_int)
           ss = "00.00"
           mm_int += 1
           if mm_int == 60:
              mm_int = 0
              hh_int += 1
              if hh_int == 24:
                 errorSexVal('With two decimal places, fractional portion of date rounds to "24:00:00.00". ' + \
                                 ' This should not happen. ', sexDate)
                   
     elif (prec == 10):

        # Round to one decimal place
        ss = "{:04.1f}".format(fracdd)
        if ss == "60.0": 
           #print("C Fixing: " + ss, mm_int, hh_int)
           ss = "00.0"
           mm_int += 1
           if mm_int == 60:
              mm_int = 0
              hh_int += 1
              if hh_int == 24:
                 errorSexVal('With one decimal place, fractional portion of date rounds to "24:00:00.0". ' + \
                                 ' This should not happen. ', sexDate)

     # Write the string
     mm = "{:02d}".format(mm_int)
     hh = "{:02d}".format(hh_int)
     isodate = m.group(1) + '-' + m.group(3)  + '-' + m.group(4)[0:2] + 'T' + hh + ':' + mm + ':' + ss + 'Z'

     if (ss[0:2] == "60") or (ss[0] == "-"):  # should raise error
        print ("Bad Date: " + ss + " for ss in date:",  sexDate)

     return (isodate, prec, oldfracdd)
   else:
     errorSexVal('date  must be "YYYY MM DD.d..." not ', sexDate)

def isoToSexDate(isodate, prec):
   """ Translates isodate to sexDate format
       Inputs:
          isodate:  a valid ISO date 
          prec:     precision value
       Return Value:
          sexdate
       Errors:  Only if prec is wierd
   """
   #print (isodate, prec)
   # -- do this later with regex which checks for Z, T and colons
   yyyy = isodate[0:4]
   month = isodate[5:7]
   day = isodate[8:10]
   hh = isodate[11:13]
   mm = isodate[14:16]
   ss = isodate[17:-1]
   xx = int(hh)*3600.0 + int(mm)*60.0 + float(ss)
   #print (yyyy, month, day, hh, mm, ss, xx, prec)
   if (prec <= 1): # < never copmes from legal input mpc
      yy = "{0:.6f}".format(xx/86400.0)[1:]
   if (prec == 10):
      yy = "{0:.5f}".format(xx/86400.0)[1:]
   if (prec == 100):
      yy = "{0:.4f}".format(xx/86400.0)[1:]
   if (prec == 1000):
      yy = "{0:.3f}".format(xx/86400.0)[1:]
   if (prec == 10000):
      yy = "{0:.2f}".format(xx/86400.0)[1:]
   if (prec >= 100000): # > never comes from legal input mpc
      yy = "{0:.1f}".format(xx/86400.0)[1:]
   #print (yy)
   sexdate = yyyy + ' ' + month + ' ' + day + yy
   #print (sexdate)
   return "{0:17s}".format(sexdate)  # get length right


def checkDate(rdict, radar=False):
   """ checks that rdict['date'] is valid and 
       rdict['obsTime'] and 
       rdict['precTime'] if it is"""
   date = rdict['date']
   (dateiso, prec, fracdd) = sexDateToISO(date, radar)
   rdict['obsTime'] = dateiso
   rdict['precTime'] = prec
   #
   # test by turning it back -- valid prec is 1 through 100000
   #
   sexdate = isoToSexDate(dateiso, prec)
   if sexdate != date:  # no round-trip
       errorSexVal( " Date invalid reverse: " + date, sexdate)


secToDegrees = 360.0/86400.0
arcsecToDegrees = 1.0/3600.0

def sexRaToDecRa( sexRa ):
   """ converts sexagesimal Ra to decimal degrees
       Inputs: 
         sexRa:  string sexagesimal RA value in hms
       Return Value: 
         A tuple:
          decRa: string decimal degrees RA 
          prec: precison value
   """
   (hours, minutes, seconds, prec) = checkSexagesimal(sexRa)
   digits = -int(math.floor(math.log10(prec*secToDegrees)))  
   if digits < 1:
     digits = 1
   fmt = '{0:.' + repr(digits) + 'f}'
   value = (hours*3600.0 + minutes*60.0 + seconds)*secToDegrees
   
   raDec = fmt.format(value)
   #print ("rdict['raSexagesimal'] = ", hours, minutes, seconds, prec, value, digits, rdict['ra'])
   return (raDec, prec)

def decRaToSexRa( decRa, prec ):
   """ converts decimal degress Ra to sexagesimal Ra
       Inputs: 
         decRa: string decimal degrees RA 
         prec: precison value
       Return Value: 
         sexRa:  string sexagesimal RA value in hms
   """
   rev = float(decRa)/secToDegrees

   revDeg = int(rev/3600.0);
   rev = rev - revDeg * 3600.0
   if prec == 0.6:
      revstr = '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.2f}'.format(100.0 + rev/60.0)[1:]
   elif prec == 6:
      revstr = '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.1f}'.format(100.0 + rev/60.0)[1:]
   elif prec == 60:
      revstr = '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.0f}'.format(100.0 + rev/60.0)[1:]
   else:
      revMin = int(rev/60.0)
      rev = rev - revMin * 60.0
      pdig = -int(math.log10(prec))
      fmt = '{0:.' + repr(pdig) + 'f}'
      #print (pdig, fmt)
      revstr = '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.0f}'.format(100+revMin)[1:] + ' ' + fmt.format(100.0 + rev)[1:]

   return "{0:12s}".format(revstr)  # get length right
   
def checkRa(rdict):
   """ checks that rdict['raSexagesimal'] is valid and adds 
       rdict['raDecimalDecgrees'] and 
       rdict['precRA'] if it is"""
   ra = rdict['raSexagesimal']
   (decRa, prec) = sexRaToDecRa(ra)
   rdict['precRA'] = prec
   rdict['ra'] = decRa

   revstr = decRaToSexRa(rdict['ra'], prec)
      
   if (revstr != ra):
      errorSexVal (" RA invalid reverse  = "+ revstr+ ' vs '+ ra + ' decimal '+ decRa, ra)

def sexDeclToDecDecl( sexDec ):
   """ converts sexagesimal delination to decimal degrees
       Inputs: 
         sexDec:  string sexagesimal Dec value in dms
       Return Value: 
         A tuple:
          decDecl: string decimal degrees Declination
          prec: precison value
   """
   # column 1 must be + or -
   sign = sexDec[0]
   valueError(sign, sexDec, 1, 1, ('+', '-')) # column 1 must be +/-
   if (sign == '-'):
      signval = -1.0
   else:
      signval = 1.0
   (degrees, minutes, seconds, prec) = checkSexagesimal(sexDec[1:])
   digits = -int(math.floor(math.log10(prec*arcsecToDegrees)))  
   if digits < 1:
     digits = 1
   fmt = '{0:.' + repr(digits) + 'f}'
   value = signval * (degrees + minutes/60.0 + seconds/3600.0)
   decDecl = fmt.format(value)
   #print ("rdict['decSexagesimal'] = ", rdict['decSexagesimal'], sign, degrees, minutes, seconds, prec, value, digits, decDecl)
   return (decDecl, prec)

def degDeclToSexDecl( sexDecl, prec ):
   """ converts decimal degress Ra to sexagesimal Declination
       Inputs: 
         decDecl: string decimal degrees Decl 
         prec: precison value
       Return Value: 
         sexDecl:  string sexagesimal Declination value in dms
   """
   rev = float(sexDecl)/arcsecToDegrees
   revSign = "+"
   if rev < 0:
      revSign = "-"
      rev = -rev
   elif sexDecl[0] == '-': # special case for -0.000
      revSign = "-"
   revDeg = int(rev/3600.0);
   rev = rev - revDeg * 3600.0
   if prec == 0.6:
      revstr = revSign + '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.2f}'.format(100.0 + rev/60.0)[1:]
   elif prec == 6:
      revstr = revSign + '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.1f}'.format(100.0 + rev/60.0)[1:]
   elif prec == 60:
      revstr = revSign + '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.0f}'.format(100.0 + rev/60.0)[1:]
   else:
      revMin = int((rev + 0.5*prec)/60.0)
      rev = rev - revMin * 60.0
      pdig = -int(math.log10(prec))
      fmt = '{0:.' + repr(pdig) + 'f}'
      #print (pdig, fmt)
      revstr = revSign + '{0:.0f}'.format(100+revDeg)[1:] + ' ' + '{0:.0f}'.format(100+revMin)[1:] + ' ' + fmt.format(100.0 + rev)[1:]
   return "{0:12s}".format(revstr)  # get length right

def checkDec(rdict):
   """ checks that rdict['decSexagesimal'] is valid and adds 
       rdict['dec'] and 
       rdict['precDec'] if it is"""
   decSexagesimal = rdict['decSexagesimal']

   (decDeg, prec) = sexDeclToDecDecl( decSexagesimal )
   rdict['precDec'] =  prec
   rdict['dec'] = decDeg
   
   revstr = degDeclToSexDecl( decDeg, prec )
      
   if (revstr != decSexagesimal):
      #print ("rdict['decSexagesimal'] = ", rdict['decSexagesimal'], rdict['dec'])
      #print (" invalid reverse  = ", revstr, 'vs', dec)
      errorSexVal (" Declination invalid reverse  = "+ revstr+ ' vs '+ decSexagesimal + ' decimal '+ decDeg, decSexagesimal)
   


def printCounts(stream = sys.stdout):

   print ("Normal:", _countNormal, file=stream)
   print ("Integer Seconds:", _countIntegerSeconds, file= stream)
   print ("Minutes Hundredths:", _countMinutesHundredths, file= stream)
   print ("Minutes Tenths:", _countMinutesTenths, file= stream)
   print ("Integer Minutes:", _countIntegerMinutes, file= stream)
   
   print ("date 1:", _countDate1, file= stream)
   print ("date 10:", _countDate10, file= stream)
   print ("date 100:", _countDate100, file= stream)
   print ("date 1000:", _countDate1000, file= stream)
   print ("date 10000:", _countDate10000, file= stream)
   print ("date 100000:", _countDate100000, file= stream)
   print ("date 1000000:", _countDate1000000, file= stream)
   print ("date big:", _countDateBig, file= stream)
   print ("date small:", _countDateSmall, file= stream)
