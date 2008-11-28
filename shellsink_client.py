#!/usr/bin/env python
import urllib2
import urllib
import socket
import sys
import os

SOCKET_TIMEOUT=10
#URL="http://localhost:8080/history/add"
URL="http://bash-history.appspot.com/history/add"

class Client:
  def __init__(self):
    self.verify_environment
    self.history_file = self.environment()['HOME'] + "/.bash_history"
    self.history_timestamp = self.environment()['HOME'] + "/.bash_history_timestamp"
    self.id = self.environment()['SHELL_SINK_ID']

  def verify_environment(self):
    if not self.environment().has_key('HOME'):
      raise Exception, "HOME environment variable must be set"
    if not self.environment().has_key('SHELL_SINK_ID'):
      raise Exception, "SHELL_SINK_ID environment variable must be set"

  def environment(self):
    return os.environ

  def send_command(self):
    params = {'hash' : self.id, 'command' : self.latest_from_history()}
    data = urllib.urlencode(params)
    url = URL + '?' + data
    self.spawn_process(http_get, url)
    
  def spawn_process(self, func, arg):
    pid = os.fork()
    if pid > 0:
      sys.exit(0)
    os.setsid()
    pid = os.fork()
    if pid > 0:
      sys.exit(0)
    func(arg)

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

  def latest_from_history(self):
    file = open(self.history_file, "r")
    latest = file.readlines()[-1]
    file.close()
    return latest

def http_get(url):
  try:
    urllib2.urlopen(url)
  except:
    pass

socket.setdefaulttimeout(SOCKET_TIMEOUT)
Client().send_command()
