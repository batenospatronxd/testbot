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
        
        # Validate duration with reasonable limits
        try:
            duration = float(duration)
            if duration <= 0:
                print("Error: Duration must be positive")
                sys.exit(1)
            if duration > 60:  # Limit to 60 seconds for educational purposes
                print("Warning: Maximum duration is 60 seconds for educational purposes")
                self.duration = 60
            else:
                self.duration = duration
        except ValueError:
            print("Error: Duration must be a number")
            sys.exit(1)
            
        # Fixed reasonable parameters for educational purposes
        self.packet_size = 1024  # Standard packet size
        self.delay = 0.01  # 10ms between packets
        self.sock = None
        self.packets_sent = 0
        
    def generate_packet(self):
        """Generate packet data of specified size."""
        if PY2:
            return ''.join(chr(random.randint(0, 255)) for _ in range(self.packet_size))
        else:
            return bytes(random.randint(0, 255) for _ in range(self.packet_size))
    
    def connect(self):
        """Create UDP socket."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Socket created successfully")
        except socket.error as e:
            print("Socket creation failed: %s" % e)
            sys.exit(1)
    
    def send_packets(self):
        """Send UDP packets to the target for the specified duration."""
        if not self.sock:
            self.connect()
            
        print("\nETHICAL REMINDER: Only use on systems you own or have permission to test!\n")
        print("Starting UDP packet sending to %s:%d" % (self.target_ip, self.target_port))
        print("Duration: %.2f seconds, Packet size: %d bytes" % (self.duration, self.packet_size))
        print("-" * 60)
        
        start_time = time.time()
        end_time = start_time + self.duration
        
        try:
            while time.time() < end_time:
                packet = self.generate_packet()
                self.sock.sendto(packet, (self.target_ip, self.target_port))
                self.packets_sent += 1
                
                # Print progress every 100 packets
                if self.packets_sent % 100 == 0:
                    elapsed = time.time() - start_time
                    remaining = max(0, self.duration - elapsed)
                    print("[%s] Packets sent: %d (%.1f seconds remaining)" % 
                          (datetime.now().strftime('%H:%M:%S'), self.packets_sent, remaining))
                
                # Respect the delay to prevent excessive resource usage
                time.sleep(self.delay)
                
        except KeyboardInterrupt:
            print("\nPacket sending interrupted by user")
        except Exception as e:
            print("\nError sending packets: %s" % e)
        finally:
            elapsed_time = time.time() - start_time
            self.print_summary(elapsed_time)
            self.close()
    
    def print_summary(self, elapsed_time):
        """Print summary of the packet sending operation."""
        print("\n" + "=" * 60)
        print("UDP Packet Sending Summary:")
        print("Target: %s:%d" % (self.target_ip, self.target_port))
        print("Packets sent: %d" % self.packets_sent)
        print("Packet size: %d bytes" % self.packet_size)
        print("Total data sent: %d bytes" % (self.packets_sent * self.packet_size))
        print("Time elapsed: %.2f seconds" % elapsed_time)
        if elapsed_time > 0:
            rate = (self.packets_sent * self.packet_size * 8) / (elapsed_time * 1000)
            print("Average sending rate: %.2f kbps" % rate)
        print("=" * 60)
    
    def close(self):
        """Close the UDP socket."""
        if self.sock:
            self.sock.close()
            print("Socket closed")


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
    sender.send_packets()


if __name__ == "__main__":
    main()
