from queue import Queue
from threading import Thread
import socket
import re
from exceptions import NotExistsIpError 
from portstatus import PortStatus
import time


class Scanner:

    def __init__(self,thread_count,limit):

        self.queue = None
        self.port_list = None
        self.HOST = None
        self.server = None
        self.limit = limit
        self.ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
        if thread_count or thread_count == 0:
            if thread_count < 1 or thread_count > 500:
                raise NotExistsValueError("You have to select thread count between 1 and 500")
            self.THREADS = thread_Count
        else:
            self.THREADS = 200
        self.ports = []
    def start_threads(self):
        self.thread_list = [Thread(target=self.scanner,daemon=True) for _ in range(self.THREADS)]
        for thread in self.thread_list:
            thread.start()
    def wait_threads(self):
        for thread in self.thread_list:
            thread.join()

    def scan(self,scr):
        scr.addstr(f"  Scanning starting on host {self.HOST}...")
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
            except socket.error:
                service = "unknown"
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.settimeout(3)
                self.server.connect((self.HOST, port))

                self.ports.append((port, service))
                self.server.close()
            except socket.error:
                pass

    def put(self, host, port):
        host = socket.gethostbyname(host)
        if self.ip_format.match(host):
            self.HOST = host
        else:
            raise NotExistsIpError("Doesn't match the ip address form")

        if (not "".join(port).replace(",", "").isdecimal()) or ("," in "".join(port) and len(port) != 1) or (
                not (len(port) == 2 or len(port) == 1)):
            raise TypeError("Please enter valid arguments")

        condition = ("," in "".join(port) or  "".join(port).isdecimal()) and  len(port) == 1
        self.port_list = "".join(port).split(",") if condition else range(int(port[0]), int(port[1]) + 1)
        self.queue = Queue()
        for port in self.port_list:
            self.queue.put(int(port))

