#! /bin/bash

tmux new-session -d -s bikeshare
tmux send-keys 'poetry shell' C-m
sleep 2 # give time for the shell to spawn
tmux send-keys 'bikeshare produce --produce-forever' C-m
tmux split-window -h
tmux send-keys 'poetry shell' C-m
sleep 2 # give time for the shell to spawn
tmux send-keys 'bikeshare consume' C-m
tmux select-pane -t 0
tmux attach-session -t bikeshare

