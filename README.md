## Prerequisites
- [Docker](https://www.docker.com/get-started/)
- [Confluent Cloud Account](https://confluent.cloud)

## Setup
0. On the [Confluent Cloud home page](https://confluent.cloud/home), click `Add Cloud Environment` on the right side.
   1. Give the environment a name
   2. Select a Stream Governance package (Essentials is fine)
   3. Select an AWS region
      1. The region selected has to have Flink enabled in it.  You can run `confluent flink region list` to see the current list of available regions.
0.  click `Create cluster on my own`
    1. Select either a Basic or Standard plan
    2. Select AWS as the cloud and pick the same region you selected in the environment configuration
    3. With a trial, you can choose to skip payment. 
    4. Give the cluster a name if you want (the default is fine), and click `Launch cluster`
    5. On the success screen, click `Get started` under `Setup Client`
0. This takes you into the `New client` dialog
    1. Select Python as the language
    2. Click create on both the `Kafka API Key` and `Schema Registry API Key`, this automatically fills it into the properties file snippet to the right
    3. Copy the snippet provided and save it for later
0. Return to the Environment page by clicking the name of the environment at the top left of the page. 
   1. Click the Flink tab and then click `Create Compute Pool`
   2. Select the AWS region that was used in previous steps
   3. Give it a name and click through the rest of the dialog
   4. Once it's finished provisioning, click `Open SQL Workspace` 
   5. Open the [table DDLs](flink/station_status_tables.sql) and copy paste them into the window
      1. Make sure you select the environment (catalog) and cluster (database) that you created previously
      2. Keep this window open, you'll need it again in a later step.
1. Run `./up.sh` - it will prompt you to paste the snippet you saved from before
   1. This will build a container and then run a [tmux](https://www.themoderncoder.com/uploads/simple-tmux-cheatsheet.jpg) window inside of it. 
   2. On the left side is the producer part of the demo, which will prompt you to select a location to pull data from
      1. As of writing, this has been most tested on Citibike (North America > US > NY > NYC), not all locations have data, but we've tried to remove most of the ones that don't work
      2. TODO: You can set an environment variable to bypass the city selections
   3. On the right side is the consumer, which will wait until data is produced into the topics created in the next step
2. Once the producer is running, you can now setup the Flink Parts
   1. Using the [Transformation SQL](flink/branch_stations_by_status.sql) provided, copy paste that into the `SQL Workspace` window that was opened earlier
3. Once that's executed successfully, you can return to the tmux page which will eventually start to populate data into a table showing the status of the various 
   1. This can take a few minutes for the data to start appearing