import json
import os
import socket
import threading
from queue import Queue
import re
import argparse
import time
import pyfiglet

parse = argparse.ArgumentParser(description="You can scan your given ports and you can see ports status and service names")
src =parse.add_argument_group("Input")
src.add_argument("-t","--target",metavar="Target",help="Target host")
src.add_argument("-p","--port",metavar="Port",help="You can type one port or more like p1,p2,p3... if you want to give range you have to type like max_port min_port ",type=str,nargs="+")
src.add_argument("--thread",help="Thread number you can select between 1 and 500 if you don't select default is 200",type=int)
src.add_argument("-g","--get",metavar="Read",help="Gets ports from .txt file")
output = parse.add_argument_group("Output")
output.add_argument("--showclosed",help="Shows closed ports",action="store_true")
output.add_argument("--hideopen",help="Hides open ports",action="store_false")
output.add_argument("-w","--write",metavar="Write",help="Write result to .txt or .json")

args = parse.parse_args()

class Server():
    
    def __init__(self):
        
        self.ip_format = re.compile(r"^[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}\.[0-9]{0,3}$")
        if args.thread or args.thread ==0:
           if args.thread<1 or args.thread>500:
               raise NotExistsValueError("You have to select thread count between 1 and 500")
           self.THREADS = args.thread
        else:
            self.THREADS = 200   
        self.ports =[] 
    def scan(self):
        print(f"Scanning starting on host {self.HOST}...",end="\n\n")
        thread_list= [threading.Thread(target=self.scanner,daemon=True) for _ in range(self.THREADS)]
        for thread in thread_list:
            thread.start()
        begin = time.time()        
        for thread in thread_list:
            thread.join() 
        end = time.time()    
        return PortStatus(self.ports,end-begin)
    def scanner(self):
       while not self.queue.empty():
         port = self.queue.get()  
         try:
             service = socket.getservbyport(port)
         except:
             service = "unknown"    
         try:
          self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
          self.server.connect((self.HOST,port))
          
          self.ports.append((port,"open",service))
          self.server.close()
         except:
             self.ports.append((port,"closed",service))
              
    def put(self,host,port):
        host = socket.gethostbyname(host)
        if self.ip_format.match(host):
            self.HOST = host
        else:
            raise NotExistsIpError("Doesn't match the ip address form")    

        if (not "".join(port).replace(",","").isdecimal()) or  ( "," in "".join(port) and len(port)!=1) or (not (len(port)==2 or len(port)==1)):
          raise TypeError("Please enter valid arguments")
        
        condition = "," in "".join(port) and len(port)==1 or ("".join(port).isdecimal() and len(port)==1)      
        self.port_list = "".join(port).split(",") if condition else range(int(port[0]),int(port[1])+1)
        self.queue = Queue()
        for port in self.port_list:
            self.queue.put(int(port))
class NotExistsIpError(Exception):               
    pass
class NullResultError(Exception):
    pass
class MultiSelectedError(Exception):
    pass
class NotExistsValueError(Exception):
    pass
class PortStatus():
    def __init__(self,port_list,time):
        self.TIME = time
        self.PORT_LIST = port_list
    def parse_and_print(self,show_closed=True,show_open=True):
        print(" "*4+"Port"+" "*8+"Status"+" "*8+"Service\n" +" "*2+"-"*38)
        if not any([show_closed,show_open]):
            raise NullResultError("You can't false both of parameters")
        elif show_closed ==True and show_open==False:
          self.PORT_LIST=  [*filter(lambda x: x[1]=="closed",self.PORT_LIST)]
        elif show_closed==False and show_open==True: 
            self.PORT_LIST=  [*filter(lambda x: x[1]=="open",self.PORT_LIST)]  
                    
        for port,status,service in sorted(self.PORT_LIST,key=lambda x: x[1]=="open" or x[0]):
            print(" "*5+str(port) +" "*(16-len(str(port))-len(str(status)))+status + " "*10+service)
        print("\nScanning completed in {0:.2f} seconds".format(self.TIME))    
        if args.write:
          try:  
                file =open(os.curdir+"/output/"+args.write if os.path.basename(args.write)==args.write else args.write,"w",encoding="utf-8")
                if args.write.endswith(".txt"):
                  
                  for port,status,service in sorted(self.PORT_LIST,key=lambda x: x[1]=="open" or x[0]):
                    file.write(f"{port} {status} {service}\n")
                elif args.write.endswith(".json"):
                  json.dump([{"port":port,"status":status,"service":service} for port,status,service in sorted(self.PORT_LIST,key=lambda x: x[1]=="open" or x[0])],file)
                
                file.close()     
          except:
              raise FileNotFoundError("File not found")          
if __name__ == "__main__":
    print("\n")
    print(pyfiglet.figlet_format("PortScanner V1"),end="\n\n")
    if args.get:
        
        if args.port:
            raise MultiSelectedError("You cannot get ports from more then one options!")
        try:
            with open(os.curdir+"/input/"+args.get if os.path.basename(args.get)==args.get else args.get,"r") as file:
              data =[*map(lambda x: x.replace("\n",""),file.readlines())]
              data =",".join(data)
              if data:
                  args.port =[data]
              else:
                  raise NullResultError("File is empty!")  
        except:
            raise FileNotFoundError("File not found!")        
                    
    if args.port and args.target:
      server = Server()
      server.put(args.target,args.port)  
      result = server.scan()
      result.parse_and_print(show_closed=args.showclosed,show_open=args.hideopen) 
        
        
        
        
        
        