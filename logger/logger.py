import time
import queue
import json

class Logger():
    def __init__(self, configuration, event_queue):
        self.configuration = configuration
        self.event_queue = event_queue

        self.stop_time = time.time() + configuration["duration"] + 0.1 # Some wait time for concluding messages

    def run(self):
        print("Program starts - Press CTRL+BREAK to force exit")
        while(time.time() < self.stop_time):
            try:
                message = self.event_queue.get(timeout = self.stop_time - time.time())
            except queue.Empty:
                print("Finished logging because of duration end")
            else: # only if try is successful
                if message["header"] == "sensor-data":
                    pass # Do nothing at the moment
                if message["header"] == "loader-event":
                    self.log_message(message)
                elif message["header"] == "manager-event":
                    self.log_message(message)


    def log_message(self, message):
        print(message["time"], message["header"], json.dumps(message["body"]))