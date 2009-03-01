import hashlib
from time import time
from google.appengine.ext import db
class Sysadmin(db.Model):
  goo_user = db.UserProperty()
  hash = db.StringProperty()
  atom_filter = db.StringProperty()
  disable_atom = db.StringProperty(default='true')
  tags = db.StringListProperty() #the set of all tags this user has ever created, shows up on preferences

  def new_hash(self):
    name = self.goo_user.nickname()
    self.hash = hashlib.md5(name + str(time())).hexdigest()
    self.put()
    return self.hash

  def filter(self):
    if self.atom_filter:
      return self.atom_filter
    return ""
  
  def add_tags(self, new_tags):
    for tag in new_tags:
      if tag in self.tags:
        pass
      else:
        self.tags.append(tag)
    self.put()

def find_sysadmin_by_user(goo_user):
  query = Sysadmin.gql("WHERE goo_user = :goo_user", goo_user=goo_user)
  result = query.fetch(1)
  if len(result) > 0:
    return result[0]
  return None

def create_first_time_sysadmin(goo_user):
  existing_admin = find_sysadmin_by_user(goo_user)
  if not existing_admin:
    new_admin = Sysadmin(goo_user = goo_user)
    new_admin.put()
    new_admin.new_hash()
    return new_admin
  return None

def find_sysadmin_by_id(id_hash):
  query = Sysadmin.gql("Where hash = :hash", hash = id_hash)
  result = query.fetch(1)
  if len(result) > 0:
    return result[0]
  return None
