import socket
import threading
import logging
import dns
import worker
import multiprocessing


class UdpOutputThread(threading.Thread):

    def __init__(self, sock, queue):
        threading.Thread.__init__(self)
        self.sock = sock
        self.queue = queue

    def run(self):
        recv_sock = self.sock
        queue = self.queue
        while True:
            try:
                output, addr = queue.get()
                recv_sock.sendto(output, addr)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error('Got exception: %r', e, exc_info=True)

                
class UdpThread(threading.Thread):

    def __init__(self, sock, num_workers=4):
        threading.Thread.__init__(self)
        self.sock = sock
        self.input_queue = multiprocessing.Queue(512)
        self.output_queue = multiprocessing.Queue(512)
        self.workers = []
        for i in range(num_workers):
            self.create_worker()
        self.output_thread = UdpOutputThread(self.sock, self.output_queue)
        self.output_thread.daemon = True
        self.output_thread.start()

    def create_worker(self):
        w = multiprocessing.Process(target=worker.work,
            args=(self.input_queue, self.output_queue))
        w.start()
        self.workers.append(w)

    def run(self):
        recv_sock = self.sock
        input_queue = self.input_queue
        output_queue = self.output_queue
        while True:
            try:
                data, addr = recv_sock.recvfrom(512)
                logging.debug('Connection from %r length %d raw = %r',
                    addr, len(data), data)
                input_queue.put((data, addr))
            except KeyboardInterrupt:
                break
            except Exception as e:
                logging.error('Got exception: %r', e, exc_info=True)
        logging.debug('UdpThread exiting')


class TcpThread(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        accept_sock = self.sock
        while True:
            try:
                sock, addr = accept_sock.accept()
                logging.debug('Connection from %r', addr)
                data = sock.recv(514)
                sock.sendall(data)
                sock.close()
            except Exception as e:
                logging.error('Got exception.', e)
