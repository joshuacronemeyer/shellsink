import logging
import cgi
import os
import datetime
from command import *
from sysadmin import *
from command_tag import *
from paging_helper import PagingHelper
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
  def get(self):
    logged_in = users.get_current_user()
    if not logged_in:
      self.redirect(users.create_login_url(self.request.uri))
      return

    if create_first_time_sysadmin(logged_in):
      self.redirect('/preferences')
      return
    self.redirect('/history')

class History(webapp.RequestHandler):
  def get(self):
    paging_helper = PagingHelper(self.request.get('page'), 'history', [])
    goo_user = users.get_current_user()
    sysadmin = find_sysadmin_by_user(goo_user)
    commands = fetch_commands(sysadmin, paging_helper.page)
    no_commands = False
    if len(commands) == 0:
      no_commands = True

    template_values = {
        'username': goo_user.nickname(),
        'commands': commands,
        'logout_url': users.create_logout_url("/"),
        'paging_helper': paging_helper,
        'no_commands': no_commands
        }

    path = os.path.join(os.path.dirname(__file__), 'html/commands.html')
    self.response.out.write(template.render(path, template_values))

class AddCommand(webapp.RequestHandler):
  def get(self):
    #called by the client
    sysadmin = find_sysadmin_by_id(self.request.get('hash'))
    if not sysadmin:
      self.response.clear()
      self.response.set_status(404)
      self.response.out.write("The account requested doesn't exist.") 
      return

    command = add_command(sysadmin, self.request.get('command'))

    print 'Content-Type: text/plain'
    print ''
    print command.key()


class AddTag(webapp.RequestHandler):
  def get(self):
    #called by the client
    command = find_command_by_db_key(self.request.get('command'))
    if not command:
      self.response.clear()
      self.response.set_status(404)
      self.response.out.write("The command requested doesn't exist.") 
      return

    command.user.add_tags([self.request.get('tag')])
    create_command_tags(command.user, command, [self.request.get('tag')])

  def post(self):
    #ajax call
    tags = self.request.get('tag').split(",")
    command = find_command_by_db_key(self.request.get('id'))
    sysadmin = find_sysadmin_by_user(users.get_current_user())
    if len(tags[0]) > 0:
      sysadmin.add_tags(tags)
      create_command_tags(sysadmin, command, tags)

    template_values = {
      'tags' : command.tags
      }

    path = os.path.join(os.path.dirname(__file__), 'html/tags.html')
    self.response.out.write(template.render(path, template_values))

class AddAnnotation(webapp.RequestHandler):
  def post(self):
    #ajax call
    command = find_command_by_db_key(self.request.get('id'))
    command.annotation = self.request.get('annotation')[0:499]
    command.put()
    template_values = {
        'username': users.get_current_user().nickname(),
        'logout_url': users.create_logout_url("/"),
        'command': command
        }
    path = os.path.join(os.path.dirname(__file__), 'html/annotation.html')
    self.response.out.write(template.render(path, template_values))

class ShowCommand(webapp.RequestHandler):
  def get(self):
    command = find_command_by_db_key(self.request.get('id'))
    template_values = {
        'username': users.get_current_user().nickname(),
        'logout_url': users.create_logout_url("/"),
        'commands': [command]
        }
    path = os.path.join(os.path.dirname(__file__), 'html/command.html')
    self.response.out.write(template.render(path, template_values))

class ShowTag(webapp.RequestHandler):
  class CommandTagWrapper():
    def __init__(self, command_tag):
      self.command_tag = command_tag
      self.command = self.command_tag.command.command
      self.key = self.command_tag.command.key
      self.date = self.command_tag.command.date
      self.tags = self.command_tag.command.tags
      self.annotation = self.command_tag.command.annotation

  def wrap_command_tags(self, command_tags):
    commands = []
    for command_tag in command_tags:
      commands.append(ShowTag.CommandTagWrapper(command_tag))
    return commands

  def get(self):
    tag = self.request.get('tag')
    paging_helper = PagingHelper(self.request.get('page'), 'showTag', ['tag='+tag])
    goo_user = users.get_current_user()
    sysadmin = find_sysadmin_by_user(goo_user)
    command_tags = find_command_tags_by_tag(sysadmin, tag, paging_helper.page)
    template_values = {
        'tag' : tag,
        'username': goo_user.nickname(),
        'commands' : self.wrap_command_tags(command_tags),
        'logout_url' : users.create_logout_url("/"),
        'paging_helper': paging_helper,
        }
    path = os.path.join(os.path.dirname(__file__), 'html/commands_by_tag.html')
    self.response.out.write(template.render(path, template_values))

