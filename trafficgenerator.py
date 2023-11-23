import argparse
import netifaces
import requests
import datetime
from scapy.all import IP, TCP, send
from tqdm import tqdm

def get_ipv4_address(interface):
    addresses = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addresses:
        return addresses[netifaces.AF_INET][0]['addr']
    else:
        raise ValueError(f"No IPv4 address found on interface {interface}!")

def generate_traffic(source_ip, destination_ip, destination_port, packet_count, use_web):
    requests_sent = 0  # Counter to keep track of requests sent
    
    if use_web:
        headers = {'Custom-Header': 'synack'}  # Custom header
        with tqdm(total=packet_count, desc="Sending requests") as pbar:
            for _ in range(packet_count):
                url = f"http://{destination_ip}:{destination_port}/"
                try:
                    start_time = datetime.datetime.now()
                    response = requests.get(url, headers=headers)
                    end_time = datetime.datetime.now()
                    status_code = response.status_code
                    color = "\033[32m" if status_code == 200 else "\033[31m"
                    print(f"[{start_time}] Response: {color}{status_code}\033[0m [{end_time}]")
                    requests_sent += 1
                    pbar.update(1)
                except requests.exceptions.RequestException as e:
                    color = "\033[31m"  # Red color
                    print(f"{color}[{datetime.datetime.now()}] No connection possible\033[0m")
                    pbar.update(1)
    else:
        with tqdm(total=packet_count, desc="Sending packets") as pbar:
            for _ in range(packet_count):
                packet = IP(src=source_ip, dst=destination_ip) / TCP(dport=destination_port)
                packet.time = datetime.datetime.now().timestamp()  # Set packet timestamp
                send(packet)
                pbar.update(1)

    if use_web:
        print(f"\nTotal requests sent: {requests_sent}")
    else:
        print(f"\nTotal packets sent: {packet_count}")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Traffic Generator')
parser.add_argument('destination_ip', type=str, help='Destination IP address')
parser.add_argument('--interface', type=str, default=None, help='Network interface name')
parser.add_argument('--port', type=int, default=80, help='Destination port (default: 80)')
parser.add_argument('--count', type=int, default=10, help='Number of packets to send (default: 10)')
parser.add_argument('--web', action='store_true', help='Use web (curl) requests instead of network packets')
args = parser.parse_args()

# Get the source IP address
if args.interface is not None:
    source_ip = get_ipv4_address(args.interface)
else:
    source_ip = netifaces.gateways()['default'][netifaces.AF_INET][0]

# Generate traffic using command-line inputs
generate_traffic(source_ip, args.destination_ip, args.port, args.count, args.web)
