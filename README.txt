2017 Mar 29  GMH
  
   INSTALLATION:
      Untar this tarball.  Ensure you have a correctly installed
      python 2 or 3 and know its path.  You can have both.  You'll
      have to install the python lxml module for your python 
      separately; the best way to do that is to build from source.
      See google for instructions, which change regularly.

      To build the C programs, go to the C/ directory, configure
      to build Makefile.config, and then cd into src and type 'make'.
      The README file in C/ has more details.  If you're on a MAC OS X,
      you'll need to read it since the instructions are different.


   USAGE:  


   The following are the main executables available from Python.
   All of these work in python 2 and 3 although they pick 
   /usr/bin/env python
   if run as commands.   

   These require the Python lxml library, available both for Python 2 and 3

   adestest/Python/bin/

       psvtoxml <psvfile> <xmlfile>  # converts psv file to xml file
       xmltopsv <xmlfile> <psvfile>  # converts xml file to psv file

       
       # the mpc80col converters are incomplete.  They do not translate
       # header records or Satellite observations.
       mpc80coltoxml <mpc80colfile> <xml file>
       xmltompc80col <xmlfile> <mpc80colfile>  

       valall <xml file>     # validates against all possible formats
                             #    using both human-readable and non-   
                             #    human-readable xslt-generated xsd files
       valsubmit <xml file>  # validates against submit format
       valgeneral <xml file> # validates against general format

       applyxslt      # <xml file> <xslt file>  > <output file>
          # example to create the submit schema
          Python/bin/applyxslt xml/adesmaster.xml xslt/xsd/submitxsd.xslt > submit.xsd

       writexml       # example script to write xml file


   There is code in C for the all of the above except mpc80coltoxml and
   xmltompc80col, in adestest/C/src.  To build it, 
   run "./configure" "cd src; make".   
   If your are on a Mac, source the forMacOS... file first before running 
   configure.  

        mpc80coltoxml and xmltompc80col are not yet in C, but the above
        programs all work the same way.


   TEST CASES:

      The "adestest/tests" directory contains numerous correct and incorrect 
      test cases.  To run them, "cd tests" and run 


      .runtests prog_python2   # to test python 2
      .runtests prog_python3   # to test python 3, if python3 is in your path
      .runtests prog_c         # to test in C, if you built the C


      Also, the tests/mpc/ directory has some mpc 80-column examples.  The
      test cases for these are not yet finished

   DOCUMENTATION:

      adestest/doc/ contains pdf and ps files documenting ADES tables
      adestest/doc/src contains code to build these in latex.  It uses
                       xslt to generate the tex files.  You'll need to
                       edit the makedoc file to point to your tex
                       installation.
 

-----------------------------------------
These are the README file for some previous distribution tests.  Some
of the information may be useful but some may be obsolete.

2016 Dec  GMH --- older notes
This is a not-quite-ready-for-prime-time attempt at a distribution.

Known Issues:
   1) xmltopsv produces different header orders on different systems for
      the headers whose order is not specified.  This round-trips OK
      but shows diffs in the tests.   I'm not sure what the right order
      should be.

   2) The WINDOWS-1252 codec is broken on some systems in the library

   3) Different xml libraries use ' or " for attribute quoting of the
      <? xml version="1.0"    or  '1.0'   line.  This is fine and
      legal but makes testing hard.  Other legal differences are possible

*  4) I've decided to make the main interface the DOM and not some
      C struct.   This is mainly because most use cases fill less
      than half of the struct and memory management is tricky.  
    
      I've written an example program (writexml) in both C and Python for writing
      a new xml file using the ElementStack interface.   I don't
      have a design for reading yet but we need to know what we want.

   5) This code words on complete documents.  Using SAX/iterparse for
      large files is possible with pretty much the same interface.  

   6) The timings are dominated by program launch times for the
      100-item examples.   I'm not sure how much performance is
      needed.

   7) The code needs some organization.   I wanted to put out something
      working.
     


Specific distribution notes:
   1)   This uses the python lxml module, which is not part of
      the default python.  There are numerous clever ways to 
      try to do binary installs but the most reliable thing
      to do is obtain a source tarball (such as lxml-3.6.4.tar.gx)
      and run "python setup build" and make and so forth on 
      your machine.  Just Google "python packages lxml" and
      poke around untill you find  the source tarball.   
         This is important because all the web sites try 
      to help you by guessing what your configuration is, 
      and they guess wrong all the time.  Find the source tarball 
      and go from that.  This is especially important if your 
      want to make both a python 2 and python 3 installation.

   2)  The runtests script source's a script for picking
       up the executables it uses.  This makes it easy
	to test your own executables

Several issues remain:

   The tests are imcomplete.  You can help by expanding them :-)

   The runtests point out that between python2, python3 and C there
   is a disagreement about the order of fields in PSV.  The ones
   we specifiy are all fine, but the order of extra ones can be
   arbitrary.  All the files round-trip just fine, so this may
   only be a problem for testing.
   
   xmlUTF8Strlen does not return the *width* of a unicode string
   but rather just the number of unicode characters (I *think*
   it handles the combining characters correctly).  This means
   padding to achieve justification in Chinese etc. will be wrong.

   NOTE:  although the maximum allowed field width is 200, that
          means 200 unicode characters.  This may even be longer
          than 200 unicode code points because of combining
          characters.  Python handles memory management properly;
          in C you're on your own. 

   
