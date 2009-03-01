import sys
import string
from sysadmin import Sysadmin
import command_search
from google.appengine.ext import db
from google.appengine.ext import search

class Command(command_search.SearchableModel):
  command = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)
  user = db.ReferenceProperty(Sysadmin)
  tags = db.StringListProperty()
  annotation = db.StringProperty(multiline=True)
  COMMANDS_PER_PAGE = 20
  MAX_KEYWORDS = 2

def find_command_by_db_key(db_key):
  return db.get(db_key)
  
def add_command(sysadmin, command_string):
  command = Command(command = command_string, user = sysadmin)
  command.put()
  return command

def fetch_commands(sysadmin, page):
  query = Command.all().filter('user =', sysadmin).order('-date')
  return query.fetch(Command.COMMANDS_PER_PAGE, (page - 1) * Command.COMMANDS_PER_PAGE)

def full_text_search(sysadmin, query, page):
  if (query == None):
    return None

  number_of_keywords = len(query.split())
  if (number_of_keywords > Command.MAX_KEYWORDS):
    query = string.join(query.split(None, Command.MAX_KEYWORDS)[0:-1], ' ')

  query = Command.all().filter('user =', sysadmin).order('-date').search(query)
  return query.fetch(Command.COMMANDS_PER_PAGE, (page - 1) * Command.COMMANDS_PER_PAGE)
