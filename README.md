## Prerequisites
- [Docker](https://www.docker.com/get-started/)
- [Confluent Cloud Account](https://confluent.cloud)

## Setup
0. On the [Confluent Cloud home page](https://confluent.cloud/home), click `Create a Cluster`
    1. Select either a Basic or Standard plan, and select a Cloud and Region of your choice
    1. With a trial, you can choose to skip payment. 
    1. Give the cluster a name if you want (the default is fine), and click `Launch cluster`
    1. On the success screen, click `Get started` under `Build an event driven application`
0. This takes you into the `New client` dialog
    1. Select Python as the language
    1. Click create on both the `Kafka API Key` and `Schema Registry API Key`, this automatically fills it into the properties file snippet to the right
    1. Copy the snippet provided 
0. Run `./up.sh` - it will prompt you to paste the snippet
    1. You can optionally add a topic name `./up.sh topic-name`
