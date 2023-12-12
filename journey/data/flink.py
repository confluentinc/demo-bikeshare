from re import sub
from json import loads
from subprocess import Popen, PIPE
from uuid import uuid4

from rich import print

class ConfluentFlinkCLIException(Exception):
    pass

def __remove_excess_whitespace(text: str) -> str:
    text = text.strip()
    text = sub(r'\s+', ' ', text) # remove excess whitespace between words
    text = sub(r'\\n', '', text) # remove newlines
    return text

def _get_query_from_file(filepath:str) -> str:
    with open(filepath) as fh:
        return __remove_excess_whitespace(fh.read())

def _run_confluent_flink_cli_command(command:list) -> dict|list:

    _cmd = ['confluent', 'flink'] + command + ['-o', 'json']
    with Popen(_cmd, stdout=PIPE, stderr=PIPE) as proc:
        out, err = proc.communicate()
        
        if proc.returncode != 0:
            raise ConfluentFlinkCLIException(f'Error running command: {' '.join(_cmd)} - {err.decode()}')
        else:
            if not out:
                raise ConfluentFlinkCLIException(f'Error running command: {' '.join(_cmd)} - no output')
            return loads(out.decode())

def create_compute_pool_if_needed(name:str, environment_id:str, cloud:str, region:str) -> str:
    '''
    Create a compute pool for the given environment id or return the id of an existing compute pool with the given name
    '''
    try:
        output = _run_confluent_flink_cli_command(['compute-pool', 'create', name, '--environment', environment_id, '--cloud', cloud, '--region', region])
        return output['id']
    except ConfluentFlinkCLIException as err:
        if f"You already have a running compute pool named '{name}'"in str(err) or 'no output' in str(err):
            print(f'Compute pool {name} already exists - skipping creation')
            output = _run_confluent_flink_cli_command(['compute-pool', 'list', '--environment', environment_id])
            for pool in output:
                if pool['name'] == name:
                    return pool['id']
        
def create_station_status_tables(environment_id:str, compute_pool_id:str, cluster_name:str, system_id:str, cloud:str, region:str):
    '''
    Create the station status tables 
    '''
    query = _get_query_from_file('flink/create_status_tables.sql')
    online_table = query.replace('$TABLE_NAME', f'{system_id}_station_online')
    query_id = str(uuid4())
    _run_confluent_flink_cli_command(["statement", 'create', query_id, '--sql', f"'{online_table}'", '--compute-pool', compute_pool_id, 
                                      '--database', cluster_name, '--environment', environment_id])
    queries = _run_confluent_flink_cli_command(['statement', 'list', '--environment', environment_id, '--compute-pool', compute_pool_id, '--cloud', cloud, '--region', region])
    for query in queries: 
        if query['name'] == query_id:
            print(query)
            break
