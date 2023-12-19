from rich import print
from textual.app import App, ComposeResult
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

class SystemsTreeApp(App):
    def __init__(self, systems:dict):
        super().__init__()
        self.systems = systems
        
    def _recurse_systems(self, node:TreeNode, data:dict|list) -> Tree:
        if isinstance(data, dict):
            keys = sorted(data.keys())
            for k in keys:
                v = data[k]
                if isinstance(v, dict):
                    child = node.add(k)
                    self._recurse_systems(child, v)
                elif isinstance(v, list):
                    sorted_v = sorted(v, key=lambda x: x['Location'])
                    child = node.add(k)
                    for item in sorted_v:
                        child.add_leaf(f'{item["Location"]} - {item["Name"]} ({item["System ID"]})')
        else:
            for item in data:
                node.add_leaf(item)
    
    def compose(self) -> ComposeResult:
        tree: Tree[dict] = Tree("World")
        tree.root.expand()
        continents = sorted(self.systems.keys())
        for continent in continents:
            continent_node = tree.root.add(continent)
            self._recurse_systems(continent_node, self.systems[continent])

        yield tree
        
    def on_tree_node_selected(self, event):
        label = str(event.node.label)
        if '(' in label:
            self.exit(label)
            
# uncomment below for debugging with the textual cli ##
# from bikeshare.data import gbfs
# app = SystemsTreeApp(gbfs.systems())
# app.run()