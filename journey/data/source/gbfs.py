from datetime import datetime

from rich import print
from gbfs.services import SystemDiscoveryService

ds = SystemDiscoveryService()

def systems():
    _systems = ds.systems
    
    us_systems = {}
    for system in _systems:
        
        ## filter out systems that don't have stations and isolate to US for now
        if (system['Country Code'] == 'US'
            and ' ' not in system['System ID'] 
            and 'bird' not in system['System ID']
            and 'Link' not in system['System ID']
            and 'lime' not in system['System ID']
            and 'revel' not in system['System ID']
            and not system['System ID'].isnumeric()
            and not system['System ID'].startswith('9')):
            try:
                system['Location'] = system['Location'].replace(', US', '')
                _, state = system['Location'].split(',')
            except ValueError:
                if  system['Location'].endswith('NS'):
                    # filter out bad systems/locations
                    continue
                print(system)
                raise
            
            us_systems.setdefault(state.strip(), []).append(system)
      
    return us_systems


def system_detail(system_id):
    return ds.get_system_by_id(system_id)

def system_feeds(system_id):
    client = ds.instantiate_client(system_id)
    return client.feed_names

def system_feed_detail(system_id, feed_name):
    client = ds.instantiate_client(system_id)
    if client is None:
        return None

    return client.request_feed(feed_name)

def system_stations(system_id):
    client = ds.instantiate_client(system_id)
    if client is None:
        return None

    data = client.request_feed('station_information').get('data').get('stations')
    return data

def system_stations_by_id(system_id):
    stations = system_stations(system_id)
    stations_by_id = {}
    for station in stations:
        stations_by_id[station['station_id']] = station
    return stations_by_id

def system_stations_statuses(system_id):
    client = ds.instantiate_client(system_id)
    if client is None:
        return None

    feed = client.request_feed('station_status')
    _stations = feed.get('data').get('stations')
    metadata = system_stations_by_id(system_id)
    
    ## get global properties
    last_updated:datetime = feed.get('last_updated')
    ttl = feed.get('ttl')
    version = feed.get('version')
    stations = []
    
    for _station in _stations:
        ## add global properties to each data entry as they're going to be split up
        station = {}
        station['last_updated'] = last_updated.timestamp()
        station['ttl'] = ttl 
        station['version'] = version
        
        # enrich with basic metadata
        _station.update(metadata.get(_station['station_id']))
        for k, v in _station.items():
            
            # data comes back as ints but need to convert to bool
            if k.startswith('is_'):
                _station[k] = bool(v)
        
        # print(_station)
        # import pdb; pdb.set_trace()
        station['station'] = _station
        
        stations.append(station)

    # print(_stations)    
    # import pdb; pdb.set_trace()
    
    return stations



def system_station_information(system_id, station_id):
    client = ds.instantiate_client(system_id)
    if client is None:
        return None

    feed = client.request_feed('station_status')
    items = feed.get('data').get('stations')

    try:
        result = next(filter(lambda x: str(x.get('station_id')) == station_id, items))
    except StopIteration:
        return None

    result.update({'last_updated': feed.get('last_updated'), 'ttl': feed.get('ttl')})
    return result



def system_station_detail(system_id, station_id):
    client = ds.instantiate_client(system_id)
    if client is None:
        return None

    station_feed = client.request_feed('station_information')
    status_feed = client.request_feed('station_status')

    all_stations = station_feed.get('data').get('stations')
    all_statuses = status_feed.get('data').get('stations')

    try:
        station = next(filter(lambda x: str(x.get('station_id')) == station_id, all_stations))
        id_join = str(station.get('station_id'))
        status = next(filter(lambda x: str(x.get('station_id')) == id_join, all_statuses))
    except StopIteration:
        return None

    result = {'last_updated': status_feed.get('last_updated'), 'ttl': status_feed.get('ttl')}
    result.update(station)
    result.update(status)

    return result


if __name__ == '__main__':
    import pdb; pdb.set_trace()