Usage:
   The executables in the varous bin/ directories (should) have
   the same interface.   To run tests, go to the tests directory
   and run 
     ./runtests prog_python2
     ./runtests prog_python3
     ./runtests prog_c

   Run these into a file since the output can be long.

   prog_python2 assumes #!/usr/bin/env python is python 2.7
   prog_python3 needs to point to your python3 not mine
   prog_c script uses python for the encoding check. xmltopsv
                 and psvtoxml are in C.   Note that the C
                 code my version seems to use single quotes
                 instead of double quotes on the version line
                 <?xml version="1.0" encoding="UTF-8"?>
                 vs.
                 <?xml version='1.0' encoding='UTF-8'?>

                 This confuses diff.  The attributes in the
                 doc are coded the same way.  Notice the EBCDIC
                 and UTF-7 encodings are fine, but the quote
                 differences make them look different.


Notes:

   For now, all the executables start by transforming the 
   xml/adesmaster.xml file into the internal tables using
   xslt/util/tableades.xslt.  This is hard-coded into
   the executables.  Eventually we may want to have the
   tables hard-coded into the executables instead once
   things stabilize.

   For now, all the xsd files are generated from adesmaster.xml
   using xslt/xsd/<name>xsd.xslt files.  We could create 
   external xsd files once we know what the final format will be.

   Those two above items add surprisingly little to program start 
   overhead.


   Everything works by converting input files, including input
   files, into an internal xml etree and doing operations on 
   that.   We may want to use iterparse to handle large files
   but so far this is not an issue.  I'm not sure what large
   means.

   It's really important for performance to not have memory
   leaks.  Memory management is tested with the C executables
   through some commented-out code using the "nMemoryTest" 
   #define in ades.h.


-----------------------

This directory has several sub-directories:


C/

  ./configure creates Makefile.config.
  cd src; make clean; make # builds and puts executables in bin
  cd src; make realclean; # removes executables from bin

  README
  configure.ac
  configure
  install.sh # what a mess
  aclocal.m4 # yup, a mess
  forMacOSXwithout_pkg_config # did I say a mess
  Makefile.config.in
  src/  # make puts executables in bin
  include/
  bin/  # same interface as Python.  At least they're supposed to :=)
           Executables:
              psvtoxml  # psvtoxml <psv file> <xml file>
              xmltopsv  # xmltopsv <xml file> <psv files>
              valall    # valall <xml file>
              valades   # see tests/runtests
              unittest  # this is woefully incomplete
              writexml  # writexml myfile

              The encoding flags for PSV files do not work.  They
              always assume the PSV encoding is UTF-8
Python
  bin/     python executable files and modules.  The modules are
           not executable and are in bin because I didn't want to
           bother with setting pythonpath yet.  

           All the python scripts are good with python2 and python3
               <script>   # runs a script with #!/usr/bin/env python
               <python2> <script>   # runs a script with python2
               <python3> <script>   # runs a script with python3

               Python/bin/xmltopsv <args>
               python xmltopsv <args>
               python3 xmltopsv <args>

           Executables:
              applyxlst
              validate
              encoding

              psvtoxml  # psvtoxml <psv file> <xml file>
              xmltopsv  # xmltopsv <xml file> <psv files>
              valall    # valall <xml file>
              valades   # see tests/runtests
              unittest  # this is woefully incomplete
              writexml  # writexml myfile

writexml myfile <encoding> works in both Python and C++.  
The C and Python conversions don't match, at least on my
machine, because one of the says
<?xml version='1.0' encoding='UTF-8'?>
and the other
<?xml version="1.0" encoding="UTF-8"?>
Both of these are legal.


"writexml myfile UTF-7" is interesting.  



xml/     The adesmaster.xml file lives here.  This is not
         the place for example xml files
     adesmaster.xml

xslt/util/  location for xslt files used by the /bin files as helpers
     Currently only has adestables.xslt

     adestables.xlst
   
xslt/xsd/   location for xslt files used to create xsd files.  I didn't
            include the xsd files themselves since they can be made
            with applyxslt.py.  They'd go in a top-level xsd/
            directory anyway
     distribhumanxsd.xslt
     distribxsd.xslt
     generalhumanxsd.xslt
     generalxsd.xslt
     submithumanxsd.xslt
     submitxsd.xslt


xslt/latex/  Location for xslt files used to translate adesmaster.xml
             into latex input.

     docades.xslt
     docelementstable.xslt
     docgrouptypestable.xslt
     docsimpletypestable.xslt


tests/    Localtion of test files.   It has its own README.
          The runtests script must be run when in the 
          tests/ directory -- it creates some extra dirs
          and knows about the sub-directories.
   


---------------------------------
Some other thoughts:

A) Use iterparse to process documents as a stream

   Both the Python and C work on xml documents, which mean the entire
   input is in memory as an xml tree (even psv input is converted to 
   an xml tree.

   Larger documents may require an iterparse structure. 


B) User interface

    Right now I don't have much for this.   The basic idea
    is to use xml documents for everything an supply routines
    to walk through them.   

    To make a new document, build an xml document, 
    validate it, and then write it either as xml or psv.

    To read a document, read it into an xml tree and
    use methods on the tree.


    Obviously we can build a layer on top of this but I haven't
    given that much work yet.  I think it is not a good idea
    to make a big struct of xmlChar* pointers, since that's 
    going to 

      1) be a recipe for memory leaks
      2) be slow because it's mostly going to be empty

    I think going through the node interface by strings is better,
    In C++ and Python that's easy.  In C and Fortran this is harder
    but I think we should be dealing with the xml directly or 
    indirectly (but conceptually)  in all cases.



C) Unicode handling

  -> Use native UTF-8 whenever possible

  Note python3 will not write UTF-8 to stdout unless the right 
  environment variables are set.  This is going to be a bigger
  problem in the future.  While C/C++ will write bytes, having
  improper terminal settings can create surprises.

      Recommendation:  Transform from file to file.  View files
                       with an editor that supports utf-8 or
                       use file:// on you web browser, which 
                      is happy with utf-8.

-----------------------------------

