"""
This file is part of Shell-Sink.
Copyright Joshua Cronemeyer 2008, 2009

Shell-Sink is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shell-Sink is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License v3 for more details.

You should have received a copy of the GNU General Public License
along with Shell-Sink.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
from shellsink_client import *
from mock import Mock
import os

class TestHistoryFile(unittest.TestCase):
  def test_new_command_is_detected_when_timestamp_is_newer(self):
    history= StubHistory()
    history.new_time = 2
    history.old_time = 1
    self.assertEqual(True, history.has_new_command())

  def test_new_command_is_not_detected_when_timestamp_is_older(self):
    history= StubHistory()
    history.new_time = 1
    history.old_time = 2
    self.assertEqual(False, history.has_new_command())

  def test_new_command_is_detected_when_no_previous_timestamp_existed(self):
    history= StubHistory()
    history.new_time = 1
    history.old_time = None
    self.assertEqual(True, history.has_new_command())

class StubHistory(HistoryFile):

  def __init__(self):
    pass

  def latest(self):
    return "the latest command"

  def history_file_timestamp(self):
    return self.new_time

  def last_recorded_history_timestamp(self):
    return self.old_time

  def record_new_last_recorded_history_timestamp(self, timestamp):
    pass

if __name__ == '__main__':
    unittest.main()

