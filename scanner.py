import queue
from queue import Queue
from threading import Thread
import socket
import re
from exceptions import InvalidThreadCountError
from portstatus import PortStatus
import time


class Scanner:

    def __init__(self, thread_count, limit):

        self.queue: queue.Queue = None
        self.HOST = None
        self.server = None
        self.limit = limit
        self.ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
        if thread_count < 1 or thread_count > 500:
            raise InvalidThreadCountError("You have to select thread count between 1 and 500")
        self.THREADS = thread_count
        self.ports = []

    def start_threads(self):
        self.thread_list = [Thread(target=self.scanner, daemon=True) for _ in range(self.THREADS)]
        for thread in self.thread_list:
            thread.start()

    def wait_threads(self):
        for thread in self.thread_list:
            thread.join()

    def scan(self, scr):
        scr.addstr(f"  Scanning started on host {self.HOST}...\n")
        scr.addstr(
            "\n\n" + " " * 4 + "Port" + " " * 8 + "Status" + " " * 8 + "Service\n" + " " * 2 + "-" * 38 + "\n")
        scr.refresh()
        self.start_threads()
        begin = time.time()
        self.wait_threads()
        end = time.time()
        return PortStatus(self.ports, end - begin, scr)

    def scanner(self):
        while not self.queue.empty() and (self.limit is None or len(self.ports) < self.limit):
            port = self.queue.get()
            try:
                service = socket.getservbyport(port)
            except Exception:
                service = "unknown"
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.connect((self.HOST, port))
                self.ports.append((port, service))
                self.server.close()
            except socket.error:
                pass

    def put(self, host, ports):
        self.HOST = host
        self.queue = Queue()
        for port in ports:
            self.queue.put(port)
