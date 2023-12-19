# Bikeshare Demo Reference Arch

## Core App
The core application is build in Python and leverages several key technologies to create the demo. 

### Poetry 
[Poetry](https://python-poetry.org) is the outer layer of the core part, it manages dependancies, environments and provides and entry point into the application.  The configuration for poetry lives in [pyproject.toml](pyproject.toml) and is largely managed by the poetry cli.  For example, if you want to add another dependancy, you'd use the `poetry add` command to do so.  

The exception to this is the `[tool.poetry.scripts]` header, which defines the cli entrypoint.

### CLI
#### Typer
Typer is used for the CLI layer, which largely lives in [`bikeshare/cli/__init__.py`](bikeshare/cli/__init__.py).  This represents the "main" for the different components of the app, and is also the primary configuration layer.  Defaults and static configs are set in this layer as is the primary logic being executed.

#### Rich and Textual
Rich is used to create a *richer* cli.  Textual is used for the more complex parts of the UI.  The textual models can be found in [`bikeshare/cli/textual`](bikeshare/cli/textual)  They are sister projects created by [Textualize](https://textualize.io)

### Data
Data is obviously at the heart of the demo 

#### General Bikeshare Feed Specification (GBFS)
> The General Bikeshare Feed Specification, or GBFS, is an open data standard for shared mobility information, developed through a consensus-based process on GitHub.

We're using GBFS to pull in all the source data live using a handy library that makes this easy. All the integration for this can be found [here](bikeshare/data/gbfs.py) 

#### Confluent Cloud
This demo assumes you're using Confluent Cloud (or later will automate this). It puts a schema in schema registry, automatically creates topics, and pulls config from the format that CC provies.  The config is expected to be in the root directory as `client.properties` by default, but can be configured as a CLI arg.

#### Kafka
The usage of Kafka here is very basic.  We're producing records and simulating those records coming from each station (a'la IOT). The specific way that this is being done is a bit of an anti-pattern (one producer producing one record vs one producer producing many records), so there's some creative async batching to work around this.

On the consumer side, we're just pulling data from one of the downstream topics that is being created/produced to from Flink.

All of the related files for the Kafka integration can be found in [`bikeshare/data/kafka`](bikeshare/data/kafka)

#### Flink
The usage of flink here is also very basic.  We're splitting the raw data stream into online and offline stations and transforming to a simplier subset of the data.  The full set of Flink SQL being used for this can be found in [`flink/branch_stations_by_status.sql`](flink/branch_stations_by_status.sql)

