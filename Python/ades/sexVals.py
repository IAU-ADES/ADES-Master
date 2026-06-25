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
import math
from datetime import datetime, timedelta


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
# Sexagesimal Parsing (relaxed to allow leading spaces or single-digit fields)
#
_checkNormal = re.compile(r'^\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2}\.(\d*))\s*$')
_checkIntegerSeconds = re.compile(r'^\s*(\d{1,2})\s+(\d{1,2})\s+(\d{1,2})\s*$')
_checkMinutesHundredths = re.compile(r'^\s*(\d{1,2})\s+(\d{1,2}\.\d{2})\s*$')
_checkMinutesTenths = re.compile(r'^\s*(\d{1,2})\s+(\d{1,2}\.\d)\s*$')
_checkIntegerMinutes = re.compile(r'^\s*(\d{1,2})\s+(\d{1,2})\s*$')

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


      

_checkDate = re.compile(r'^(?P<year>(?P<century>16|17|18|19|[2-9]\d)\d\d) (?P<month>0[1-9]|10|11|12) (?P<days>(?P<day>0[1-9]|[12]\d|30|31)\.(?P<fractional_day>\d+)) *$')
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

def sexDateToISO(sexDate, intsec=False, microsec=False, mpc_rounding=True):
   """ Translates sexagesimal date into ISO formatted date, with rounding behavior controlled through argument inputs. 
   If all rounding behavior arguments are False, will round ISO format date using the precision of the provided sexagesimal date.
       Inputs:
           sexDate:  sexDate string
           intsec (bool, optional): round to integer seconds (Defaults to False)
           microsec (bool, optional): round to microseconds (Defaults to False)
           mpc_rounding (bool, optional): always report isoDate with millisecond precision (Defaults to True)
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
      d = m.groupdict()
      year = int(d['year'])
      month = int(d['month'])
      day = int(d['day'])
      oldfracdd = "." + d['fractional_day']
      seconds = float(oldfracdd) * 86400
      # Approximate (reciprocal) precision in millionths of a day, e.g., prec=100 means 1e-4 day
      prec = 10.0**(6 - len(d['fractional_day'])) # >1 for legal mpc
      if prec >= 1:
         prec = int(prec)

      # Count the number of different precision values
      if prec == 1: _countDate1 += 1       # This means 1e-6 day precision
      if prec == 10: _countDate10 += 1
      if prec == 100: _countDate100 += 1
      if prec == 1000: _countDate1000 += 1
      if prec == 10000: _countDate10000 += 1
      if prec == 100000: _countDate100000 += 1
      if prec == 1000000: _countDate1000000 += 1 # This means integer day precision
      if prec >  1000000: _countDateBig += 1 # Should not be possible
      if prec < 1: _countDateSmall += 1 # Should not be possible

      # If more than one of intsec, microsec, and  mpc_rounding are True then there is a conflict.
      # Prioritize intsec (radar), microsec (testing), mpc_rounding (default) 
      if intsec:
         # Round to integer seconds (probably for radar)
         digits = 0
      elif microsec:
         # Report microseconds (probably for testing)
         digits = 6
      elif mpc_rounding:
         #  MPC records will have precision 1e-6 day (= 86.4 ms) or less. Always convert MPC records to millisec precision.
         digits = 3
      else:
         # smart rounding for ISO format seconds according to the sexTime day precision
         # prec_day prec_sec microsecond digits
         # 1e-06    9e-08     8
         # 1e-05    9e-07     7
         # 0.0001   9e-06     6
         # 0.001    9e-05     5
         # 0.01     9e-04     4
         # 0.1      9e-03     3
         # 1        9e-02     2
         # 10       9e-01     1
         # 100      9e+00     0
         # 1000     9e+01    -1
         # 10000    9e+02    -2
         # 100000   9e+03    -3
         # 1000000  9e+04    -4
         # ISO format accepts at most 6 digits (microsecond)
         # and at minimum 0 digits (whole seconds)
         digits = int(min(max(0, 2 - math.log10(prec)), 6))

      if digits == 0:
        seconds = round(seconds)

      dt = datetime(year, month, day) + timedelta(seconds=seconds)
      isoDate = dt.strftime("%Y-%m-%dT%H:%M:%S")

      if digits != 0:
        fractional_seconds = round((seconds - int(seconds)) * 10**digits)
        isoDate += "." + str(fractional_seconds).rjust(digits, "0")

      isoDate += "Z"

      return isoDate, prec, oldfracdd

   else:

      errorSexVal('date must be "YYYY MM DD.d..." not ', sexDate)

def isoToSexDate(isodate, prec):
   """ Translates isodate to sexDate format
       Inputs:
          isodate:  a valid ISO date 
          prec:     precision value
       Return Value:
          sexdate
       Errors:  Only if prec is wierd
   """
   # This next line will only work reliably for python 3.11+ 
   # dt = datetime.fromisoformat(isodate)
   # And so we'll do it more carefully:
   try:
      # Try parsing with fractional seconds
      dt =  datetime.strptime(isodate, "%Y-%m-%dT%H:%M:%S.%fZ")
   except ValueError:
      # Fallback to parsing without fractional seconds
      dt = datetime.strptime(isodate, "%Y-%m-%dT%H:%M:%SZ")
   epoch = datetime(dt.year, dt.month, dt.day, tzinfo=dt.tzinfo)
   delta = (dt - epoch)
   # get fractional days
   fracdd = delta.seconds / 86400 + delta.microseconds / (86400) / 1e6
   # compute fractional days considering precision
   number_of_digits = 6 - int(math.log10(prec))
   if number_of_digits <= 0: # this corresponds to integer days or less precision
      # never comes from legal input mpc
      number_of_digits = 1
   fmt = "{" + f":.{number_of_digits}f" + "}"
   fracdd = fmt.format(fracdd) # round to the desired number of digits
   fracdd = fracdd.split(".")[1] # get digits after decimal place
   fracdd = fracdd.ljust(6, " ") # pad with whitespace
   fracdd = "." + fracdd

   sexDateFmt = "%Y %m %d"
   sexdate = dt.strftime(sexDateFmt) + fracdd
   return sexdate


def checkDate(rdict, radar=False):
   """ checks that rdict['date'] is valid and 
       rdict['obsTime'] and 
       rdict['precTime'] if it is"""
   date = rdict['date']
   (dateiso, prec, fracdd) = sexDateToISO(date, radar)
   if prec < 1:
      errorSexVal(f"time precision too high for ADES: precTime={prec}", date)
   #
   # test by turning it back -- valid prec is 1 through 100000
   #
   sexdate = isoToSexDate(dateiso, prec)
   if sexdate != date:  # no round-trip
       errorSexVal( " Date invalid reverse: " + date, sexdate)

   rdict['obsTime'] = dateiso
   rdict['precTime'] = prec


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

def _generic_decimal_to_sexagesimal(tot_seconds, prefix, prec, is_ra):
   """
   Return a sexagesimal representation of a number.

   Inputs: 
      tot_seconds: float, the value in its "seconds" unit; should already be bounds-checked
      prefix: string, a prefix to apply to the result
      prec: float, precision value (see below)
      is_ra: bool, True if we are handling an RA; otherwise, it is a declination

   Returns: 
      The sexagesimal string

   See docstrings for decRaToSexRa or degDeclToSexDecl for details. The
   *is_ra* parameter is needed to know how to handle values at the extremes 
   of the allowed domain, which in turn we need to know because of our
   rounding logic.
   """

   if prec == 60:
      minutes_mode = True
      places = 0
   elif prec == 6:
      minutes_mode = True
      places = 1
   elif prec == 0.6:
      minutes_mode = True
      places = 2
   else:
      minutes_mode = False
      places = -int(math.log10(prec))

   if places < 1:
      width = places + 2  # no decimal point
   else:
      width = places + 3  # yes decimal point

   # We need to round the rightmost fractional item *before* breaking down into
   # H/M/S to avoid `60.0` situations. But the "native" unit of this item
   # depends on whether we're in "minutes mode" or not. Either way, we also need
   # to check if rounding has brought us to the edge of the domain, and wrap or
   # clamp depending on whether we're RA or dec.

   if minutes_mode:
      tot_minutes = tot_seconds / 60
      tot_minutes = round(tot_minutes, places)
      
      if is_ra:
         if tot_minutes >= 1440.:
            tot_minutes -= 1440  # this could happen if we round from 23:59:59.9 to 24:00:00
      elif tot_minutes > 5400:  # +90 deg decl
         tot_minutes = 5400.
      elif tot_minutes < -5400:  # -90 deg decl
         tot_minutes = -5400.

      hours = int(tot_minutes // 60)
      minutes = tot_minutes - hours * 60
      result = "%s%02d %0*.*f" % (prefix, hours, width, places, minutes)
   else:
      tot_seconds = round(tot_seconds, places)

      if is_ra:
         if tot_seconds >= 86400.:
            tot_seconds -= 86400
      elif tot_seconds > 324000:  # +90 deg decl
         tot_seconds = 324000.
      elif tot_seconds < -324000:  # -90 deg decl
         tot_seconds = -324000.

      hours = int(tot_seconds // 3600)
      seconds = tot_seconds - hours * 3600
      minutes = int(seconds // 60)
      seconds = seconds - minutes * 60
      result = "%s%02d %02d %0*.*f" % (prefix, hours, minutes, width, places, seconds)

   return "{0:12s}".format(result)  # get length right

def decRaToSexRa(decRa, prec):
   """
   Converts decimal degrees RA to sexagesimal Ra

   Inputs: 
      decRa: decimal degrees RA; type is anything that can be converted to a float
      prec: float, precision value (see below)
   Return Value: 
      sexRa: string, sexagesimal RA value in hms

   The returned string will be at least twelve characters long, with padding
   spaces added at the end if needed. Different values of *prec* result
   in different outputs as follows:

   - 60   => `HH MM       `
   - 6    => `HH MM.M     `
   - 0.6  => `HH MM.MM    `
   - 1    => `HH MM SS    `
   - 0.1  => `HH MM SS.S  `
   - 0.01 => `HH MM SS.SS `
   - 1e-5 => `HH MM SS.SSSSS`, etc.
   """

   tot_seconds = float(decRa) / secToDegrees

   if tot_seconds < 0 or tot_seconds >= 86400.:
      raise RuntimeError("illegal decRaToSexRa input {0!r}: out of numerical bounds".format(decRa))
   
   return _generic_decimal_to_sexagesimal(tot_seconds, "", prec, True)

   
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

def degDeclToSexDecl(sexDecl, prec):
   """
   Converts decimal degrees declination to sexagesimal

   Inputs: 
      decDecl: **string** representation of a declination in decimal degrees
      prec: float, precision value (see below)
   Return Value: 
      sexDecl: string, sexagesimal declination value in dms

   The returned string will be at least twelve characters long, with padding
   spaces added at the end if needed. Different values of *prec* result
   in different outputs as follows:

   - 60   => `DD MM       `
   - 6    => `DD MM.M     `
   - 0.6  => `DD MM.MM    `
   - 1    => `DD MM SS    `
   - 0.1  => `DD MM SS.S  `
   - 0.01 => `DD MM SS.SS `
   - 1e-5 => `DD MM SS.SSSSS`, etc.
   """

   tot_seconds = float(sexDecl) / arcsecToDegrees
   prefix = "+"

   if tot_seconds < -324000 or tot_seconds > 324000:
      raise RuntimeError("illegal degDeclToSexDecl input {0!r}: out of numerical bounds".format(sexDecl))

   if tot_seconds < 0 or sexDecl[0] == '-': # special case for -0.000
      prefix = "-"
      tot_seconds = abs(tot_seconds)

   return _generic_decimal_to_sexagesimal(tot_seconds, prefix, prec, False)

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