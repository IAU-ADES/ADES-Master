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

from ades import adesutility

#
# sys.argv[1]: input mpc 80-column file
# sys.argv[2]: output xml file  (in utf-8)
# example: ./psvtoxml.py <psv file> <xml file>
#


_badLineMsg = 'Invalid MPC80COL line ('
decodeInitial80ColumnLine(line):
   """ decodeInitial80ColumnLine breaks an initial 80-col line in MPC
       format into its constituent parts and types.  The type may mean
       the next line is a continuation

       Input:  A line in 80-col format.  This is padded with spaces by 
               the caller

       Output:  A tuple:
           permid: Permanent ID or ''
           provid: Provisional ID, temporary ID, or ''
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

       Exceptions:  raises "Invalid MPC80COL line (<reason>): <line> " is the line 
                    is not valid for some reason
   """
   if len(line) != 80:
      raise _badLineMsg + 'not 80 columns) ' + line

   permid = line[0:5]    # 1-5
   provid = line[5:12]   # 6-12
   disc =   line[12]     # 13
   note =   line[13]     # 14
   code =   line[14]     # 15
   date =   line[15:32]  # 16-32
   ra   =   line[32:44]  # 33-44
   decl =   line[44:56]  # 45-56
   bl1  =   line[56:65]  # 57-65
   mag  =   line[65:70]  # 66-70
   band =   line[70]     # 71
   bl2  =   line[71:77]  # 72-77
   obs  =   line[77:79]  # 78-80

   if (bl1.isspace() != '         ') or (bl2 != '      '): # note: only space allowed, not tabs
      raise _badLineMsg + '57-65 and 72-77 must be blank)' + line

   if (disc != '*') or (disc != ' '):
      raise _badLineMsg + 'disc must be * or " " in column 13)' + line

   # Now figure out if permid is a comet, natural satellite, or minor planet
   # Notice that permid may be blank except for this designator, in which case
   # provid is affected by it.
  
   flag = permid[4]
   if flag == 'S':  # natural satellite
      if provid.isspace():
         #
         # unpack and decode provid
         #
         provid = provid
      if permid[0:4].isspace():
         #
         # decode permid
         #
         permid = permid
   elif (flag == 'C') or (flag == 'P') or (flag == 'D') \
     or (flag == 'X') or (flag == 'A'): # comet or minor planet given a comet designation
      if provid.isspace():
         #
         # unpack and decode provid
         #
         provid = provid
      if permid[0:4].isspace():
         #
         # decode permid
         #
         permid = permid
   else: # minor planet
      pass
   

   return (permid, provid, disc, note, code, date, ra, decl, mag, band obs)


with open(sys.argv[1]) as f:
   l = readline(f):
   print decodeInitial80ColumnLine(l)
