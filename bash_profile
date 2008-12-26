#Shell Sink
shopt -s histappend
export SHELL_SINK_COMMAND=~/shellsink_client
export SHELL_SINK_ID=12c1e1fbac8c36c8b310b1f335081c4a
PROMPT_COMMAND="history -a;$SHELL_SINK_COMMAND"
SHELL_SINK_TAGS=
