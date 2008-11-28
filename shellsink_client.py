#!/usr/bin/env python
import urllib2
import urllib
import socket
import sys
import os

SOCKET_TIMEOUT=10
URL="http://localhost:8080/history/add"
#URL="http://bash-history.appspot.com/history/add"

class Client:
  def __init__(self):
    self.verify_environment
    self.history_file = os.environ['HOME'] + "/.bash_history"
    self.history_timestamp = os.environ['HOME'] + "/.bash_history_timestamp"
    self.id = os.environ['SHELL_SINK_ID']

  def verify_environment(self):
    if not os.environ.has_key('HOME'):
      raise Exception, "HOME environment variable must be set"
    if not os.environ.has_key('SHELL_SINK_ID'):
      raise Exception, "SHELL_SINK_ID environment variable must be set"

  def url_with_command(self):
    params = {'hash' : self.id, 'command' : self.latest_from_history()}
    data = urllib.urlencode(params)
    return URL + '?' + data

  def send_command(self):
    self.spawn_process(http_get, self.url_with_command())
    
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
    new_history_timestamp = self.history_file_timestamp()
    timestamp_if_there_is_no_last_recorded = new_history_timestamp - 1
    last_recorded_history_timestamp = self.last_recorded_history_timestamp()
    if not last_recorded_history_timestamp:
      last_recorded_history_timestamp = timestamp_if_there_is_no_last_recorded

    self.record_new_last_recorded_history_timestamp(new_history_timestamp)
    return new_history_timestamp > last_recorded_history_timestamp

  def history_file_timestamp(self):
    return os.path.getmtime(self.history_file)

  def last_recorded_history_timestamp(self):
    if os.path.exists(self.history_timestamp):
      file = open(self.history_timestamp,"r")
      old_history_timestamp = float(file.readline())
      file.close()
      return old_history_timestamp
    return None

  def record_new_last_recorded_history_timestamp(self, timestamp):
    file = open(self.history_timestamp,"w")
    file.writelines([str(timestamp)])
    file.close()

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

if __name__== '__main__':
  socket.setdefaulttimeout(SOCKET_TIMEOUT)
  Client().send_command()
