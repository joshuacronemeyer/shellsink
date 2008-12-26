#Shell Sink
shopt -s histappend
export SHELL_SINK_COMMAND=shellsink_client
export SHELL_SINK_ID=your-hex-id
PROMPT_COMMAND="history -a;$SHELL_SINK_COMMAND"
export SHELL_SINK_TAGS=