class Preferences(webapp.RequestHandler):
  def get(self):
    goo_user = users.get_current_user()
    sysadmin = find_sysadmin_by_user(goo_user)
    filter = sysadmin.filter()
    template_values = {
        'username': goo_user.nickname(),
        'hash': sysadmin.hash,
        'key': sysadmin.key(),
        'tags': sysadmin.tags,
        'filter': filter,
        'disable_atom': sysadmin.disable_atom,
        'logout_url' : users.create_logout_url("/"),
        }

    path = os.path.join(os.path.dirname(__file__), 'html/preferences.html')
    self.response.out.write(template.render(path, template_values))

class CommandSearch(webapp.RequestHandler):
  def post(self):
    query = self.request.get('query')
    paging_helper = PagingHelper(self.request.get('page'), 'commandSearch', ['query='+query])
    goo_user = users.get_current_user()
    sysadmin = find_sysadmin_by_user(goo_user)
    commands = full_text_search(sysadmin, query, paging_helper.page)
    template_values = {
        'username': goo_user.nickname(),
        'commands': commands,
        'query': query,
        'logout_url': users.create_logout_url("/"),
        'paging_helper': paging_helper,
        }

    path = os.path.join(os.path.dirname(__file__), 'html/commands.html')
    self.response.out.write(template.render(path, template_values))

  def get(self):
    self.post()

class Atom(webapp.RequestHandler):
  def get(self):
    sysadmin = db.get(self.request.get('user_id'))
    if sysadmin.disable_atom == 'true':
      commands = []
    elif sysadmin.filter() == "":
      commands = fetch_commands(sysadmin, 1)
    else:
      commands = find_commands_by_filter_tag_for_atom(sysadmin)
    update_time = datetime.datetime.now()
    if len(commands) > 0:
      update_time = commands[0].date
    template_values = {
      'year': datetime.datetime.now().year,
      'user_id': sysadmin.hash,
      'nickname': sysadmin.goo_user.nickname(),
      'update_time': update_time,
      'email': sysadmin.goo_user.email(),
      'commands': commands, 
      }

    path = os.path.join(os.path.dirname(__file__), 'html/atom.xml')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    #this is ajax updateFilter
    sysadmin = find_sysadmin_by_id(self.request.get('id'))
    if (self.request.get('filter')):
      sysadmin.atom_filter = self.request.get('filter')
    if (self.request.get('disable_atom')):
      sysadmin.disable_atom = self.request.get('disable_atom')
    sysadmin.put()

class PullCommands(webapp.RequestHandler):
  def get(self):
    #called by client
    sysadmin = find_sysadmin_by_id(self.request.get('hash'))
    tag = self.request.get('tag')
    keyword = self.request.get('keyword')
    if not sysadmin:
      return
    
    if tag:
      command_tags = find_command_tags_by_tag(sysadmin, tag, 1)
      commands = []
      for command_tag in command_tags:
        commands.append(ShowTag.CommandTagWrapper(command_tag))
    elif keyword:
      commands = full_text_search(sysadmin, keyword, 1)
    else:
      commands = fetch_commands(sysadmin, 1)
    
    if not commands:
      commands = []
    commands.reverse()

    #return lame xml
    print 'Content-Type: text/xml'
    print ''
    print '<shellsink-commands>'
    for command in commands:
      print command.command.strip()
    print '</shellsink-commands>'
    print ''

application = webapp.WSGIApplication(
    [ ('/', MainPage), 
      ('/history', History), 
      ('/addCommand', AddCommand), 
      ('/addTag', AddTag), 
      ('/preferences', Preferences),
      ('/addTag', AddTag),
      ('/showTag', ShowTag),
      ('/commandSearch', CommandSearch),
      ('/atom', Atom),
      ('/setAtomPreference', Atom),
      ('/addAnnotation', AddAnnotation),
      ('/showCommand', ShowCommand),
      ('/pull', PullCommands),
    ], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
