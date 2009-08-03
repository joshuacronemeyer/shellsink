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

class TestInlineTag(unittest.TestCase):
  def test_one_inline_tag(self):
    client = StubClient() 
    self.assertEqual(['tag'], client.inline_tags("echo #tag"))
  
  def test_zero_inline_tags(self):
    client = StubClient() 
    self.assertEqual(None, client.inline_tags("echo"))

  def test_two_inline_tags(self):
    client = StubClient() 
    self.assertEqual(["tag1", "tag2"], client.inline_tags("echo #tag1:tag2"))

  def test_one_escaped_comment_delimiter(self):
    client = StubClient() 
    self.assertEqual(None, client.inline_tags("echo \#tag1:tag2"))

  def test_one_escaped_comment_delimiter_and_one_unescaped(self):
    client = StubClient() 
    self.assertEqual(["tag2"], client.inline_tags("echo \#tag1 #tag2"))

  def test_two_escaped_comment_delimiters_and_two_unescaped(self):
    client = StubClient()
    self.assertEqual(["tag1", "tag2"], client.inline_tags("echo \#tag1 \#tag2 #tag1:tag2"))

#These document a known issue.
#  def test_strange_adjoining_comments_are_escaped_behavior(self):
#    client = StubClient()
#    self.assertEqual(None, client.inline_tags("echo \##tag"))

#  def test_strange_adjoining_comments_are_escaped_behavior_can_have_tag_later(self):
#    client = StubClient()
#    self.assertEqual(["taglater"], client.inline_tags("echo \##tag #taglater"))


class StubClient(Client):

  def __init__(self):
    pass
  
if __name__ == '__main__':
    unittest.main()

