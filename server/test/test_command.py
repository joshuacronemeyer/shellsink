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

class TestCommand(unittest.TestCase):

  def setUp(self):
    self.clear_datastore()

  def test_creation(self):
    command = Command(command = "pwd")
    command.put()
    fetched = Command.all().filter('command =', "pwd").fetch(1)[0]
    self.assertEquals(fetched.command, "pwd")

  def test_add_command(self):
    admin = create_first_time_sysadmin(User(email = "foo@foo.com"))
    add_command(admin, "foo")
    self.assertEqual(len(Command.all().fetch(10)), 1)
    add_command(admin, "bar")
    self.assertEqual(len(Command.all().fetch(10)), 2)

  def test_fetch_commands(self):
    admin = create_first_time_sysadmin(User(email = "foo@foo.com"))
    add_command(admin, "foo")
    add_command(admin, "bar")
    self.assertEqual(len(fetch_commands(admin, 1)), 2)

  def test_commands_are_sorted_newest_first_in_results(self):
    admin = create_first_time_sysadmin(User(email = "foo@foo.com"))
    add_command(admin, "foo")
    new_command = add_command(admin, "bar")
    self.assertEqual(new_command.key(), fetch_commands(admin, 1)[0].key())

  def test_commands_are_only_fetched_for_the_user_they_are_associated_with(self):
    admin = create_first_time_sysadmin(User(email = "foo@foo.com"))
    admin2 = create_first_time_sysadmin(User(email = "foo2@foo.com"))
    add_command(admin, "foo")
    new_command = add_command(admin, "bar")
    self.assertEqual(0, len(fetch_commands(admin2, 1)))

  def test_command_can_have_tags(self):
    command = Command(command = "pwd", tags = ["foo", "bar"])
    command.put()
    fetched = Command.all().fetch(10)[0]
    self.assertEquals(["foo", "bar"], fetched.tags)

  def test_find_command_by_db_key(self):
    command = Command(command = "pwd")
    command.put()
    fetched = find_command_by_db_key(command.key())
    self.assertEquals(command.key(), fetched.key())

  def test_full_text_search_gives_correct_results_down_to_a_one_character_search(self):
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    admin2 = create_first_time_sysadmin(User(email = "weasel@goo.com"))
    command = add_command(admin, "v")
    add_command(admin, "ls")
    command2 = add_command(admin2, "v command.py")
    commands = Command.all().filter('user =', admin).search("v")
    self.assertEquals(1, len(commands.fetch(10)))
    self.assertEquals(command.key(), commands[0].key())

  def test_full_text_search_ignores_keywords_after_first_two(self):
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    admin2 = create_first_time_sysadmin(User(email = "weasel@goo.com"))
    command = add_command(admin, "python is great")
    command = add_command(admin, "python")
    add_command(admin, "will find wont find")
    search_results = full_text_search(admin, "wont find python is great", 1)
    self.assertEquals(1, len(search_results))

  def test_full_text_search_finds_matches(self):
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    admin2 = create_first_time_sysadmin(User(email = "weasel@goo.com"))
    command = add_command(admin, "python")
    add_command(admin, "cd /Users/admin/stuff")
    search_results = full_text_search(admin, "python", 1)
    self.assertEquals(command.key(), search_results[0].key())

  def test_full_text_search_doesnt_find_matches_if_user_has_no_commands(self):
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    admin2 = create_first_time_sysadmin(User(email = "weasel@goo.com"))
    add_command(admin, "cd /Users/admin/stuff")
    search_results = full_text_search(admin2, "cd", 1)
    self.assertEquals(0,len(search_results))

  def test_full_text_search_paging_works(self):
    Command.COMMANDS_PER_PAGE = 2
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    command = add_command(admin, "cd /Users/admin/stuff")
    add_command(admin, "cd /Users/admin/stuff")
    add_command(admin, "cd /Users/admin")
    search_results = full_text_search(admin, "cd", 2)
    self.assertEquals(1, len(search_results))
    self.assertEquals(command.key(), search_results[0].key())

  def test_first_command_entered_is_last_in_search_results(self):
    admin = create_first_time_sysadmin(User(email = "foo@goo.com"))
    command = add_command(admin, "cd /Users/admin/stuff")
    add_command(admin, "cd /Users/admin/stuff")
    search_results = full_text_search(admin, "cd", 1)
    self.assertEquals(command.key(), search_results[-1].key())

  def clear_datastore(self):
    # Use a fresh stub datastore.
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    stub = datastore_file_stub.DatastoreFileStub('shell-sink', '/dev/null', '/dev/null')
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub) 
