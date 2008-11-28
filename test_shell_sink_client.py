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



class StubClient(Client):

  def __init__(self):
    pass

  def set_environment(self, env_hash):
    self.env_hash = env_hash

  def environment(self):
    return self.env_hash
  

if __name__ == '__main__':
    unittest.main()
