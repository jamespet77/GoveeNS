"""
Govee Node Server
Copyright (C) 2023 James Bennett

MIT License
"""

import udi_interface
import sys
import rest
import time
import asyncio

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
This is the sensor node class.
It's just a node for storing data, no actions.
'''
class Light(udi_interface.Node):
    id = 'child'
    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV0', 'value': 1, 'uom': 25}
            ]

    def __init__(self, polyglot, parent, address, name, api_address, model):
        super(Light, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.api_address = api_address
        self.model = model

        polyglot.subscribe(polyglot.POLL, self.poll)

    def poll(self, pollType):
        if 'shortPoll' in pollType:
            self.updateState()

    def updateState(self):
        state = rest.query('devices/state', {
            'device': self.api_address,
            'model': self.model
        })

        if state is None:
            LOGGER.error(f'Failed to get state for {self.name}')
            return
        state = state['data']

        powerState = state['properties'][1]['powerState']
        self.setDriver('ST', int(powerState == 'on'), True, True)
        deviceState = state['properties'][0]['online']
        self.setDriver('GV0', int(deviceState != 'false'), True, True)

    def setState(self, state):
        rest.put('devices/control', {
            'device': self.api_address,
            'model': self.model,
            'cmd': {
                'name': 'turn',
                'value': state
            }
        })
        self.updateState()

    def on(self, command):
        self.setState('on')

    def off(self, command):
        self.setState('off')
    
    commands = {'DON': on, 'DOF': off}