#!/usr/bin/env python3
#
# testit.py is a test script for adesutility
#

#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

from ades import adesutility
from ades import xmlutility
import sys

#
# test with missing required elements
#

print ('Example of missing elements ')
try:
   ed = { 'permID': 1234, 'stn': '342', 'obsTime' : '2015-01-15T12:33:44.22Z'}
   elist = adesutility.makeElementList([ (item, str(ed[item])) for item in ed] )
   adesutility.makeADESElement('optical', elist)
except RuntimeError as e:
  print (e)
print (' ')

#
# test with a correct list
#
print ('Example of correct  elements ')
try:
   ed['dec'] =  90.0
   ed['ra'] =  0.0
   ed['astCat'] =  '12345'
   ed['remarks'] = "The king is still a fink!"
   ed['mode'] = "CCD"
   elist = adesutility.makeElementList([ (item, str(ed[item])) for item in ed] )
   correct = adesutility.makeADESElement('optical', elist)

   treeTop = adesutility.makeTree(correct)
   print (xmlutility.XMLTree.tostring(treeTop, pretty_print=True).decode())

except RuntimeError as e:
  print (e)
print (' ')

#
# test adding extra elements
#


print ('Example of extra  elements ')
try:
   ed['notgood'] =  90.0
   elist = adesutility.makeElementList([ (item, str(ed[item])) for item in ed] )
   adesutility.makeADESElement('optical', elist )
except RuntimeError as e:
  print (e)
print (' ')


for e in sorted(adesutility.allowedElementDict):
   print (e, ": ", adesutility.allowedElementDict[e])
for e in sorted(adesutility.requiredElementDict):
   print (e, ": ", adesutility.requiredElementDict[e])
print (adesutility.psvFormatDict)
