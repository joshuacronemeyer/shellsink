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
