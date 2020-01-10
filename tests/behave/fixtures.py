import logging
from time import sleep
from multiprocessing import Process
import uvicorn
from behave import fixture
from webservice import main

PORT = 5555
HOST = 'localhost'


def run_server():
    uvicorn.run(main.app, port=PORT, host=HOST)


@fixture
def matching_api(_context, **kwargs):
    proc = Process(target=run_server, args=(), daemon=True)
    logging.info('Starting server subprocess')
    proc.start()
    sleep(0.5)
    yield
    logging.info('Stopping server subprocess')
    proc.kill()
