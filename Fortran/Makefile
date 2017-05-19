#!/usr/bin/make


.SUFFIXES:
.SUFFIXES: .o .f90


FC=gfortran
FFLAGS=-g -O2 

INCFLAGS=`fox-master/FoX-config --fcflags`
LNKFLAGS=`fox-master/FoX-config --libs --dom`


#Dependency rules are created by autoconf according to whether
#discrete preprocessing is necessary or not.
.f90.o:
	$(FC) -c $(FFLAGS) $(INCFLAGS) $(FCFLAGS_free_f90)  $<


EXAMPLES=readxmlfox writexmlfox

default: $(EXAMPLES)

readxmlfox: readxmlfox.o
	gfortran $(FFLAGS) -o $@ $< $(LNKFLAGS)

writexmlfox: writexmlfox.o
	gfortran $(FFLAGS) -o $@ $< $(LNKFLAGS)

clean: 
	rm -f *.o $(EXAMPLES)
