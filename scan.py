import curses
import argparse
import time
import pyfiglet
from exceptions import MultiSelectedError, NullResultError 
from scanner import Scanner

def parse_arguments():
    
    parse = argparse.ArgumentParser(
    description="You can scan your given ports and you can see ports status and service names")

    src = parse.add_argument_group("Input")
    src.add_argument("-t", "--target", metavar="Target", help="Target host",required=True)
    src.add_argument("-p", "--port", metavar="Port",
                 help="You can type one port or more like p1,p2,p3... "
                      "if you want to give range you have to type like MIN_PORT MAX_PORT ",
                 type=str, nargs="+",required=True)
    src.add_argument("--thread", help="Thread number you can select between 1 and 500 if you don't select default is 200",
                 type=int)
    src.add_argument("--limit",help="don't show ports more than limit",type=int)
    src.add_argument("-g", "--get", metavar="Read", help="Gets ports from .txt file")
    output = parse.add_argument_group("Output")
    output.add_argument("-w", "--write", metavar="Write", help="Write result to .txt or .json")

    args = parse.parse_args()
    
    return args

def main():
    args = parse_arguments()
    scr = curses.initscr()
    scr.addstr(pyfiglet.figlet_format("  PortScanner V 1.2",width=110)+"\n\n")
    scr.refresh()
    if args.get:
        if args.port:
            raise MultiSelectedError("You cannot get ports from more then one options!")
        try:
            with open(args.get, "r") as file:
                data = [*map(lambda x: x.replace("\n", ""), file.readlines())]
                data = ",".join(data)
                if data:
                    args.port = [data]
                else:
                    raise NullResultError("File is empty!")
        except OSError:
            raise FileNotFoundError("File not found!")

    if args.port and args.target:
        scanner = Scanner(args.thread,args.limit)
        scanner.put(args.target, args.port)
        result = scanner.scan(scr)
        result.parse_and_print(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
