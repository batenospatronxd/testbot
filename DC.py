#!/usr/bin/env python3
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

import socket
import time
import argparse
import sys
import random
import ipaddress
from datetime import datetime


class UDPPacketSender:
    def __init__(self, target_ip, target_port, packet_size=64, 
                 delay=0.1, count=10, random_data=False):
        """Initialize the UDP packet sender with target parameters."""
        try:
            # Validate IP address
            ipaddress.ip_address(target_ip)
            self.target_ip = target_ip
        except ValueError:
            print("Error: Invalid IP address: %s" % target_ip)
            sys.exit(1)
            
        # Validate port
        if not (1 <= target_port <= 65535):
            print("Error: Port must be between 1-65535, got %d" % target_port)
            sys.exit(1)
            
        self.target_port = target_port
        
        # Validate packet size (with reasonable limits)
        if not (16 <= packet_size <= 1472):  # Max UDP payload in standard Ethernet
            print("Error: Packet size must be between 16-1472 bytes, got %d" % packet_size)
            sys.exit(1)
            
        self.packet_size = packet_size
        
        # Validate delay (prevent flooding)
        if delay < 0.1:  # Enforce minimum delay of 100ms
            print("Warning: Minimum delay is 0.1 seconds. Setting delay to 0.1.")
            self.delay = 0.1
        else:
            self.delay = delay
            
        # Validate count (with reasonable limits)
        if count > 100:  # Limit maximum packets for safety
            print("Warning: Maximum packet count is 100. Setting count to 100.")
            self.count = 100
        else:
            self.count = count
            
        self.random_data = random_data
        self.sock = None
        self.packets_sent = 0
        
    def generate_packet(self):
        """Generate packet data of specified size."""
        if self.random_data:
            return bytes(random.randint(0, 255) for _ in range(self.packet_size))
        else:
            # Create a recognizable pattern for educational purposes
            return b'X' * self.packet_size
    
    def connect(self):
        """Create UDP socket."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Socket created successfully")
        except socket.error as e:
            print("Socket creation failed: %s" % e)
            sys.exit(1)
    
    def send_packets(self):
        """Send UDP packets to the target."""
        if not self.sock:
            self.connect()
            
        print("\nETHICAL REMINDER: Only use on systems you own or have permission to test!\n")
        print("Starting UDP packet sending to %s:%d" % (self.target_ip, self.target_port))
        print("Packet size: %d bytes, Delay: %.1fs, Count: %d" % (self.packet_size, self.delay, self.count))
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            for i in range(self.count):
                packet = self.generate_packet()
                self.sock.sendto(packet, (self.target_ip, self.target_port))
                self.packets_sent += 1
                
                # Print progress
                print("[%s] Packet %d/%d sent (%d bytes)" % (datetime.now().strftime('%H:%M:%S'), i+1, self.count, len(packet)))
                
                # Respect the delay to prevent flooding
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


def validate_positive(value_type):
    """Create a validator for positive numeric values."""
    def validate(value):
        try:
            ivalue = int(value)
            if ivalue <= 0:
                raise argparse.ArgumentTypeError("%s must be positive" % value_type)
            return ivalue
        except ValueError:
            raise argparse.ArgumentTypeError("%s must be an integer" % value_type)
    return validate


def validate_float_positive(value_type):
    """Create a validator for positive float values."""
    def validate(value):
        try:
            fvalue = float(value)
            if fvalue <= 0:
                raise argparse.ArgumentTypeError("%s must be positive" % value_type)
            return fvalue
        except ValueError:
            raise argparse.ArgumentTypeError("%s must be a number" % value_type)
    return validate


def main():
    """Parse command line arguments and run the UDP packet sender."""
    parser = argparse.ArgumentParser(
        description="UDP Packet Sender - Educational Tool",
        epilog="EDUCATIONAL USE ONLY. Use responsibly and ethically."
    )
    
    parser.add_argument("target_ip", help="Target IP address")
    parser.add_argument("target_port", type=int, help="Target port (1-65535)")
    parser.add_argument("-s", "--size", type=validate_positive("Packet size"), 
                        default=64, help="Packet size in bytes (default: 64)")
    parser.add_argument("-d", "--delay", type=validate_float_positive("Delay"), 
                        default=0.1, help="Delay between packets in seconds (default: 0.1)")
    parser.add_argument("-c", "--count", type=validate_positive("Count"), 
                        default=10, help="Number of packets to send (default: 10)")
    parser.add_argument("-r", "--random", action="store_true", 
                        help="Use random data for packets")
    
    # Print ethical banner
    print("\n" + "=" * 80)
    print("UDP PACKET SENDER - EDUCATIONAL TOOL".center(80))
    print("=" * 80)
    print("ETHICAL USAGE WARNING:".center(80))
    print("This tool is for educational purposes only.".center(80))
    print("Only use on systems you own or have explicit permission to test.".center(80))
    print("Unauthorized network scanning or flooding is illegal.".center(80))
    print("=" * 80 + "\n")
    
    # Check for no arguments and print help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # Confirm ethical usage
    confirm = input("Do you confirm that you are using this tool ethically and have permission "
                   "to send packets to the specified target? (yes/no): ")
    if confirm.lower() not in ["yes", "y"]:
        print("Operation cancelled. Ethical usage not confirmed.")
        sys.exit(0)
    
    # Create and run the UDP packet sender
    sender = UDPPacketSender(
        args.target_ip, 
        args.target_port,
        packet_size=args.size,
        delay=args.delay,
        count=args.count,
        random_data=args.random
    )
    
    sender.send_packets()


if __name__ == "__main__":
    main()
