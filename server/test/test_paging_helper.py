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
from shell_sink.paging_helper import *

class TestPagingHelper(unittest.TestCase):

  def test_paging_helper_knows_if_there_is_a_previous_page(self):
    page = 10
    helper = PagingHelper(page, "", [])
    self.assertEquals(True, helper.has_prev())

  def test_paging_helper_knows_default_page_is_page_one(self):
    helper = PagingHelper("", "", [])
    self.assertEquals(1, helper.page)

  def test_paging_helper_creates_next_url(self):
    correct_next_url = "/showTag?page=2&tag=foo"
    helper = PagingHelper("", 'showTag', ['tag=foo'])
    self.assertEquals(correct_next_url, helper.next_url())

  def test_paging_helper_creates_previous_url(self):
    correct_next_url = "/showTag?page=1&tag=foo&other=bar"
    helper = PagingHelper("2", 'showTag', ['tag=foo', 'other=bar'])
    self.assertEquals(correct_next_url, helper.previous_url())
