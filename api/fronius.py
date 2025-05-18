import requests
from typing import Dict, Optional

class FroniusClient:
    def __init__(self, host: str, port: int = 80):
        """Initialize the Fronius API client.
        
        Args:
            host: The IP address or hostname of the Fronius inverter
            port: The port number (default: 80)
        """
        self.base_url = f"http://{host}:{port}"
        
    def get_power_data(self) -> Dict:
        """Fetch current power data from the Fronius inverter.
        
        Returns:
            Dict containing power data (P_PV, P_Load, P_Grid)
        """
        # Endpoint for power flow data
        url = f"{self.base_url}/solar_api/GetPowerFlowRealtimeData.fcgi"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant power data
            power_data = {
                'P_PV': data.get('Body', {}).get('Data', {}).get('Site', {}).get('P_PV', 0),
                'P_Load': data.get('Body', {}).get('Data', {}).get('Site', {}).get('P_Load', 0),
                'P_Grid': data.get('Body', {}).get('Data', {}).get('Site', {}).get('P_Grid', 0)
            }
            
            return power_data
            
        except requests.RequestException as e:
            print(f"Error fetching power data: {e}")
            return {'P_PV': 0, 'P_Load': 0, 'P_Grid': 0} 