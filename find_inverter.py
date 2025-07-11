"""
Script to find Fronius inverters on the local network.
This script scans the local network for Fronius inverters by checking
common Fronius API endpoints.
"""

import requests
import socket
import ipaddress
import concurrent.futures
from typing import List, Optional

def get_local_ip() -> str:
    """Get the local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_network_range() -> List[str]:
    """Get list of IP addresses in the local network."""
    local_ip = get_local_ip()
    network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    return [str(ip) for ip in network.hosts()]

def check_fronius(ip: str) -> Optional[str]:
    """Check if a Fronius inverter is at the given IP address."""
    try:
        # Try the common Fronius API endpoint
        url = f"http://{ip}/solar_api/GetPowerFlowRealtimeData.fcgi"
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return ip
    except:
        pass
    return None

def find_inverters() -> List[str]:
    """Find all Fronius inverters on the local network."""
    print("Scanning network for Fronius inverters...")
    print("This might take a few minutes...")
    
    network = get_network_range()
    found_inverters = []
    
    # Use ThreadPoolExecutor to scan IPs in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(check_fronius, ip): ip for ip in network}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                result = future.result()
                if result:
                    found_inverters.append(result)
                    print(f"\nFound Fronius inverter at: {result}")
            except Exception as e:
                print(f"Error checking {ip}: {e}")
    
    return found_inverters

def main():
    """Main function to find inverters and update configuration."""
    print("Parra Energy - Fronius Inverter Finder")
    print("=====================================")
    
    found_inverters = find_inverters()
    
    if not found_inverters:
        print("\nNo Fronius inverters found on the network.")
        print("Please check that:")
        print("1. Your inverter is powered on")
        print("2. You're connected to the same network as the inverter")
        print("3. The inverter's network settings are correct")
    else:
        print("\nFound inverters:")
        for i, ip in enumerate(found_inverters, 1):
            print(f"{i}. {ip}")
        
        print("\nTo use an inverter, update the host in parra_energy/web/app.py:")
        print("fronius = FroniusClient(host=\"YOUR_INVERTER_IP\")")

if __name__ == "__main__":
    main() 