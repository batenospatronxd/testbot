#!/usr/bin/env python
"""
UDP Packet Sender - Educational Tool

This script demonstrates how UDP packets work for educational purposes only.
It is designed with strict ethical limitations and should only be used on systems
you own or have explicit permission to test.

ETHICAL USAGE GUIDELINES:
1. Only use on your own systems or systems you have explicit permission to test
2. Never use against production systems or public services
3. Always comply with local laws and regulations
4. This tool is for educational purposes only

DISCLAIMER:
The author does not take responsibility for any misuse of this tool.
Unauthorized network scanning or flooding is illegal in most jurisdictions.
"""

from __future__ import print_function  # For Python 2 compatibility

import socket
import time
import sys
import random
import threading
from datetime import datetime

# Python 2/3 compatibility
PY2 = sys.version_info[0] == 2
if PY2:
    input = raw_input
    # For Python 2, we need to implement our own ip_address validation
    def ip_address(ip_string):
        """Simple IP address validation for Python 2."""
        parts = ip_string.split('.')
        if len(parts) != 4:
            raise ValueError("IPv4 address should have 4 parts")
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError("Each part must be 0-255")
            except ValueError:
                raise ValueError("Each part must be an integer")
        return ip_string
else:
    # Python 3
    from ipaddress import ip_address


class UDPPacketSender:
    def __init__(self, target_ip, target_port, duration, threads=4):
        """Initialize the UDP packet sender with target parameters."""
        try:
            # Validate IP address
            ip_address(target_ip)
            self.target_ip = target_ip
        except ValueError:
            print("Error: Invalid IP address: %s" % target_ip)
            sys.exit(1)
            
        # Validate port
        try:
            port = int(target_port)
            if not (1 <= port <= 65535):
                print("Error: Port must be between 1-65535, got %d" % port)
                sys.exit(1)
            self.target_port = port
        except ValueError:
            print("Error: Port must be a number")
            sys.exit(1)
        
        # Validate duration with reasonable limits
        try:
            duration = float(duration)
            if duration <= 0:
                print("Error: Duration must be positive")
                sys.exit(1)
            if duration > 30:  # Limit to 30 seconds for educational purposes
                print("Warning: Maximum duration is 30 seconds for educational purposes")
                self.duration = 30
            else:
                self.duration = duration
        except ValueError:
            print("Error: Duration must be a number")
            sys.exit(1)
            
        # Optimized parameters for better performance
        self.packet_size = 8192  # Increased packet size (8KB)
        self.threads = min(threads, 8)  # Limit number of threads to 8 max
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.packets_sent = 0
        self.bytes_sent = 0
        
        # Pre-generate some packets to avoid overhead during sending
        self.packets = []
        for _ in range(10):  # Create 10 different packet patterns
            if PY2:
                self.packets.append(''.join(chr(random.randint(0, 255)) for _ in range(self.packet_size)))
            else:
                self.packets.append(bytes(random.randint(0, 255) for _ in range(self.packet_size)))
    
    def sender_thread(self, thread_id):
        """Thread function to send UDP packets."""
        # Create a socket for each thread
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Set socket options for better performance
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)  # Larger send buffer
            
            # Bind to different local ports to avoid port conflicts
            if thread_id > 0:  # Skip for first thread
                try:
                    # Try to bind to a specific port (useful for some systems)
                    sock.bind(('0.0.0.0', 0))  # Let the OS assign a port
                except:
                    pass  # Ignore if binding fails
                    
        except socket.error as e:
            print("Thread %d: Socket creation failed: %s" % (thread_id, e))
            return
            
        # Get a subset of packets for this thread to use
        thread_packets = self.packets
        packet_count = len(thread_packets)
        
        # Send packets as fast as possible until stop event is set
        local_count = 0
        while not self.stop_event.is_set():
            try:
                # Use round-robin selection of packets
                packet = thread_packets[local_count % packet_count]
                sock.sendto(packet, (self.target_ip, self.target_port))
                
                # Update counters (thread-safe)
                with self.lock:
                    self.packets_sent += 1
                    self.bytes_sent += len(packet)
                    
                local_count += 1
                
                # Minimal delay to prevent CPU saturation
                if local_count % 1000 == 0:
                    time.sleep(0.001)
                    
            except Exception as e:
                print("Thread %d: Error sending packet: %s" % (thread_id, e))
                break
                
        # Clean up
        sock.close()
    
    def start_sending(self):
        """Start multiple threads to send UDP packets."""
        print("\nETHICAL REMINDER: Only use on systems you own or have permission to test!\n")
        print("Starting UDP packet sending to %s:%d" % (self.target_ip, self.target_port))
        print("Duration: %.2f seconds, Packet size: %d bytes, Threads: %d" % 
              (self.duration, self.packet_size, self.threads))
        print("-" * 60)
        
        # Create and start sender threads
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.sender_thread, args=(i,))
            t.daemon = True  # Thread will exit when main thread exits
            threads.append(t)
            t.start()
            print("Started sender thread %d" % i)
            
        # Monitor and report progress
        start_time = time.time()
        try:
            last_packets = 0
            last_time = start_time
            
            while time.time() - start_time < self.duration:
                time.sleep(0.5)  # Update stats every 0.5 seconds
                
                current_time = time.time()
                elapsed = current_time - start_time
                remaining = max(0, self.duration - elapsed)
                
                # Calculate current rate
                current_packets = self.packets_sent
                delta_packets = current_packets - last_packets
                delta_time = current_time - last_time
                
                if delta_time > 0:
                    rate = (delta_packets * self.packet_size * 8) / (delta_time * 1000000)
                    print("[%s] Packets: %d, Rate: %.2f Mbps (%.1f seconds remaining)" % 
                          (datetime.now().strftime('%H:%M:%S'), 
                           current_packets, rate, remaining))
                    
                last_packets = current_packets
                last_time = current_time
                
        except KeyboardInterrupt:
            print("\nPacket sending interrupted by user")
        finally:
            # Signal threads to stop and wait for them
            self.stop_event.set()
            
            for i, t in enumerate(threads):
                t.join(timeout=1.0)
                print("Stopped sender thread %d" % i)
                
            # Print summary
            elapsed_time = time.time() - start_time
            self.print_summary(elapsed_time)
    
    def print_summary(self, elapsed_time):
        """Print summary of the packet sending operation."""
        print("\n" + "=" * 60)
        print("UDP Packet Sending Summary:")
        print("Target: %s:%d" % (self.target_ip, self.target_port))
        print("Packets sent: %d" % self.packets_sent)
        print("Packet size: %d bytes" % self.packet_size)
        print("Total data sent: %d bytes (%.2f MB)" % 
              (self.bytes_sent, self.bytes_sent / (1024 * 1024)))
        print("Time elapsed: %.2f seconds" % elapsed_time)
        
        if elapsed_time > 0:
            rate_kbps = (self.bytes_sent * 8) / (elapsed_time * 1000)
            rate_mbps = rate_kbps / 1000
            print("Average sending rate: %.2f Mbps (%.2f kbps)" % (rate_mbps, rate_kbps))
            print("Packets per second: %.2f" % (self.packets_sent / elapsed_time))
        
        print("=" * 60)


