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
    """Service for calculating commute times using OpenStreetMap and OSRM"""
    
    def __init__(self):
        self.geocode_url = "https://nominatim.openstreetmap.org/search"
        self.routing_base_url = "https://router.project-osrm.org/route/v1"
        self.user_agent = "HouseScope/1.0"
        self._geocode_cache = {}
    
    def _geocode_address(self, address: str, retry_count: int = 0) -> Optional[Dict]:
        """Convert address to coordinates using Nominatim"""
        if address in self._geocode_cache:
            return self._geocode_cache[address]
        
        try:
            time.sleep(1.2)
            
            queries = [
                address,
                address.replace("#", "Unit"),
                address.split(",")[0] + ", USA"
            ]
            
            for query in queries:
                params = {
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "us"
                }
                
                headers = {
                    "User-Agent": self.user_agent
                }
                
                response = requests.get(
                    self.geocode_url, 
                    params=params, 
                    headers=headers, 
                    timeout=15
                )
                
                if response.status_code == 429 and retry_count < 2:
                    logger.warning(f"Rate limited, retrying after delay")
                    time.sleep(3)
                    return self._geocode_address(address, retry_count + 1)
                
                response.raise_for_status()
                data = response.json()
                
                if data and len(data) > 0:
                    logger.info(f"Successfully geocoded: {address}")
                    result = {
                        "lat": float(data[0]["lat"]),
                        "lon": float(data[0]["lon"])
                    }
                    self._geocode_cache[address] = result
                    return result
                
                time.sleep(0.5)
            
            logger.warning(f"Could not geocode address: {address}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error geocoding address: {e}")
            if retry_count < 2:
                time.sleep(2)
                return self._geocode_address(address, retry_count + 1)
            return None
        except Exception as e:
            logger.error(f"Error geocoding address: {e}")
            return None
    
    def calculate_commute(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        departure_time: str = "now"
    ) -> Optional[Dict]:
        """Calculate commute time from origin to destination using OSRM"""
        try:
            logger.info(f"Calculating commute: {origin} -> {destination}")
            origin_coords = self._geocode_address(origin)
            
            if not origin_coords:
                logger.error(f"Failed to geocode origin: {origin}")
                return None
            
            dest_coords = self._geocode_address(destination)
            
            if not dest_coords:
                logger.error(f"Failed to geocode destination: {destination}")
                return None
            
            profile_map = {
                "driving": "car",
                "walking": "foot",
                "bicycling": "bike",
                "transit": "car"
            }
            profile = profile_map.get(mode, "car")
            
            url = f"{self.routing_base_url}/{profile}/{origin_coords['lon']},{origin_coords['lat']};{dest_coords['lon']},{dest_coords['lat']}"
            
            params = {
                "overview": "false",
                "steps": "false"
            }
            
            headers = {
                "User-Agent": self.user_agent
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("code") != "Ok":
                logger.error(f"OSRM routing error: {data.get('code')}")
                return None
            
            route = data["routes"][0]
            duration_seconds = route["duration"]
            distance_meters = route["distance"]
            
            duration_minutes = int(duration_seconds / 60)
            duration_text = f"{duration_minutes} min" if duration_minutes > 0 else "< 1 min"
            
            distance_km = distance_meters / 1000
            distance_miles = distance_km * 0.621371
            distance_text = f"{distance_miles:.1f} mi"
            
            return {
                "duration_seconds": int(duration_seconds),
                "duration_text": duration_text,
                "distance_meters": int(distance_meters),
                "distance_text": distance_text,
            }
            
        except Exception as e:
            logger.error(f"Error calculating commute: {e}")
            return None
    
    def check_property_commute_compatibility(
        self,
        property_address: str,
        roommates: List[Dict]
    ) -> Dict:
        """Check if a property meets commute requirements for all roommates"""
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
