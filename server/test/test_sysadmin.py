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
from google.appengine.api.users import User
from server.sysadmin import *
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub

class TestSysadmin(unittest.TestCase):
  
  def setUp(self):
    self.clear_datastore()

  def test_creation(self):
    self.create_sysadmin()
    fetched_admin = Sysadmin.all().filter('goo_user =', self.user).fetch(1)[0]
    self.assertEquals(fetched_admin.goo_user, self.user)

  def test_db_is_recreated_between_tests(self):
    user = User(email = "test@foo.com")
    fetched = Sysadmin.all().filter('goo_user =', user).fetch(1)
    self.assertEquals(fetched, [])

  def test_find_by_google_user(self):
    self.create_sysadmin()
    fetched = find_sysadmin_by_user(self.user)
    self.assertEquals(fetched.key(), self.admin.key())

  def test_find_by_google_user_returns_none_if_record_doesnt_exit(self):
    self.create_sysadmin()
    fetched = find_sysadmin_by_user(User(email = "notfound@foo.com"))
    self.assertEquals(fetched, None)

  def test_first_time_sysadmin_creation(self):
    admin = create_first_time_sysadmin(User(email = "new@foo.com"))
    fetched = find_sysadmin_by_user(admin.goo_user)
    self.assert_(fetched.hash)

  def test_create_first_time_sysadmin_doesnt_create_new_entry_for_existing(self):
    user = User(email = "new@foo.com")
    admin = create_first_time_sysadmin(user)
    again_admin = create_first_time_sysadmin(user)
    self.assertEquals(1, len(Sysadmin.all().fetch(10)))
    self.assertEquals(again_admin, None)

  def test_find_sysadmin_by_id(self):
    admin = create_first_time_sysadmin(User(email = "new@foo.com"))
    self.assertEquals(find_sysadmin_by_id(admin.hash).key(), admin.key())

  def test_find_sysadmin_by_id_returns_none_when_not_found(self):
    self.assertEquals(find_sysadmin_by_id(1234), None)

  def test_filter_comes_back_as_empty_string_if_there_is_no_filter(self):
    admin = create_first_time_sysadmin(User(email = "new@foo.com"))
    self.assertEquals("", admin.filter())

  def test_adding_duplicate_tags_doesnt_create_duplicates(self):
    admin = create_first_time_sysadmin(User(email = "new@foo.com"))
    admin.add_tags(["foo"])
    admin.add_tags(["foo", "foo"])
    admin.put()
    self.assertEquals(["foo"], find_sysadmin_by_id(admin.hash).tags)
    admin.add_tags(["bar"])
    admin.put()
    self.assertEquals(["foo", "bar"], find_sysadmin_by_id(admin.hash).tags)

  def create_sysadmin(self):
    self.user = User(email = "test@foo.com")
    self.admin = Sysadmin(goo_user = self.user)
    self.admin.put()

  def clear_datastore(self):
    # Use a fresh stub datastore.
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    stub = datastore_file_stub.DatastoreFileStub('shell-sink', '/dev/null', '/dev/null')
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub) 