def main():
    """Simple main function to get IP, port and duration."""
    # Print ethical banner
    print("\n" + "=" * 80)
    print("UDP PACKET SENDER - EDUCATIONAL TOOL".center(80))
    print("=" * 80)
    print("ETHICAL USAGE WARNING:".center(80))
    print("This tool is for educational purposes only.".center(80))
    print("Only use on systems you own or have explicit permission to test.".center(80))
    print("Unauthorized network scanning or flooding is illegal.".center(80))
    print("=" * 80 + "\n")
    
    # Get parameters
    if len(sys.argv) == 4:
        target_ip = sys.argv[1]
        target_port = sys.argv[2]
        duration = sys.argv[3]
    else:
        print("Usage: python %s <target_ip> <target_port> <duration_seconds>" % sys.argv[0])
        print("Example: python %s 127.0.0.1 8080 5" % sys.argv[0])
        sys.exit(1)
    
    # Confirm ethical usage
    confirm = input("Do you confirm that you are using this tool ethically and have permission "
                   "to send packets to the specified target? (yes/no): ")
    if confirm.lower() not in ["yes", "y"]:
        print("Operation cancelled. Ethical usage not confirmed.")
        sys.exit(0)
    
    # Create and run the UDP packet sender
    sender = UDPPacketSender(target_ip, target_port, duration)
    sender.start_sending()


if __name__ == "__main__":
    main()
