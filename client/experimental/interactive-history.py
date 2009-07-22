#Playing with being able to have a more interactive way to browse the history...
#Works different in different terminals. Don't think this will pan out.
import os
import sys
import tty
import termios

def getch():
  stdin_fd = sys.stdin.fileno()
  old_term_settings = termios.tcgetattr(stdin_fd)
  try:
    tty.setraw(sys.stdin.fileno())
    term_character = sys.stdin.read(1)
  finally:
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_term_settings)
  return term_character

def history():
  history_file = os.environ['HOME'] + "/.bash_history"
  commands = []
  try:
    file = open(history_file, "r")
    commands = file.readlines()
  finally:
    file.close()
  commands.reverse()
  return commands

def term_width():
  return int(os.system("tput cols"))

commands = history()
command_index = 0
overwrite = 0

def user_message():
  return "Command to tag: %s" % commands[command_index].strip()

input = " "

while input != 13:
  message = user_message() + " "*overwrite
  message = message[0:term_width()] + "\t"
  sys.stdout.write(message)
  sys.stdout.flush()
  overwrite = len(message)

  input = ord(getch())
  if input == 65:
    command_index -= 1
  if input == 66:
    command_index += 1

print commands[command_index]
