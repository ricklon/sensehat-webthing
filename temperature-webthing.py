
# Examples based on : https://www.raspberrypi.org/magpi/sense-hat-science-temperature/

import logging
from sense_hat import SenseHat
from datetime import datetime
from time import sleep

# Webthing imports
from asyncio import sleep, CancelledError, get_event_loop
from webthing import (Action, Event, MultipleThings, Property, Thing, Value,
                              WebThingServer)
import random
import uuid

# Set up log file
logfile = "temperature-"+str(datetime.now().strftime("%Y%m%d-%H%M"))+".csv"

# Configure log settings and format for CSV
logging.basicConfig(filename=logfile, level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d, %H:%M:%S,')

# Configure sense hat
sh = SenseHat()
prev_h = 0

class TemperatureSensor(Thing):
    """ Temperature Sensor using the SenseHat """
    def __init__(self):
        Thing.__init__(self,
                'Sensehat Temperature Sensor',
                ['TemperatureSensor'],
                'A web connected temperature sensor')

        self.temp = Value(0.0)
        self.add_property(
                Property(self,
                    'temp',
                    self.temp,
                    metadata={
                        '@type': 'number',
                        'label': 'Temperature',
                        'type': 'number',
                        'description': 'The current temperature in F',
                        'unit': 'degree celsius',
                        'readonly': True,
                    }))
        logging.debug('Starting the sensor update loop')
        self.sensor_update_task = get_event_loop().create_task(self.update_level())    

    async def update_level(self):
        try:
            while True:
                await sleep(3)
                new_level = sh.get_temperature()
                logging.info(str(new_level))
                self.temp.notify_of_external_update(new_level)
        except CancelledError:
            # No clean up needed
            pass
    def cancel_update_level_task(self):
        self.sensor_update_task.cancel()
        get_event_loop().run_until_complete(self.sensor_update_task)

def run_server():
    SensorTemperature = TemperatureSensor()
    server = WebThingServer(MultipleThings([SensorTemperature],'Temperature Device'),port=9999)

    try:
        logging.info('starting the sever')
        server.start()
    except KeyboardInterrupt:
        logging.debug('canceling sesor update looping task')
        SensorTemperature.cancel_update_level_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')

if __name__=='__main__':
    run_server()


        
