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

  def test_new_command_is_detected_when_timestamp_is_newer(self):
    client = StubClient()
    client.new_time = 2
    client.old_time = 1
    self.assertEqual(True, client.has_new_command())

  def test_new_command_is_not_detected_when_timestamp_is_older(self):
    client = StubClient()
    client.new_time = 1
    client.old_time = 2
    self.assertEqual(False, client.has_new_command())

  def test_new_command_is_detected_when_no_previous_timestamp_existed(self):
    client = StubClient()
    client.new_time = 1
    client.old_time = None
    self.assertEqual(True, client.has_new_command())

  def test_nothing_happens_if_no_new_command(self):
    client = StubClient()
    client.new_time = 1
    client.old_time = 2
    client.send_command()
    self.assertEquals(False, client.spawned)

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
    pass

  def latest_from_history(self):
    return "the latest command"

  def history_file_timestamp(self):
    return self.new_time

  def last_recorded_history_timestamp(self):
    return self.old_time

  def record_new_last_recorded_history_timestamp(self, timestamp):
    pass

  def spawn_process(self, func, arg):
    self.spawned = True
  

if __name__ == '__main__':
    unittest.main()
