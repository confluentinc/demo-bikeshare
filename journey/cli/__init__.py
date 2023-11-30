from typer import Typer

from journey.globals import GLOBALS
from journey.cli.bikeshare import bikes_menu

cli = Typer()

cli.add_typer(bikes_menu, name="bikeshare")

@cli.callback()
def callback(confluent_cloud_config_file:str='client.properties'):
    '''
    Demo putting Travel related data (bikes and planes) into Confluent Cloud
    '''
    global GLOBALS
    GLOBALS['cc_config'] = confluent_cloud_config_file


def run():
    cli()