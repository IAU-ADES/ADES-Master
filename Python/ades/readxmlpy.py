#!/usr/bin/env python3
#
# readxml.py
#
# simple python script to demonstrate how to read xml
# files and walk though the elements and their children
# using the lxml library.  The only slightly tricky 
# thing is to remember to strip() the text to remove
# leading and trailing whitespace.
#
# as with all Python programs which might write
# UTF-8 to stdout, you must set the environment
# variable PYTHONIOENCODING to UTF-8 before
# launching.
#
# This script is designed to work with both
# python 2 and python 3
#
#
# This implementaiton uses lxml, which is not part of
# the default python installation and so must
# be installed separately. 
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

from lxml import etree as XMLTree
from lxml.etree import Element as XMLElement

import sys
import argparse

#
# printElement recursively prints an element and
# its children,   
#
#  element:  the element to print
#  depth:    incremented for each child call
#
def printElement(element, depth=0):
   #
   # print text and attrib for this element if 
   # they exist and are not empty
   #
   print ( depth*'  ', element.tag, end='')
   if element.text:
      if not element.text.isspace():  print (':', element.text, end='' )
   if element.attrib:  
      print (':', element.attrib, end='' )
   print ()

   # 
   # now recursively print the children.
   #
   # As and example, separate the 'optical' tags
   # and call processOptical on a list of all their children
   #
   if (element.tag == 'optical'):
      opticalElements = [ (i.tag, i.text) for i in element ]
      processOptical(opticalElements, depth+1)
   else:
      for i in element:  # recursively process the rest
         printElement(i, depth+1)
   

#
# A demonstration used to process only optical tags
#
def processOptical(opticalList, depth=0):

   print (depth*'  ', 'OPTICAL ELEMENT LIST FOUND')
   for tag, text in opticalList:
      print (depth*'  ', tag, '=', text)
   
             
def readxmlpy(xmlFile):
   #
   # read the xml file into python.  This grabs the whole thing
   #
   xmlTree = XMLTree.parse(xmlFile)

   #
   # now call the routine to print it recursively
   #
   printElement(xmlTree.getroot(), 0)
   
def main():
   parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   parser.add_argument("xmlfilename", type=str, help="XML file to read")

   args = parser.parse_args()

   readxmlpy(args.xmlfilename)

# ------------------------------------------------------
if __name__ == '__main__':
   main()
