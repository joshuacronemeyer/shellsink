#!/usr/bin/env python

from distutils.core import setup

setup(name = "shellsink",
    version = "0.1",
    description = "Shellsink is a tool for storing your bash history on the shellsink.com server",
    author = "Josh Cronemeyer",
    author_email = "joshuacronemeyer@shellsink.com",
    url = "http://shellsink.com",
    data_files = [('/usr/bin', ['shellsink-client'])]
    )
