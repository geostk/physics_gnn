import os.path as path

"""Values by default for parameters. Any parameters given would
overwrite those"""


defaultconfig = {

    # training parameters
    'epoch': 50,

    # optimizer options
    'optimizer': 'SGD',
    'loss': 'BCE',
    'lr': 0.0001,
    'lr_thr': 1.0,
    'lr_update': 0.95,
    'lr_nbbatch': 50000,

    # printing parameters
    'nbdisplay': 2000,
    'nbstep': 1,

    # ploting parameters
    'zoom': [1, 0.1, 0.01, 0.001, 0.0001],
    'possible_stats': ['loss', 'kernel', 'avg1', 'std1', 'avg0', 'std0'],

    # initialisation parameters
    'modeltype': 'RGCs_FCL',
    'dim': [10, 10],
    'deg': [1, 1],
    'modifdeg': [],

}


def read_local():
    config_dir = path.dirname(path.abspath(__file__))
    local_config_path = path.join(config_dir, 'local.txt')

    with open(local_config_path, 'r') as local_config_file:
        local_config = local_config_file.read().split('\n')

    local_config = [arg_config.split(':')
                    for arg_config in local_config
                    if len(arg_config.strip()) > 0 and  # remove empty lines
                    not (arg_config.startswith('#'))]  # remove comments

    local_arguments = ['datadir', 'netdir', 'stdout']
    local_config = [arg_config for arg_config in local_config
                    if arg_config[0].strip() in local_arguments]

    local_config = {arg_config[0].strip(): arg_config[1].strip()
                    for arg_config in local_config
                    if len(arg_config[1].strip()) > 0}  # delete unspecified arguments

    # stdout can be None
    if 'stdout' in local_config and local_config['stdout'] == 'stdout':
        local_config['stdout'] = None

    return local_config
