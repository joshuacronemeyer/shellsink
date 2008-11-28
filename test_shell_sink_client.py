import unittest
from shellsink_client import Client
from mock import Mock
class TestShellSinkClient(unittest.TestCase):

  def test_home_env_variable_required(self):
    client = StubClient()
    client.set_environment({'SHELL_SINK_ID' : None})
    self.assertRaises(Exception, client.verify_environment)

  def test_id_env_variable_required(self):
    client = StubClient()
    client.set_environment({'HOME' : None})
    self.assertRaises(Exception, client.verify_environment)

  def test_url_is_correct(self):
    client = StubClient()
    url_hash = {'id': "1234", 'url': "http://localhost:8080/history/add?"}
    client.id, client.URL = url_hash['id'], url_hash['url']
    correct_url = "%(url)scommand=the+latest+command&hash=%(id)s" % url_hash
    self.assertEqual(client.url_with_command(), correct_url)

class StubClient(Client):

  def __init__(self):
    pass

  def set_environment(self, env_hash):
    self.env_hash = env_hash

  def environment(self):
    return self.env_hash

  def latest_from_history(self):
    return "the latest command"
  

if __name__ == '__main__':
    unittest.main()
