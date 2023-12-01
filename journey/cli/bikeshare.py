from typer import Typer, Option
from typing_extensions import Annotated

from rich import print
from textual.app import App, ComposeResult
from textual.widgets import Tree

from journey.globals import GLOBALS
from journey.source import gbfs

bikes_menu = Typer()
produce_menu = Typer()

bikes_menu.add_typer(produce_menu, name="produce")

_system_id_from_label = lambda label: label.split('(')[-1].replace(')', '')

class SystemsTree(App):
    def __init__(self, systems:dict):
        super().__init__()
        self.systems = systems
    
    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("US")
        tree.root.expand()
        states = sorted(self.systems.keys())
        for state in states:
            state_node = tree.root.add(state)
            systems = sorted(self.systems[state], key=lambda x: x['Location'])
            for system in systems:
                state_node.add_leaf(f'{system["Location"]} - {system["Name"]} ({system["System ID"]})')
                
        yield tree
        
    def on_tree_node_selected(self, event):
        label = str(event.node.label)
        if '(' in label:
            self.exit(label)
    

@bikes_menu.command()
def systems():
    '''
    Show tree of different systems that can be queried
    '''
    systems_tree = SystemsTree(gbfs.systems())
    label = systems_tree.run()
    print(f'You selected {label} - use --system-id={_system_id_from_label(label)} to query this system in other commands')
    
@produce_menu.command()
def station_data(system_id:Annotated[str, Option(help='ID of system to use - use `journey bikeshare systems` to see a list')]=''):
    '''
    Load station data 
    '''
    
    if system_id == '':
        systems_tree = SystemsTree(gbfs.systems())
        label = systems_tree.run()
        if label is None:
            print('No system selected - please select a system or provide one with the --system-id option and try again')
            exit(1)
            
        system_id = _system_id_from_label(label)
        print(f'You selected {label} - use `--system-id={system_id}` to query this directly in the future')
    
    valid = True
    try:
        stations = gbfs.system_stations(system_id)
    except:
        valid = False
        
    if not valid or stations is None or len(stations) == 0:
        print(f'No stations found in system {system_id} - please try another system')
        exit(1)
        
    print(f'{len(stations)} stations found in system {system_id}')
    