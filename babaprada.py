#!/usr/bin/env python3
"""
UDP Network Testing Tool

This script sends UDP packets to a specified IP address and port for a given duration.
It's designed for legitimate network testing of your own servers.

Usage:
    python udp_client.py <target_ip> <port> <duration_seconds>

Example:
    python udp_client.py 192.168.1.100 8080 10
"""

import socket
import sys
import time
import random
import string
import argparse
from datetime import datetime

def generate_random_data(size=1024):
    """Generate random string data of specified size."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def send_udp_packets(target_ip, port, duration):
    """
    Send UDP packets to the target IP and port for the specified duration.
    
    Args:
        target_ip (str): Target IP address
        port (int): Target port
        duration (int): Duration in seconds to send packets
    """
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Generate some random data to send
    data = generate_random_data().encode('utf-8')
    
    # Calculate end time
    end_time = time.time() + duration
    packets_sent = 0
    
    print(f"[*] Starting UDP packet transmission to {target_ip}:{port}")
    print(f"[*] Test will run for {duration} seconds")
    print(f"[*] Press Ctrl+C to stop before the duration completes")
    
    start_time = time.time()
    
    try:
        # Send packets until duration is reached
        while time.time() < end_time:
            sock.sendto(data, (target_ip, port))
            packets_sent += 1
            
            # Print status every second
            if packets_sent % 100 == 0:
                elapsed = time.time() - start_time
                print(f"[+] Sent {packets_sent} packets in {elapsed:.2f} seconds "
                      f"({packets_sent/elapsed:.2f} packets/sec)")
            
            # Small delay to prevent overwhelming local resources
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n[!] Test interrupted by user")
    finally:
        # Close the socket
        sock.close()
        
        # Calculate and display statistics
        total_time = time.time() - start_time
        print("\n--- Test Results ---")
        print(f"Target: {target_ip}:{port}")
        print(f"Duration: {total_time:.2f} seconds")
        print(f"Packets sent: {packets_sent}")
        print(f"Rate: {packets_sent/total_time:.2f} packets/second")
        print(f"Approximate data sent: {(packets_sent * len(data)) / (1024*1024):.2f} MB")

def validate_ip(ip):
    """Validate IP address format."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def main():
    """Main function to parse arguments and start the test."""
    parser = argparse.ArgumentParser(
        description="UDP Network Testing Tool - For testing your own servers only"
    )
    parser.add_argument("target_ip", help="Target IP address")
    parser.add_argument("port", type=int, help="Target port number")
    parser.add_argument("duration", type=int, help="Test duration in seconds")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validate_ip(args.target_ip):
        print("[!] Error: Invalid IP address format")
        sys.exit(1)
        
    if args.port < 1 or args.port > 65535:
        print("[!] Error: Port must be between 1 and 65535")
        sys.exit(1)
        
    if args.duration < 1:
        print("[!] Error: Duration must be at least 1 second")
        sys.exit(1)
    
    # Display warning and confirmation
    print("\n" + "="*60)
    print("WARNING: This tool is for legitimate network testing purposes only.")
    print("You should only use this against servers you own or have permission to test.")
    print("Unauthorized testing against third-party servers may be illegal.")
    print("="*60 + "\n")
    
    confirmation = input("Do you confirm you're testing your own server? (yes/no): ")
    if confirmation.lower() != "yes":
        print("[!] Test aborted by user")
        sys.exit(0)
    
    # Start the test
    send_udp_packets(args.target_ip, args.port, args.duration)

if __name__ == "__main__":
    main()
