from typer import Typer

from journey.globals import GLOBALS
from journey.cli.bikeshare import bikes_menu
from journey.data.kafka.utils import cc_config, sr_config

cli = Typer()

cli.add_typer(bikes_menu, name="bikeshare")

@cli.callback()
def callback(confluent_cloud_config_file:str='client.properties'):
    '''
    Demo putting Travel related data (bikes and planes) into Confluent Cloud
    '''
    global GLOBALS
    GLOBALS['cc_config'] = cc_config(confluent_cloud_config_file)
    GLOBALS['sr_config'] = sr_config(confluent_cloud_config_file)

def run():
    cli()