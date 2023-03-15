import os
import json
import curses

class PortStatus:
    def __init__(self, port_list, t, scr):
        self.TIME = t
        self.screen = scr
        self.PORT_LIST = port_list

    def parse_and_print(self,args): 
        self.screen.addstr("\n\n"+" " * 4 + "Port" + " " * 8 + "Status" + " " * 8 + "Service\n" + " " * 2 + "-" * 38 + "\n")
        for port, service in sorted(self.PORT_LIST):
            self.screen.addstr(" " * 5 + str(port) + " " * (16 - len(str(port)) - 4) + " " * 10 + service+"\n")
        self.screen.refresh()
        if args.write:
            try:
                with open(args.write,"w",encoding="utf-8") as f:
                    if args.write.endswith(".txt"):
                        for port, service in sorted(self.PORT_LIST):
                            f.write(f"{port} open {service}\n")

                    elif args.write.endswith(".json"):
                        json_data = [{"port": port,"status": "open","service": service} for port, service in sorted(self.PORT_LIST)]
                        json.dump(json_data, f)
                   
                    self.screen.addstr("\n  Saved to {}".format(os.path.abspath(args.write)))
            except OSError:
                raise FileNotFoundError("File not found")

        self.screen.addstr("\n\n  Scanning completed in {0:.2f} seconds".format(self.TIME))
        
        self.screen.getch()
        curses.endwin()
