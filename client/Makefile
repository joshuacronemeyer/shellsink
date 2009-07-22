# $Id: Makefile,v 1.6 2008/12/26 01:01:35 josh Exp $
#
PYTHON=`which python`
DESTDIR=/

all:
		@echo "make install - Install on local system"
		@echo "make buildsrc - Generate a deb source package"
		@echo "make clean - Get rid of scratch and byte files"

install:
		$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildsrc:
		debuild -S

clean:
		$(PYTHON) setup.py clean
		$(MAKE) -f $(CURDIR)/debian/rules clean
