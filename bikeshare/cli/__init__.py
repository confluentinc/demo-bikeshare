from datetime import datetime
from time import sleep

from typer import Typer, Option
from typing_extensions import Annotated
from uvloop import run as async_run

from rich import print
from rich.status import Status
from rich.table import Table
from rich.live import Live
from rich.text import Text

from bikeshare.globals import GLOBALS
from bikeshare.data.source import gbfs
from bikeshare.data.kafka.consumer import consume as _consume
from bikeshare.data.kafka.producer import multiple_producer_fanout
from bikeshare.data.kafka.admin import create_topic, serializer_for_json_schema, deserializer_for_flink_avro_schema
from bikeshare.data.kafka.utils import cc_config, sr_config
from bikeshare.cli.textual.systems import SystemsTreeApp

cli = Typer()

_system_id_from_label = lambda label: label.split('(')[-1].replace(')', '')

def _color_station_table(row):
    if row['availability_ratio'] >= GLOBALS['station_availability_high']:
        color = GLOBALS['station_availability_color']['high']
    elif row['availability_ratio'] <= GLOBALS['station_availability_low']:
        color = GLOBALS['station_availability_color']['low']
    else:
        color = GLOBALS['station_availability_color']['medium']
        
    _row = {}
    for k, v in row.items():
        text = Text(str(v))
        text.stylize(color)
        _row[k] = text
        
    return _row
        
        

def _stations_table(headers, data, sort_by:str='last_updated', desc:bool=True, hidden_fields:list|None=None, colorer:callable=None):
    hidden_fields = hidden_fields or [] # collection types as defaults cause weird errors as they're mutable and persistent across calls
    colorer = colorer or (lambda x: {k:str(v) for k, v in x.items()}) # default to no color and ensure string
    _data = [v for v in data.values()]
    sorted_data = sorted(_data, key=lambda x: x[sort_by], reverse=desc)
    table = Table(*headers, show_header=True)
    
    for row in sorted_data:
        row = colorer(row)
        table.add_row(*[v for k, v in row.items() if k not in hidden_fields])
    
    return table
    
def _systems_tree_controller_dialog() -> str:
    systems_tree = SystemsTreeApp(gbfs.systems())
    label = systems_tree.run()
    if label is None:
        print('No system selected - please select a system or provide one with the `--system-id` option and try again')
        exit(1)
        
    system_id = _system_id_from_label(label)
    print(f'You selected {label} - use `--system-id={system_id}` to skip selection and use this station directly in the future')
    return system_id

        
def _stations_data_by_name(system_id:str) -> (dict, int):
    valid = True
    try:
        stations = gbfs.system_stations_statuses(system_id)
    except:
        valid = False
        
    if not valid or stations is None or len(stations) == 0:
        print(f'No stations found in system {system_id} - please try another system')
        exit(1)
    
    print(f'{len(stations)} stations found in system {system_id}')
  
    ## transform stations to match producer's expected format
    stations_by_name = {}
    ttl = -1
    for station in stations:
        ttl = station['ttl']
        stations_by_name[station['station']['name']] = station
        
    return stations_by_name, ttl

@cli.command()
def systems():
    '''
    Show tree of different systems that can be queried
    '''
    _systems_tree_controller_dialog()
    
@cli.command()
def produce(system_id:Annotated[str, Option(help='ID of system to use - use `journey bikeshare systems` to see a list')]='',
            produce_forever:Annotated[bool, Option(help='Produce data forever')]=False,
            fanout_size:Annotated[int, Option(help='Number of producers to fan out to - reduce number if you see errors - increase to improve performance')]=6,
            topic:Annotated[str, Option(help='Topic to produce to')]='station_status'):
    '''
    (Continuously) load station statuses
    '''
    
    if system_id == '':
        system_id = _systems_tree_controller_dialog()
    
    stations_by_name, ttl = _stations_data_by_name(system_id)
    
    seralizer = serializer_for_json_schema(GLOBALS['sr_config'], 'schemas/station_status.json', topic)
    create_topic(GLOBALS['cc_config'], topic)
    
    while True:
        start = datetime.now()
        async_run(multiple_producer_fanout(GLOBALS['cc_config'], topic, stations_by_name, fanout_size=fanout_size, data_seralizer=seralizer))
        if produce_forever:
            ## check to see if a full minute has elapsed - if not, wait until it has
            time_spent = (datetime.now() - start).total_seconds()
            if time_spent < ttl:
                time_needed = int(ttl - time_spent)
                with Status(f'Waiting {time_needed} seconds before next produce', spinner='dqpb'):
                    sleep(time_needed)
            
            ## get the a fresh batch of data and do it again!
            stations_by_name, ttl = _stations_data_by_name(system_id)
        else:
            break

@cli.command()
def consume(consumer_id:Annotated[str, Option(help='ID for consumer to use')]='live-updates-consumer',
            poll_interval:Annotated[int, Option(help='Poll interval in seconds')]=1,
            topic:Annotated[str, Option(help='Topic to consume from')]='station_online', 
            debug:Annotated[bool, Option(help='Show debug messages')]=False,
            hidden_fields:Annotated[str, Option(help='Comma delimited list of fields to hide from output')]='id,availability_ratio,last_updated,ttl,received_at'):
    '''
    Show online stations
    '''
    deserializer = deserializer_for_flink_avro_schema(GLOBALS['sr_config'], f'schemas/{topic}.avsc')
    first_message = None
    data = {}
    hidden_fields = hidden_fields.split(',') if hidden_fields else []
    
    with Status(f'Waiting for messages from topic {topic}', spinner='pong'):
        while first_message is None:
            for message in _consume(GLOBALS['cc_config'], topic, deserializer, consumer_id, poll_interval):
                if debug:
                    print(f'message: {message}')
                if message is not None:
                    message['received_at'] = int(datetime.now().timestamp())
                    first_message = message
                    break
    
    data[first_message['id']] = first_message
    headers = [key for key in first_message.keys() if key not in hidden_fields]
    
    with Live(_stations_table(headers, data, sort_by='received_at', hidden_fields=hidden_fields, colorer=_color_station_table), auto_refresh=False) as live:
        for message in _consume(GLOBALS['cc_config'], topic, deserializer, consumer_id, poll_interval):
            if debug:
                live.console.print(f'message: {message}')
            if message is not None:
                message['received_at'] = int(datetime.now().timestamp())
                data[message['id']] = message
                live.update(_stations_table(headers, data, sort_by='received_at', hidden_fields=hidden_fields, colorer=_color_station_table), refresh=True)

@cli.callback()
def global_callback(confluent_cloud_config_file:str='client.properties'):
    '''
    Function gets ran before command, used for setting up global state
    or other settings that are global that are needed for downstream tasks
    '''
    global GLOBALS
    GLOBALS['cc_config'] = cc_config(confluent_cloud_config_file)
    GLOBALS['sr_config'] = sr_config(confluent_cloud_config_file)

def run():
    cli()
    
