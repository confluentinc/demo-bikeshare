from typer import Typer, Option
from typing_extensions import Annotated
from uvloop import run

from rich import print

from journey.globals import GLOBALS
from journey.data.source import gbfs
from journey.data.kafka.producer import produce, multiple_producer_fanout
from journey.data.kafka.admin import create_topic, serializer_for_schema
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
    _systems_tree_controller_dialog()
    
@produce_menu.command()
def station_data(system_id:Annotated[str, Option(help='ID of system to use - use `journey bikeshare systems` to see a list')]=''):
    '''
    Load station data 
    '''
    
    if system_id == '':
        system_id = _systems_tree_controller_dialog()
    
    valid = True
    try:
        stations = gbfs.system_stations_by_id(system_id)
    except:
        valid = False
        
    if not valid or stations is None or len(stations) == 0:
        print(f'No stations found in system {system_id} - please try another system')
        exit(1)
        
    print(f'{len(stations)} stations found in system {system_id}')
    
    topic = f'{system_id}.station.info'
    create_topic(GLOBALS['cc_config'], topic)
    produce(GLOBALS['cc_config'], topic, stations)
    
@produce_menu.command()
def station_statuses(system_id:Annotated[str, Option(help='ID of system to use - use `journey bikeshare systems` to see a list')]='',
                     produce_forever:Annotated[bool, Option(help='Produce data forever')]=False,
                     fanout_size:Annotated[int, Option(help='Number of producers to fan out to - reduce number if you see errors')]=6):
    '''
    (Continuously) load station statuses
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
    
    print(f'{len(stations)} stations found in system {system_id}')
  
    ## transform stations to match producer's expected format
    stations_by_name = {}
    for station in stations:
        stations_by_name[station['station']['name']] = station
    
    topic = f'{system_id}.station.status.raw'
    seralizer = serializer_for_schema(GLOBALS['sr_config'], 'schemas/station_status_raw.json', topic)
    create_topic(GLOBALS['cc_config'], topic)
    
    while True:
        run(multiple_producer_fanout(GLOBALS['cc_config'], topic, stations_by_name, fanout_size=fanout_size, data_seralizer=seralizer))
        #run(produce(GLOBALS['cc_config'], topic, stations_by_name, data_seralizer=seralizer))
        if not produce_forever:
            break