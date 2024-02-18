import csv
import time
import queue
import json

OUTPUT_DIR = "./output/"

class Logger():
    def __init__(self, configuration, event_queue):
        self.configuration = configuration
        self.event_queue = event_queue

        self.file = open(OUTPUT_DIR + configuration["file_name"], "w", newline="")
        self.writer = csv.writer(self.file, delimiter=',')
        self.stop_time = time.time() + configuration["duration"] + 0.1 # Some wait time for concluding messages

        self.header_written = False

    def run(self):
        print("Program starts - Press CTRL+BREAK to force exit")
        while(time.time() < self.stop_time):
            try:
                message = self.event_queue.get(timeout = self.stop_time - time.time())
            except queue.Empty:
                print("Finished logging because of duration end")
            else: # only if try is successful
                if message["header"] == "sensor-data":
                    if not self.header_written:
                        self.writer.writerow(list(message["body"].keys()))
                        self.header_written = True
                    self.writer.writerow(list(message["body"].values()))
                elif message["header"] == "loader-event":
                    self.log_message(message)
                elif message["header"] == "manager-event":
                    self.log_message(message)


    def log_message(self, message):
        print(message["time"], message["header"], json.dumps(message["body"]))