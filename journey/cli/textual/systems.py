from textual.app import App, ComposeResult
from textual.widgets import Tree

class SystemsTreeApp(App):
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
            
## uncomment below for debugging with the textual cli ##
# from journey.data.source import gbfs
# app = SystemsTree(gbfs.systems())