"""
Commute calculation service using OpenStreetMap and OSRM (free alternative)
"""

import os
import requests
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class CommuteService:
    """Service for calculating commute times using OpenStreetMap and OSRM (free)"""
    
    def __init__(self):
        # Nominatim for geocoding (free, no API key needed)
        self.geocode_url = "https://nominatim.openstreetmap.org/search"
        # OSRM for routing (free, no API key needed)
        self.routing_base_url = "https://router.project-osrm.org/route/v1"
        self.user_agent = "HouseScope/1.0"
        # Cache to avoid repeated geocoding of same addresses
        self._geocode_cache = {}
        print("[CACHE] Geocoding cache initialized")
    
    def _geocode_address(self, address: str, retry_count: int = 0) -> Optional[Dict]:
        """
        Convert address to coordinates using Nominatim (OpenStreetMap)
        
        Args:
            address: Street address to geocode
            retry_count: Number of retries attempted
            
        Returns:
            Dict with lat and lon, or None if failed
        """
        # Check cache first
        if address in self._geocode_cache:
            print(f"[CACHE] ✅ Using cached coordinates for: {address}")
            return self._geocode_cache[address]
        
        try:
            print(f"[GEOCODE] Starting geocode for: {address}")
            # Rate limiting: Nominatim requires 1 second between requests
            print(f"[GEOCODE] Waiting 1.2 seconds for rate limiting...")
            time.sleep(1.2)
            
            # Try different query formats for better results
            queries = [
                address,  # Original address
                address.replace("#", "Unit"),  # Handle apartment numbers
                address.split(",")[0] + ", USA"  # Just street + country
            ]
            
            for i, query in enumerate(queries):
                print(f"[GEOCODE] Attempt {i+1}/{len(queries)}: Trying query '{query}'")
                params = {
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "us"  # Restrict to USA for better results
                }
                
                headers = {
                    "User-Agent": self.user_agent
                }
                
                print(f"[GEOCODE] Sending request to Nominatim...")
                response = requests.get(
                    self.geocode_url, 
                    params=params, 
                    headers=headers, 
                    timeout=15
                )
                print(f"[GEOCODE] Response status: {response.status_code}")
                
                if response.status_code == 429 and retry_count < 2:
                    # Rate limited, wait longer and retry
                    print(f"[GEOCODE] Rate limited! Waiting 3 seconds and retrying...")
                    logger.warning(f"Rate limited, retrying after delay...")
                    time.sleep(3)
                    return self._geocode_address(address, retry_count + 1)
                
                response.raise_for_status()
                data = response.json()
                print(f"[GEOCODE] Got {len(data)} results")
                
                if data and len(data) > 0:
                    print(f"[GEOCODE] ✅ Success! Found: {data[0].get('display_name', '')}")
                    logger.info(f"Successfully geocoded: {address} -> {data[0].get('display_name', '')}")
                    result = {
                        "lat": float(data[0]["lat"]),
                        "lon": float(data[0]["lon"])
                    }
                    # Cache the result
                    self._geocode_cache[address] = result
                    print(f"[CACHE] Cached coordinates for: {address}")
                    return result
                
                # Wait between query variations
                print(f"[GEOCODE] No results, waiting 0.5s before trying next format...")
                time.sleep(0.5)
            
            print(f"[GEOCODE] ❌ Failed to geocode after trying all formats")
            logger.warning(f"Could not geocode address after trying multiple formats: {address}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"[GEOCODE] ❌ Network error: {e}")
            logger.error(f"Network error geocoding address: {e}")
            if retry_count < 2:
                print(f"[GEOCODE] Retrying after 2 seconds...")
                time.sleep(2)
                return self._geocode_address(address, retry_count + 1)
            return None
        except Exception as e:
            print(f"[GEOCODE] ❌ Unexpected error: {e}")
            logger.error(f"Error geocoding address: {e}")
            return None
    
    def calculate_commute(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        departure_time: str = "now"
    ) -> Optional[Dict]:
        """
        Calculate commute time from origin to destination using OSRM (free)
        
        Args:
            origin: Starting address (property address)
            destination: Destination address (work/school)
            mode: Transportation mode (driving, foot for walking, bicycle for bicycling)
                  Note: transit not supported by OSRM
            departure_time: Ignored (not used by OSRM)
            
        Returns:
            Dict with duration (seconds), duration_text, distance, and distance_text
        """
        try:
            # Geocode both addresses
            logger.info(f"Geocoding origin: {origin}")
            origin_coords = self._geocode_address(origin)
            
            if not origin_coords:
                logger.error(f"Failed to geocode origin: {origin}")
                return None
            
            logger.info(f"Geocoding destination: {destination}")
            dest_coords = self._geocode_address(destination)
            
            if not dest_coords:
                logger.error(f"Failed to geocode destination: {destination}")
                return None
            
            # Map mode to OSRM profile
            profile_map = {
                "driving": "car",
                "walking": "foot",
                "bicycling": "bike",
                "transit": "car"  # Fallback to car for transit
            }
            profile = profile_map.get(mode, "car")
            print(f"[ROUTING] Using profile: {profile}")
            
            # Build OSRM route URL
            # Format: /route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}
            url = f"{self.routing_base_url}/{profile}/{origin_coords['lon']},{origin_coords['lat']};{dest_coords['lon']},{dest_coords['lat']}"
            print(f"[ROUTING] Requesting route from OSRM...")
            
            params = {
                "overview": "false",
                "steps": "false"
            }
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"[ROUTING] Response status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                print(f"[ROUTING] ❌ OSRM error: {data.get('code')}")
                logger.error(f"OSRM routing error: {data.get('code')}")
                return None
            
            # Extract route information
            route = data["routes"][0]
            duration_seconds = route["duration"]
            distance_meters = route["distance"]
            print(f"[ROUTING] ✅ Route calculated successfully!")
            
            # Format text representations
            duration_minutes = int(duration_seconds / 60)
            duration_text = f"{duration_minutes} min" if duration_minutes > 0 else "< 1 min"
            
            distance_km = distance_meters / 1000
            distance_miles = distance_km * 0.621371
            distance_text = f"{distance_miles:.1f} mi"
            
            print(f"[ROUTING] Duration: {duration_text}, Distance: {distance_text}")
            
            return {
                "duration_seconds": int(duration_seconds),
                "duration_text": duration_text,
                "distance_meters": int(distance_meters),
                "distance_text": distance_text,
            }
            
        except Exception as e:
            print(f"[ROUTING] ❌ Error: {e}")
            logger.error(f"Error calculating commute: {e}")
            return None
    
    def check_property_commute_compatibility(
        self,
        property_address: str,
        roommates: List[Dict]
    ) -> Dict:
        """
        Check if a property meets commute requirements for all roommates
        
        Args:
            property_address: The property address
            roommates: List of dicts with keys: destination, max_commute_minutes, mode
            
        Returns:
            Dict with compatible (bool) and commute_details (list)
        """
        commute_details = []
        all_compatible = True
        
        for i, roommate in enumerate(roommates):
            destination = roommate.get("destination")
            max_minutes = roommate.get("max_commute_minutes")
            mode = roommate.get("mode", "driving")
            
            if not destination or not max_minutes:
                continue
            
            result = self.calculate_commute(
                origin=property_address,
                destination=destination,
                mode=mode
            )
            
            if result:
                duration_minutes = result["duration_seconds"] / 60
                is_compatible = duration_minutes <= max_minutes
                
                commute_details.append({
                    "roommate_index": i + 1,
                    "destination": destination,
                    "mode": mode,
                    "duration_minutes": round(duration_minutes, 1),
                    "duration_text": result["duration_text"],
                    "distance_text": result["distance_text"],
                    "max_allowed_minutes": max_minutes,
                    "compatible": is_compatible
                })
                
                if not is_compatible:
                    all_compatible = False
            else:
                # If we can't calculate, mark as incompatible
                all_compatible = False
                commute_details.append({
                    "roommate_index": i + 1,
                    "destination": destination,
                    "mode": mode,
                    "error": "Could not calculate commute",
                    "compatible": False
                })
        
        return {
            "compatible": all_compatible,
            "commute_details": commute_details
        }
