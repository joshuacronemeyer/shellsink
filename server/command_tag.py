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
from command import Command
from sysadmin import Sysadmin
from google.appengine.ext import db

class Tag(db.Model):
  name = db.CategoryProperty()

class CommandTag(db.Model):
  command = db.ReferenceProperty(Command)
  tag = db.ReferenceProperty(Tag)
  user = db.ReferenceProperty(Sysadmin)
  tag_creation_date = db.DateTimeProperty(auto_now_add=True)
  command_creation_date = db.DateTimeProperty()
  MAX_TAGS_YOU_CAN_ADD_AT_ONE_TIME = 4

def limit_tag_count(tags):
  number_of_tags = len(tags)
  if (number_of_tags > CommandTag.MAX_TAGS_YOU_CAN_ADD_AT_ONE_TIME):
    tags = tags[0:CommandTag.MAX_TAGS_YOU_CAN_ADD_AT_ONE_TIME]
  return tags

def find_tag_by_name(name):
  tag = Tag.all().filter('name =', name).fetch(1)
  if len(tag) > 0:
    return tag[0]
  return None

def create_tag(name):
  tag = find_tag_by_name(name)
  if not tag:
    tag = Tag(name = name)
    tag.put()
  return tag

def create_command_tags(sysadmin, command, tag_names):
  for tag_name in tag_names:
    tag = create_tag(tag_name)
    command_tag = CommandTag(user = sysadmin, tag = tag, command = command, command_creation_date = command.date)
    command_tag.put()
  command.tags.extend(tag_names)
  command.put()

def find_command_tags_by_tag(sysadmin, tag_name, page):
  tag = find_tag_by_name(tag_name)
  command_tag_query = db.GqlQuery("SELECT * FROM CommandTag WHERE user = :user AND tag = :tag ORDER BY command_creation_date desc", user = sysadmin, tag = tag)
  return command_tag_query.fetch(Command.COMMANDS_PER_PAGE, (page - 1) * Command.COMMANDS_PER_PAGE)

def find_commands_by_filter_tag_for_atom(sysadmin):
  command_tags = find_command_tags_by_tag(sysadmin, sysadmin.filter(), 1)
  commands = []
  for command_tag in command_tags:
    commands.append(command_tag.command)
  return commands
