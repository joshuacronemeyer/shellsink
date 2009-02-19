import unittest
from shellsink_client import *
from mock import Mock
import os

class TestShellSinkClient(unittest.TestCase):

  def test_home_env_variable_required(self):
    os.environ = {'SHELL_SINK_ID' : None}
    self.assertRaises(Exception, verify_environment)

  def test_id_env_variable_required(self):
    os.environ = {'HOME' : None}
    self.assertRaises(Exception, verify_environment)

  def test_url_of_send_command_is_correct(self):
    client = StubClient()
    url_hash = {'id': "1234", 'url': "http://history.shellsink.com/addCommand?"}
    client.id, client.URL = url_hash['id'], url_hash['url']
    correct_url = "%(url)scommand=the+latest+command&hash=%(id)s" % url_hash
    self.assertEqual(client.url_with_send_command(), correct_url)

  def test_url_of_send_tag_is_correct(self):
    client = StubClient()
    correct_url = "http://history.shellsink.com/addTag?tag=abc&command=1234"
    self.assertEqual(client.url_with_send_tag('abc', '1234'), correct_url)

  def test_nothing_happens_if_no_new_command(self):
    client = StubClient()
    mock = Mock()
    def has_new_command():
      return False
    mock.has_new_command = has_new_command
    client.history = mock
    client.send_command()
    self.assertEquals(False, client.spawned)
  
  def test_http_process_spawned_if_new_command(self):
    client = StubClient()
    mock = Mock()
    def has_new_command():
      return True
    mock.has_new_command = has_new_command
    client.history = mock
    client.send_command()
    self.assertEquals(True, client.spawned)

  def test_get_tag_returns_none_when_there_is_no_tag(self):
    opts = [("-p",None)]
    self.assertEquals(None, get_tag(opts))
    
  def test_get_tag_returns_tag_when_there_is_a_tag(self):
    opts = [("-p",None),("-t","mytag")]
    self.assertEquals("mytag", get_tag(opts))
    opts = [("-p",None),("--tag","mytag")]
    self.assertEquals("mytag", get_tag(opts))

  def test_get_keyword_returns_none_when_there_is_no_keyword(self):
    opts = [("-p",None)]
    self.assertEquals(None, get_keyword(opts))
    
  def test_get_tag_returns_keyword_when_there_is_a_keyword(self):
    opts = [("-p",None),("-k","mykeyword")]
    self.assertEquals("mykeyword", get_keyword(opts))
    opts = [("-p",None),("--keyword","mykeyword")]
    self.assertEquals("mykeyword", get_keyword(opts))

class StubClient(Client):

  def __init__(self):
    self.spawned = False
    self.tags = []
    mock = Mock()
    def latest():
      return "the latest command"
    mock.latest = latest
    self.history = mock
    pass
  
  def spawn_process(self, func, arg):
    self.spawned = True

  def async_sending_of_command_and_tags(self):
    pass
  

if __name__ == '__main__':
    unittest.main()
