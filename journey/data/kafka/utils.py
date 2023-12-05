SCHEMA_REGISTRY_CONFIG_FIELDS = set(['schema.registry.url', 'basic.auth.credentials.source', 'basic.auth.user.info'])

def _read_config_file(config_file, schema_registry=False):
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                ## remove schema registry params from config as it causes an error later or only return those params
                if schema_registry:
                    if parameter in SCHEMA_REGISTRY_CONFIG_FIELDS:
                        conf[parameter] = value.strip()
                else:
                    if parameter not in SCHEMA_REGISTRY_CONFIG_FIELDS:
                        conf[parameter] = value.strip()
    return conf

def cc_config(config_file):
    return _read_config_file(config_file, schema_registry=False)

def sr_config(config_file):
    config = _read_config_file(config_file, schema_registry=True)
    # import pdb; pdb.set_trace()
    config.pop('basic.auth.credentials.source') # I guess nothing uses this?
    url = config.pop('schema.registry.url')
    config['url'] = url # because the `SchemaRegistryClient` expects `url` instead of `schema.registry.url`
    return config

def filter_timeout_property(config):
    _config = config.copy()
    _config.pop('session.timeout.ms') # remove session timeout as it causes an annoying warning
    return _config

