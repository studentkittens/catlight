# Name: Makefile
# Project: hid-custom-rq example
# Author: Christian Starkjohann
# Creation Date: 2008-04-06
# Tabsize: 4
# Copyright: (c) 2008 by OBJECTIVE DEVELOPMENT Software GmbH
# License: GNU GPL v2 (see License.txt), GNU GPL v3 or proprietary (CommercialLicense.txt)
# This Revision: $Id: Makefile 692 2008-11-07 15:07:40Z cs $


# Concigure the following definitions according to your system.
# This Makefile has been tested on Mac OS X, Linux and Windows.

# Use the following 3 lines on Unix (uncomment the framework on Mac OS X):
USBFLAGS   = `libusb-config --cflags`
USBLIBS    = `libusb-config --libs`
GLIBFLAGS  = `pkg-config --cflags glib-2.0`
GLIBLIBS   = `pkg-config --libs   glib-2.0`
EXE_SUFFIX =

# Use the following 3 lines on Windows and comment out the 3 above. You may
# have to change the include paths to where you installed libusb-win32
#USBFLAGS = -I/usr/local/include
#USBLIBS = -L/usr/local/lib -lusb
#EXE_SUFFIX = .exe

NAME = catlight
SRC=src
BIN=bin

OBJECTS = $(SRC)/$(NAME).o

CC		= gcc
CFLAGS	= $(CPPFLAGS) $(USBFLAGS) $(GLIBFLAGS) -Os -Wall -Wextra
LIBS	= $(USBLIBS) $(GLIBLIBS)

PROGRAM = $(BIN)/$(NAME)$(EXE_SUFFIX)


all: $(PROGRAM)

.c.o:
	$(CC) $(CFLAGS) -c $<

$(PROGRAM): $(OBJECTS)
	$(CC) -o $(PROGRAM) *.o $(LIBS)
	cd catlightd && go build catlightd.go
	cd catlightctl && go build catlightctl.go

strip: $(PROGRAM)
	strip -s $(PROGRAM)

clean:
	rm -f *.o $(PROGRAM)

install:
	chmod u+s $(PROGRAM)
	cp $(PROGRAM) /usr/bin/
	cp catlightd/catlightd /usr/bin
	cp catlightctl/catlightctl /usr/bin
