## Prerequisites
- [Docker](https://www.docker.com/get-started/)
- [Confluent Cloud Account](https://confluent.cloud)

## Running the Demo
There are two ways to run the demo: the easy way, and the hard way. The easy way uses terraform to provision the Confluent Cloud setup, and will drop you directly into the demo.  This version requires a [Confluent Cloud API Key](https://confluent.cloud/settings/api-keys).  You can jump to the instructions for this version [here](README.md#the-easy-way)

The Hard Way of running the demo mainly exists as an educational tool to explain what's going on at a lower level.  Feel free to take that approach [here](README.md#the-hard-way).

### The Easy Way
1. Go to the [Cloud API keys page](https://confluent.cloud/settings/api-keys) page of Confluent Cloud and create a new key pair.  Alternatively, if you already have one saved, have it handy for the next step.
2. Set the keypair to the env vars `CC_API_KEY` and `CC_API_SECRET` and run `./deploy.sh` inside the repo folder.  You may also provide them when prompted.
   1. The script runs the container as a background task and then executes other commands against it.  This means that exiting out of the demo doesn't actually turn off the container.  It has a timer for 3 hours by default.  You can either set `export BIKESHARE_RUN_FOREVER=1` to have it run until the computer next restarts, or change the time by setting `export BIKESHARE_SLEEP_TIME=desired time in seconds`
   2. 

### The Hard Way
1. On the [Confluent Cloud home page](https://confluent.cloud/home), click `Add Cloud Environment` on the right side.
   1. Give the environment a name
   2. Select a Stream Governance package (Essentials is fine)
   3. Select an AWS region
      1. The region selected has to have Flink enabled in it.  You can run `confluent flink region list` to see the current list of available regions.
1.  click `Create cluster on my own`
    1. Select either a Basic or Standard plan
    2. Select AWS as the cloud and pick the same region you selected in the environment configuration
    3. With a trial, you can choose to skip payment. 
    4. Give the cluster a name if you want (the default is fine), and click `Launch cluster`
    5. On the success screen, click `Get started` under `Setup Client`
1. This takes you into the `New client` dialog
    1. Select Python as the language
    2. Click create on both the `Kafka API Key` and `Schema Registry API Key`, this automatically fills it into the properties file snippet to the right
    3. Copy the snippet provided and save it for later
1. Return to the Environment page by clicking the name of the environment at the top left of the page. 
   1. Click the Flink tab and then click `Create Compute Pool`
   2. Select the AWS region that was used in previous steps
   3. Give it a name and click through the rest of the dialog
   4. Once it's finished provisioning, click `Open SQL Workspace` 
   5. Open the [table DDLs](flink/station_status_tables.sql) and copy paste them into the window
      1. Make sure you select the environment (catalog) and cluster (database) that you created previously
      2. Keep this window open, you'll need it again in a later step.
1. Run `./run.sh` - it will prompt you to paste the snippet you saved from before
   1. This will build a container and then run a tmux window inside of it. 
      1. tmux has a special set of hotkey commands to navigate it, click [here](https://www.themoderncoder.com/uploads/simple-tmux-cheatsheet.jpg) if you're not familiar with its interface.
   2. On the left side is the producer part of the demo, which will prompt you to select a location to pull data from
      1. As of writing, this has been most tested on Citibike (North America > US > NY > NYC), not all locations have data, but we've tried to remove most of the ones that don't work
      2. TODO: You can set an environment variable to bypass the city selections
   3. On the right side is the consumer, which will wait until data is produced into the topics created in the next step
2. Once the producer is running, you can now setup the Flink Parts
   1. Using the [Transformation SQL](flink/branch_stations_by_status.sql) provided, copy paste that into the `SQL Workspace` window that was opened earlier
3. Once that's executed successfully, you can return to the tmux page which will eventually start to populate data into a table showing the status of the various 
   1. This can take a few minutes for the data to start appearing

## Development Settings
- `BIKESHARE_FORCE_DOCKER_REBUILD=1` will force the container to rebuild when running `run.sh` or `deploy.sh` which is helpful if it seems like a cached version of the container is being ran.  Can remove with `unset BIKESHARE_FORCE_DOCKER_REBUILD`.
- `SKIP_FLINK=1` will skip the Flink `INSERT` statements from being ran as a part of the [bash/tmux.sh](bash/tmux.sh) script.
