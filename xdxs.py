#!/usr/bin/env python
"""
Simple UDP Flood Tool for Network Testing
For testing your own servers only
"""

import socket
import sys
import time
import random
import string
import threading

def generate_random_data(size=1024):
    """Generate random string data of specified size."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def send_udp_packets(target_ip, port, duration, packet_size=1024):
    """Send UDP packets to the target IP and port."""
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Generate random data to send based on packet size
    data = generate_random_data(packet_size).encode('utf-8')
    
    # Calculate end time
    end_time = time.time() + duration
    packets_sent = 0
    
    print("[*] Starting UDP packet transmission to %s:%s" % (target_ip, port))
    print("[*] Test will run for %s seconds" % duration)
    print("[*] Packet size: %s bytes" % packet_size)
    print("[*] Press Ctrl+C to stop before the duration completes")
    
    start_time = time.time()
    
    try:
        # Send packets until duration is reached
        while time.time() < end_time:
            sock.sendto(data, (target_ip, port))
            packets_sent += 1
            
            # Print status every 1000 packets
            if packets_sent % 1000 == 0:
                elapsed = time.time() - start_time
                print("[+] Sent %s packets in %.2f seconds (%.2f packets/sec)" % 
                      (packets_sent, elapsed, packets_sent/elapsed))
            
    except KeyboardInterrupt:
        print("\n[!] Test interrupted by user")
    finally:
        # Close the socket
        sock.close()
        
        # Calculate and display statistics
        total_time = time.time() - start_time
        print("\n--- Test Results ---")
        print("Target: %s:%s" % (target_ip, port))
        print("Duration: %.2f seconds" % total_time)
        print("Packets sent: %s" % packets_sent)
        print("Rate: %.2f packets/second" % (packets_sent/total_time))
        print("Packet size: %s bytes" % packet_size)
        print("Approximate data sent: %.2f MB" % ((packets_sent * len(data)) / (1024*1024)))

def run_threads(target_ip, port, duration, packet_size, num_threads):
    """Run multiple threads for higher intensity testing."""
    threads = []
    
    for i in range(num_threads):
        thread = threading.Thread(
            target=send_udp_packets,
            args=(target_ip, port, duration, packet_size)
        )
        threads.append(thread)
        thread.start()
        print("[*] Started thread %s" % (i + 1))
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()

def main():
    """Main function to parse arguments and start the test."""
    if len(sys.argv) < 4:
        print("Usage: python test.py <target_ip> <port> <duration> [packet_size] [threads]")
        print("Example: python test.py 192.168.1.100 8080 10 8192 4")
        sys.exit(1)
    
    # Parse command line arguments
    target_ip = sys.argv[1]
    port = int(sys.argv[2])
    duration = int(sys.argv[3])
    
    # Optional arguments
    packet_size = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
    num_threads = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    
    # Validate inputs
    if port < 1 or port > 65535:
        print("[!] Error: Port must be between 1 and 65535")
        sys.exit(1)
        
    if duration < 1:
        print("[!] Error: Duration must be at least 1 second")
        sys.exit(1)
        
    if packet_size < 1 or packet_size > 65507:  # Max UDP packet size
        print("[!] Error: Packet size must be between 1 and 65507 bytes")
        sys.exit(1)
        
    if num_threads < 1 or num_threads > 100:
        print("[!] Error: Number of threads must be between 1 and 100")
        sys.exit(1)
    
    # Display warning and confirmation
    print("\n" + "="*60)
    print("WARNING: This tool is for legitimate network testing purposes only.")
    print("You should only use this against servers you own or have permission to test.")
    print("Unauthorized testing against third-party servers may be illegal.")
    
    # Additional warning for high intensity tests
    if packet_size > 8192 or num_threads > 10:
        print("\nHIGH INTENSITY TEST DETECTED!")
        print("You are requesting a high-intensity test that could potentially")
        print("cause significant load on both your network and the target server.")
    print("="*60 + "\n")
    
    confirmation = raw_input("Do you confirm you're testing your own server? (yes/no): ")
    if confirmation.lower() != "yes":
        print("[!] Test aborted by user")
        sys.exit(0)
    
    # Start the test
    if num_threads > 1:
        print("[*] Starting multi-threaded UDP test with %s threads" % num_threads)
        run_threads(target_ip, port, duration, packet_size, num_threads)
    else:
        send_udp_packets(target_ip, port, duration, packet_size)

if __name__ == "__main__":
    main()
