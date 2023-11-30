from typer import Typer

from textual.app import App, ComposeResult
from textual.widgets import Tree

from journey.globals import GLOBALS
from journey.source import gbfs

bikes_menu = Typer()
produce_menu = Typer()

bikes_menu.add_typer(produce_menu, name="produce")

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
                state_node.add_leaf(f'{system["Location"]} - {system["Name"]}')
                
        yield tree
        
        
@bikes_menu.command()
def systems():
    '''
    Get list of different systems that can be queried
    '''
    tree = SystemsTree(gbfs.systems())
    tree.run()    

@produce_menu.command()
def station_data():
    '''
    Demo putting bike data into Confluent Cloud
    '''
    print(GLOBALS)