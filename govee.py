"""
Govee Node Server
Copyright (C) 2023 James Bennett

MIT License
"""

'''
TODO - Add more comments
'''

import udi_interface
import sys
from nodes import controller
import rest
import time

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

n_queue = []
mainNode = None

def node_queue(data):
    if data['address'] not in n_queue:
        n_queue.append(data['address'])


def wait_for_node_done():
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop() 


'''
Main function for generating nodes at beginning of server
'''

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')
        
        mainNode = None
        def parameterHandler(params):
            global mainNode
            Parameters.load(params)

            if 'API Key' in Parameters:
                key = Parameters['API Key']

                if key != '':
                    polyglot.Notices.clear()
                    rest.init(key)

                    if mainNode is None:
                        mainNode = controller.Controller(polyglot, 'controller', 'controller', 'Govee Controller')
                        n_queue.clear()
                        polyglot.addNode(mainNode)
                        wait_for_node_done()
                        mainNode.createDevices()
                else:
                    # No key provided
                    polyglot.Notices['API'] = 'Missing API Key'
            else:
                polyglot.Notices['API'] = 'Missing API Key Parameter'
            
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)


        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        # Just sit and wait for events
        polyglot.ready()
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

