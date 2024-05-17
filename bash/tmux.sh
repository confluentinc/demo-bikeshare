#! /bin/bash

tmux new-session -d -s bikeshare
tmux send-keys 'poetry shell' C-m
sleep 2 # give time for the shell to spawn
tmux send-keys 'bikeshare produce --produce-forever --system-id=NYC' C-m

sleep 5 # let produce start to run to get schema setup

tmux split-window -h

if [ -z "$SKIP_FLINK" ]; then
    cd terraform
    export TF_VAR_run_flink_insert_statements=true
    terraform apply -auto-approve
    cd ..
fi

tmux send-keys 'poetry shell' C-m
sleep 2 # give time for the shell to spawn
tmux send-keys 'bikeshare consume' C-m
tmux select-pane -t 0
tmux attach-session -t bikeshare

