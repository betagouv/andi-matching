from behave import fixture
from multiprocessing import Process
import uvicorn
import logging
from webservice import main
from time import sleep

PORT = 5555
HOST = 'localhost'


def run_server():
    uvicorn.run(main.app, port=PORT, host=HOST)


@fixture
def matching_api(context, **kwargs):
    proc = Process(target=run_server, args=(), daemon=True)
    logging.info('Starting server subprocess')
    proc.start()
    sleep(0.5)
    yield
    logging.info('Stopping server subprocess')
    proc.kill()
