shopt -s histappend
SHELL_SINK_COMMAND=~/shellsink_client.py
SHELL_SINK_ID=12c1e1fbac8c36c8b310b1f335081c4a
PROMPT_COMMAND='history -a;mylastcommand="$(tail -1 ~/.bash_history)";sinkoutput="$($SHELL_SINK_COMMAND "$SHELL_SINK_ID" "$mylastcommand")"'
