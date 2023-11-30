from typer import Typer

from journey.globals import GLOBALS

bikes_menu = Typer()
produce_menu = Typer()

bikes_menu.add_typer(produce_menu, name="produce")

@produce_menu.command()
def station_data():
    '''
    Demo putting bike data into Confluent Cloud
    '''
    print(GLOBALS)