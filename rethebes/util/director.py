"""
Generic director class that controls multiple instruments.

Authors: Giulio Foletto.
"""

import logging
from threading import Thread
import zmq
from rethebes.util import Instrument

class Director(Instrument):
    def __init__(self, name, context, subordinates = []):
        self.subordinates = subordinates
        self.threads = dict()
        super().__init__(name, context)

    def release(self):
        self.terminate_sockets()
        self.threads.clear()
        self.subordinates.clear()

    def init_sockets(self):
        self.poller = zmq.Poller()
        self.sockets = dict()
        for subordinate in self.subordinates:
            socket = self.context.socket(zmq.PAIR)
            socket.bind("inproc://" + subordinate.name)
            self.sockets[subordinate.name] = socket
            self.poller.register(socket, zmq.POLLIN)
        self.sockets_ready = True

    def open(self):
        for subordinate in self.subordinates:
            thread = Thread(target = subordinate.main)
            self.threads[subordinate.name] = thread
            thread.start()
        self.send_event(command = "start")
        logging.info("Program starts - Press CTRL+C to exit (more or less) gracefully or CTRL+BREAK to force exit")

    def close(self):
        logging.info("Program ends gracefully")

    def run(self):
        # Should never run
        self.set_state("waiting")

    def wait(self):
        if self.check_should_continue():
            self.listen() # Exit only with a message
        else:
            self.set_state("closing")

    def listen(self, timeout = None):
        try:
            events = self.poller.poll(timeout)
        except KeyboardInterrupt:
            self.send_event(command = "close")
            self.wait_for_closure()
            events = []
        if len(events) > 0:
            for event in events:
                if event[0] in self.sockets.values() and event[1] == zmq.POLLIN:
                    message = event[0].recv_json()
                    self.process_message(message)

    def check_should_continue(self):
        return bool(self.threads)
    
    def wait_for_closure(self):
        names = list(self.threads.keys())
        for name in names:
            self.threads[name].join()
            self.threads.pop(name)
            self.sockets[name].close()
            self.poller.unregister(self.sockets[name])
            self.sockets.pop(name)