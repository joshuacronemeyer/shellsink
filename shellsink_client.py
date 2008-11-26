#!/usr/bin/env python
import urllib2
import urllib
import socket
import sys
import os

SOCKET_TIMEOUT=0.5
#URL="http://localhost:8080/history/add"
URL="http://bash-history.appspot.com/history/add"

class Client:
  def __init__(self, id):
    if not os.environ.has_key('HOME'):
      raise Exception, "HOME environment variable must be set"

    self.history_file = os.environ['HOME'] + "/.bash_history"
    self.history_timestamp = os.environ['HOME'] + "/.bash_history_timestamp"
    self.id = id

  def send_command(self, command):
    if not self.has_new_command():
      return None

    params = {'hash' : self.id, 'command' : command}
    data = urllib.urlencode(params)
    url = URL + '?' + data
    try:
      req = urllib2.urlopen(url)
    except:
      pass

  def has_new_command(self):
    new_history_timestamp = os.path.getmtime(self.history_file)
    old_history_timestamp = new_history_timestamp - 1

    if os.path.exists(self.history_timestamp):
      file = open(self.history_timestamp,"r")
      old_history_timestamp = float(file.readline())
      file.close()

    file = open(self.history_timestamp,"w")
    file.writelines([str(new_history_timestamp)])
    file.close()

    return new_history_timestamp > old_history_timestamp


#would be cool to have the following
####
####command to open my history in browser tab
####be able to turn off so you only log ad-hoc
####command to add tag to list of tags being used
####way to add a tag to a command as it is being issued.  Perhaps the command before should be tag... that lets you set a one time tag.
####command to clear tags being used
####of course tags that are specified in the env variables are never cleared
####logging to syslog any problems
####command to pull last n commands to local history
####command to pull last n commands with tags a...z to local history
####batch up commands to send to server
socket.setdefaulttimeout(SOCKET_TIMEOUT)
client = Client(sys.argv[1])
client.send_command(sys.argv[2])
