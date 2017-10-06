# -*- coding: utf-8 -*-
import yaml


### CONFIGURATION ###
config_file = path.join(path.dirname(path.realpath(__file__)), 'config/config.yml')
if path.exists(config_file):
    config = yaml.load(open(config_file, 'r'))
else:
    print config_file + ' not found'
    exit()

release = config['releases']


if __name__ == '__main__':
    #TODO GET THE RELEASE DATE OF EACH issue
    #TODO
