#! /bin/bash

export CONFIG_FILE='client.properties'

# Check if $CONFIG_FILE exists
if [ -e "$CONFIG_FILE" ]; then
    # Display existing configuration information
    echo "An existing configuration ($CONFIG_FILE) has been found: $(grep '^bootstrap\.servers=' $CONFIG_FILE)"

    # Ask the user if they want to use the existing configuration
    read -p "Do you want to use this existing configuration? (y/n): " use_existing

    if [ "$use_existing" == "y" ] || [ "$use_existing" == "Y" ]; then
        echo "Using the existing configuration."
    else
        # Prompt the user to paste the new configuration
        echo "Please paste the new configuration from Confluent Cloud and press Ctrl-D when complete:"
        IFS='' # Set Internal Field Separator to empty to preserve leading and trailing whitespace
        config_text=$(cat)

        # Check if the user entered any text
        if [ -z "$config_text" ]; then
            echo "No input provided. Exiting."
            exit 1
        fi

        # Write the new configuration to $CONFIG_FILE
        echo -e "$config_text" > $CONFIG_FILE

        echo "New configuration successfully written to $CONFIG_FILE."
    fi
else
    # Prompt the user to paste the configuration
    echo "Please paste the configuration from Confluent Cloud and press Ctrl-D when complete:"
    IFS='' # Set Internal Field Separator to empty to preserve leading and trailing whitespace
    config_text=$(cat)

    # Check if the user entered any text
    if [ -z "$config_text" ]; then
        echo "No input provided. Exiting."
        exit 1
    fi

    # Write the configuration to $CONFIG_FILE
    echo -e "$config_text" > $CONFIG_FILE

    echo "Configuration successfully written to $CONFIG_FILE."
fi

# # Accept an argument for the topic name
# if [ "$#" -eq 1 ]; then
#     export TOPIC_NAME="$1"
#     echo "Topic name set to: '$TOPIC_NAME'"
# else
#     export TOPIC_NAME="demo-topic"
#     echo "Topic name set to default: '$TOPIC_NAME'"
# fi

# Build the docker container and run it
docker build -t bikeshare .
docker run -dit -v terraform:/opt/bikeshare/terraform -v .confluent:/root/.confluent --name bikeshare-demo bikeshare sleep infinity
docker exec -it -e "SKIP_FLINK=1" bikeshare-demo bash bash/tmux.sh

