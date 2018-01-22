#!/usr/bin/env python

import click
import logging
import sys
import signal
import application

@click.command()
@click.option('--port', help='Application port', default= 8183)
@click.option('--debug', help='Debug mode', default= False)
def server(port, debug):

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stderr))

    if debug:
	logging.basicConfig(level=logging.DEBUG)
	logging.getLogger('flask_ask').setLevel(logging.DEBUG)
	logger.setLevel(logging.DEBUG)

    app = application.create(logger= logger)
    app.run('0.0.0.0', port, debug=False)

def exit_gracefully(a, b):
    print('Exiting...')
    sys.stdout.flush()
    
if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    server(auto_envvar_prefix='DAIKIN')
