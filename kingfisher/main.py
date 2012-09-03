import sys
import socket
import net
import threading
import logging

def main(argv):
    sys.stdout.write(str(argv) + '\n')
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    u.bind(('127.0.0.1', 1053))
    x = net.UdpThread(u)
    x.start()
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main(sys.argv))
