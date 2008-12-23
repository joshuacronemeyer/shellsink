#!/usr/bin/python
import shutil
import os

project = 'shellsink'
version = '0.1'
dist = project + '-' + version
tarfile = project + '_' + version + '.orig.tar.gz'

os.mkdir(dist)
shutil.copytree('debian', dist + '/debian')
shutil.copy('shellsink_client.py', dist)
tarcommand = "tar czf " + tarfile + " " + dist
os.system(tarcommand)
