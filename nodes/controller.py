"""
Govee Node Server
Copyright (C) 2023 James Bennett

MIT License
"""

import udi_interface
import sys
import time
from nodes import deviceNode
import rest

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
The SensorPush Gateway node class.
Represents a physical gateway that individual sensors connect to.

Any sensors updated by this gateway are represented as children of this node.
Individually gets the new samples for each sensor attached.

TODO: Add checking for disconnected sensors and gateways
'''

class Controller(udi_interface.Node):
    id = 'ctl'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 25}
            ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []
        
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)
        polyglot.subscribe(self.poly.POLL, self.poll)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop() 


    def createDevices(self):
        devices = rest.get('devices')['data']['devices']

        for device in devices:
            LOGGER.info(f'Adding device {device.__str__()}')
            address = device['device'].lower().replace(':', '')

            node = deviceNode.Light(self.poly, self.address, address, device['deviceName'], device['device'], device['model'])

            self.poly.addNode(node)
            self.wait_for_node_done()


    def poll(self, pollType):
        if 'shortPoll' in pollType:
            # Update devices
            return

        return

    def stop(self):
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':
                nodes[node].setDriver('GV0', 0, True, True)

        self.poly.stop()
