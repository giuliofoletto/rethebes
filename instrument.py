import datetime
import zmq

class Instrument():
    def __init__(self, name, configuration, context):
        self.name = name
        self.configuration = configuration
        self.context = context
        self.init_sockets()

    def __del__(self):
        self.socket.close()

    def init_sockets(self):
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect("inproc://manager-" + self.name)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

    def prepare_and_run(self):
        self.should_continue = True
        self.is_running = True
        self.run()

    def run(self):
        pass

    def listen(self, timeout = None):
        events = self.poller.poll(timeout)
        if len(events) > 0:
            for event in events:
                if event[0] == self.socket and event[1] == zmq.POLLIN:
                    message = event[0].recv_json()
                    self.process_message(message)

    def process_message(self):
        pass

    def send_event(self, **kwargs):
        event = dict()
        event["sender"] = self.name
        event["header"] = self.name + "-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        self.socket.send_json(event)
    
