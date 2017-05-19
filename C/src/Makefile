-include ../Makefile.config

#
# for WILDCARDSOURCES
#
VPATH = .


#
# .c and .cpp source files
#
C_SOURCES = $(WILDCARDSOURCES_C)
CXX_SOURCES = $(WILDCARDSOURCES_CXX)

#
# .o files from .c and .cpp files
#
OBJECTS = $(C_SOURCES:.c=.o) $(CXX_SOURCES:.cpp=.o)

#
# programs to build
#
PROGRAMS = unittest testthings testthings2 valall valgeneral valsubmit valades oldvalades xmltopsv psvtoxml writexml writexmlc readxmlc

#
# all programs are put in $(PREFIX)/bin 
#
BINPROGS = $(addprefix $(PREFIX)/bin/,$(PROGRAMS))

#
# libobjs are all .o files which are not <program>.o
#
LIBOBJS = $(filter-out $(addsuffix .o,$(PROGRAMS)), $(OBJECTS))


#
# Rules for building .o, .d, and $(PREFIX)/bin/<prog> are 
# in ../Makefile.config made by configure.  That also
# defines $(RM), $(LD) and aother useful things
#

#
# The default target, all, builds all the programs and 
# then puts them in $(PREFIX)/bin using a recursive call
#
.PHONY: 
all: programs   
	make $(BINPROGS)

#
# build all the program objects
#
.PHONY: 
programs: $(PROGRAMS)

#
# The clean target removes all built files from the src dir.
#
.PHONY: clean
clean:
	$(RM) -rf $(OBJECTS) $(PROGRAMS) $(DEPEND_INCLUDES)

#
# The realclean target removes the $(PREFIX)/bin files as
# well as everything removed by clean.
#
.PHONY: realclean
realclean: clean
	$(RM) -rf $(BINPROGS)


#
# need explicit rules for some programs since member
# not all of them link with all $(LIBOBJS)
#

%: %.o $(LIBOBJS)
	$(LD) $< $(LIBOBJS) -o $@

oldvalades: oldvalades.o 
	$(LD) $< -o $@

#
# .d files are included to catch updates needed when .h files
# are changed.  The .d file is generated (see Makefile.config
# for the rule) from the source.  It contains a rule making
# a dependency on all includes.
#
DEPEND_INCLUDES = $(C_SOURCES:.c=.d) $(CXX_SOURCES:.cpp=.d)

ifneq ($(nodepend),1)
    -include $(DEPEND_INCLUDES)
endif

