#! /bin/bash

tmux new-session -d -s bikeshare
tmux send-keys 'poetry shell' C-m
sleep 2 # give time for the shell to spawn
tmux send-keys 'bikeshare produce --produce-forever --system-id=NYC' C-m

sleep 5 # let produce start to run to get schema setup

tmux split-window -h

if [ -z "$SKIP_FLINK"]; then
    cd terraform
    
    export CC_ENV=$(terraform output -json | jq -r .environment.value.id)
    export KAFKA_CLUSTER=$(terraform output -json | jq -r .kafka_cluster.value.display_name)
    export FLINK_POOL=$(terraform output -json | jq -r .flink_pool.value.id)

    cd ..
    
    confluent environment use $CC_ENV
    confluent flink statement create --compute-pool $FLINK_POOL --database $KAFKA_CLUSTER --sql "$(cat flink/branch_stations_by_status/branch_online.sql | tr -d '\n' | xargs)"
    confluent flink statement create --compute-pool $FLINK_POOL --database $KAFKA_CLUSTER --sql "$(cat flink/branch_stations_by_status/branch_offline.sql | tr -d '\n' | xargs)"
fi

tmux send-keys 'poetry shell' C-m
sleep 2 # give time for the shell to spawn
tmux send-keys 'bikeshare consume' C-m
tmux select-pane -t 0
tmux attach-session -t bikeshare

