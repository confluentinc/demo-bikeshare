from typer import Typer, Option
from typing_extensions import Annotated

from rich import print

from journey.globals import GLOBALS
from journey.data.source import gbfs
from journey.data.kafka.producer import produce
from journey.data.kafka.utils import create_topic_if_needed
from journey.cli.textual.systems import SystemsTreeApp

bikes_menu = Typer()
produce_menu = Typer()

bikes_menu.add_typer(produce_menu, name="produce")

_system_id_from_label = lambda label: label.split('(')[-1].replace(')', '')

def _systems_tree_controller_dialog():
    systems_tree = SystemsTreeApp(gbfs.systems())
    label = systems_tree.run()
    if label is None:
        print('No system selected - please select a system or provide one with the `--system-id` option and try again')
        exit(1)
        
    system_id = _system_id_from_label(label)
    print(f'You selected {label} - use `--system-id={system_id}` to skip selection and use this station directly in the future')
    return system_id

@bikes_menu.command()
def systems():
    '''
    Show tree of different systems that can be queried
    '''
    systems_tree = SystemsTreeApp(gbfs.systems())
    label = systems_tree.run()
    print(f'You selected {label} - use --system-id={_system_id_from_label(label)} to target this system in other commands')
    
@produce_menu.command()
def station_data(system_id:Annotated[str, Option(help='ID of system to use - use `journey bikeshare systems` to see a list')]=''):
    '''
    Load station data 
    '''
    
    if system_id == '':
        system_id = _systems_tree_controller_dialog()
    
    valid = True
    try:
        stations = gbfs.system_stations(system_id)
    except:
        valid = False
        
    if not valid or stations is None or len(stations) == 0:
        print(f'No stations found in system {system_id} - please try another system')
        exit(1)
        
    print(f'{len(stations)} stations found in system {system_id}')
    
    ## transform stations to match producer's expected format
    stations_by_id = {}
    for station in stations:
        stations_by_id[station['station_id']] = station
    
    topic = f'{system_id}.stations.info'
    create_topic_if_needed(GLOBALS['cc_config'], topic)
    produce(GLOBALS['cc_config'], topic, stations_by_id)
    
@produce_menu.command()
def station_statuses(system_id:Annotated[str, Option(help='ID of system to use - use `journey bikeshare systems` to see a list')]=''):
    '''
    Load station statuses
    '''
    
    if system_id == '':
        system_id = _systems_tree_controller_dialog()
    
    valid = True
    try:
        stations = gbfs.system_stations_statuses(system_id)
    except:
        valid = False
        
    if not valid or stations is None or len(stations) == 0:
        print(f'No stations found in system {system_id} - please try another system')
        exit(1)
  
    ## transform stations to match producer's expected format
    stations_by_id = {}
    for station in stations:
        stations_by_id[station['name']] = station
    
    topic = f'{system_id}.stations.status.raw'
    create_topic_if_needed(GLOBALS['cc_config'], topic)
    produce(GLOBALS['cc_config'], topic, stations_by_id)