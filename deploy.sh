#! /bin/bash -e

BIKESHARE_SLEEP_TIME="${BIKESHARE_SLEEP_TIME:-10800}" ## default to 3 hours

if [ -z "$BIKESHARE_FORCE_DOCKER_REBUILD" ]; then
    docker build -t bikeshare . 
else
    docker build --no-cache -t bikeshare . 
fi

if ! [ -z "$BIKESHARE_RUN_FOREVER" ]; then
    docker run -dit -v $PWD/terraform:/opt/bikeshare/terraform -v $PWD/.confluent:/root/.confluent --name bikeshare-demo bikeshare sleep $BIKESHARE_SLEEP_TIME
else
    docker run -dit -v $PWD/terraform:/opt/bikeshare/terraform -v $PWD/.confluent:/root/.confluent --name bikeshare-demo bikeshare sleep infinity
fi

if [ -z "$CC_API_KEY" ] || [ -z "$CC_API_SECRET" ]; then
    docker exec -it bikeshare-demo /bin/bash bash/provision.sh
else
    docker exec -it -e "TF_VAR_cc_api_key=$CC_API_KEY" -e "TF_VAR_cc_api_secret=$CC_API_SECRET" bikeshare-demo /bin/bash -ex bash/provision.sh
fi

docker exec -it bikeshare-demo /bin/bash bash/tmux.sh
