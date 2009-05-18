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
from server.command import *
from server.sysadmin import *
from server.command_tag import *
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub

class TestCommandTag(unittest.TestCase):

  def setUp(self):
    self.clear_datastore()

  def test_creation(self):
    command = Command(command = "pwd")
    command.put()
    tag = Tag(name = "lame")
    tag.put()
    command_tag = CommandTag(command = command, tag = tag)
    command_tag.put()
    self.assertEqual(1, len(CommandTag.all().fetch(10)))

  def test_find_tag_by_name_returns_none_if_not_found(self):
    self.assertEquals(None, find_tag_by_name('nothing'))

  def test_create_tag_doesnt_create_duplicates(self):
    create_tag("foo")
    create_tag("foo")
    self.assertEquals(1, len(Tag.all().fetch(10)))

  def test_create_command_tags(self):
    user = User(email = "test@foo.com")
    sysadmin = Sysadmin(goo_user = user)
    sysadmin.put()
    command = Command(command = "pwd", user = sysadmin)
    command.put()
    create_command_tags(sysadmin, command, ["foo", "bar"])
    self.assertEquals(2, len(CommandTag.all().fetch(10)))

  def test_find_commands_by_tag(self):
    user = User(email = "test@foo.com")
    sysadmin = Sysadmin(goo_user = user)
    sysadmin.put()
    command = Command(command = "pwd", user = sysadmin)
    command.put()
    command2 = Command(command = "ls", user = sysadmin)
    command2.put()
    tag = Tag(name = "lame")
    tag.put()
    command_tag = CommandTag(command = command, tag = tag, user = sysadmin)
    command_tag.put()
    command_tag2 = CommandTag(command = command2, tag = tag, user = sysadmin)
    command_tag2.put()
    self.assertEqual(2, len(find_command_tags_by_tag(sysadmin, "lame", 1)))

  def test_find_by_tag_orders_by_command_creation_date(self):
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    oldest_command = add_command(admin, "ls")
    newest_command = add_command(admin, "vi")
    create_command_tags(admin, newest_command, ["foo"])
    create_command_tags(admin, oldest_command, ["foo"])
    self.assertEqual(newest_command.key(), find_command_tags_by_tag(admin, "foo", 1)[0].command.key())

  def test_limit_tag_count_to_four(self):
    tags = [1,2,3,4,5]
    self.assertEqual([1,2,3,4], limit_tag_count(tags))

  def test_limit_tag_count_does_nothing_if_list_is_under_limit(self):
    tags = [1,2,3]
    self.assertEqual(tags, limit_tag_count(tags))

  def clear_datastore(self):
    # Use a fresh stub datastore.
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    stub = datastore_file_stub.DatastoreFileStub('shell-sink', '/dev/null', '/dev/null')
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub) 
