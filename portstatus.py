import os
import json
import curses


class PortStatus:
    def __init__(self, port_list, t, scr):
        self.TIME = t
        self.screen = scr
        self.PORT_LIST = port_list

    def print_status(self):

        for port, service in sorted(self.PORT_LIST):
            self.screen.addstr(" " * 4 + str(port) + " " * 8 + "open" + " " * 10 + service + "\n")
        self.screen.refresh()

        self.screen.addstr("\n\n  Scanning completed in {0:.2f} seconds".format(self.TIME))

    def write_to_file(self, output_path):
        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    if output_path.endswith(".txt"):
                        for port, service in sorted(self.PORT_LIST):
                            f.write(f"{port} open {service}\n")

                    elif output_path.write.endswith(".json"):
                        json_data = [{"port": port, "status": "open", "service": service} for port, service in
                                     sorted(self.PORT_LIST)]
                        json.dump(json_data, f)

                    self.screen.addstr("\n  Saved to {}".format(os.path.abspath(output_path)))
            except OSError:
                self.screen.addstr("Output file not found!\n")
                self.screen.getch()
                curses.endwin()
