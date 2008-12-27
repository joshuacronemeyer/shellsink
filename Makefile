# $Id: Makefile,v 1.6 2008/12/26 01:01:35 josh Exp $
#
PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/shellsink
PROJECT=shellsink
VERSION=0.1.4

all:
		@echo "make install - Install on local system"
		@echo "make builddeb - Generate a deb package"
		@echo "make clean - Get rid of scratch and byte files"

install:
		$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

builddeb:
		mkdir -p ${BUILDIR}
		DESTDIR=$(BUILDIR) dpkg-buildpackage -rfakeroot

buildsrc:
		tar czf shellsink_$(VERSION).orig.tar.gz debian setup.py Makefile shellsink-client
		mkdir build
		tar -C build -xzf shellsink_$(VERSION).orig.tar.gz
		cd $(CURDIR)/build; debuild -S

clean:
		$(PYTHON) setup.py clean
		$(MAKE) -f $(CURDIR)/debian/rules clean
		rm -rf build/ MANIFEST
		rm -rf shellsink_*
		find . -name '*.pyc' -delete
