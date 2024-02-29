import datetime
import zmq
from threading import Lock

class Instrument():
    def __init__(self, name, configuration, context):
        self.name = name
        self.configuration = configuration
        self.context = context
        self.state_lock = Lock()
        self.init_sockets()
        self.set_state("opening")
        self.main()

    def __del__(self):
        self.terminate_sockets()

    def set_state(self, state):
        self.state_lock.acquire()
        self.state = state
        self.state_lock.release()

    def get_state(self):
        self.state_lock.acquire()
        state = self.state
        self.state_lock.release()
        return state
    
    def main(self):
        while True:
            if self.sockets_ready: # For some instruments, it might make sense to init sockets in open
                self.listen(0)
            state = self.get_state()
            if state == "opening":
                self.open()
                self.set_state("waiting")
            elif state == "waiting":
                self.wait()
            elif state == "running":
                self.run()
            elif state == "closing":
                self.close()
                break
            else:
                raise ValueError("Unknown state: " + state)

    def init_sockets(self):
        self.socket = self.context.socket(zmq.PAIR)
        self.socket.connect("inproc://manager-" + self.name)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.sockets_ready = True

    def terminate_sockets(self):
        self.socket.close()
        self.sockets_ready = False

    def open(self):
        pass

    def close(self):
        pass

    def run(self):
        pass

    def wait(self):
        return self.listen()

    def listen(self, timeout = None):
        try:
            events = self.poller.poll(timeout)
        except KeyboardInterrupt:
            self.set_state("closing")
            events = []
        if len(events) > 0:
            for event in events:
                if event[0] == self.socket and event[1] == zmq.POLLIN:
                    message = event[0].recv_json()
                    self.process_message(message)

    def process_message(self, message):
        if "command" in message["body"] and message["body"]["command"] == "finish":
            self.set_state("closing")
            self.send_event(command = "finish")
        elif "command" in message["body"] and message["body"]["command"] == "start":
            self.set_state("running")
        elif "command" in message["body"] and message["body"]["command"] == "stop":
            self.set_state("waiting")

    def send_event(self, **kwargs):
        event = dict()
        event["sender"] = self.name
        event["header"] = self.name + "-event"
        event["time"] = datetime.datetime.now().isoformat()
        event["body"] = kwargs
        self.socket.send_json(event)
    
