"""
Airport Service
Handles airport/city code mapping using multiple approaches
"""
from typing import Optional, Dict, Any
import logging
import json
import os

logger = logging.getLogger(__name__)


class AirportService:
    """Service for airport/city code mapping and lookup"""
    
    def __init__(self):
        # Comprehensive airport database with major cities
        self.airport_database = {
            # Indian cities
            'bangalore': 'BLR', 'bengaluru': 'BLR',
            'mumbai': 'BOM', 'bombay': 'BOM',
            'delhi': 'DEL', 'new delhi': 'DEL',
            'chennai': 'MAA', 'madras': 'MAA',
            'kolkata': 'CCU', 'calcutta': 'CCU',
            'hyderabad': 'HYD',
            'pune': 'PNQ',
            'ahmedabad': 'AMD',
            'jaipur': 'JAI',
            'kochi': 'COK', 'cochin': 'COK',
            'goa': 'GOI',
            'kerala': 'COK',
            'rajasthan': 'JAI',
            'tamil nadu': 'MAA',
            'karnataka': 'BLR',
            'maharashtra': 'BOM',
            'west bengal': 'CCU',
            'gujarat': 'AMD',
            
            # International cities
            'paris': 'CDG',
            'london': 'LHR',
            'new york': 'JFK', 'nyc': 'JFK',
            'tokyo': 'NRT',
            'singapore': 'SIN',
            'dubai': 'DXB',
            'bangkok': 'BKK',
            'bali': 'DPS', 'denpasar': 'DPS', 'ubud': 'DPS',
            'sydney': 'SYD',
            'melbourne': 'MEL',
            'toronto': 'YYZ',
            'vancouver': 'YVR',
            'los angeles': 'LAX', 'la': 'LAX',
            'san francisco': 'SFO', 'sf': 'SFO',
            'chicago': 'ORD',
            'miami': 'MIA',
            'las vegas': 'LAS',
            'seattle': 'SEA',
            'boston': 'BOS',
            'atlanta': 'ATL',
            'denver': 'DEN',
            'phoenix': 'PHX',
            'dallas': 'DFW',
            'houston': 'IAH',
            'detroit': 'DTW',
            'minneapolis': 'MSP',
            'orlando': 'MCO',
            'tampa': 'TPA',
            'charlotte': 'CLT',
            'philadelphia': 'PHL',
            'washington': 'DCA', 'dc': 'DCA',
            'baltimore': 'BWI',
            'salt lake city': 'SLC',
            'portland': 'PDX',
            'san diego': 'SAN',
            'austin': 'AUS',
            'nashville': 'BNA',
            'kansas city': 'MCI',
            'columbus': 'CMH',
            'indianapolis': 'IND',
            'milwaukee': 'MKE',
            'cleveland': 'CLE',
            'cincinnati': 'CVG',
            'pittsburgh': 'PIT',
            'buffalo': 'BUF',
            'rochester': 'ROC',
            'albany': 'ALB',
            'syracuse': 'SYR',
            'burlington': 'BTV',
            'portland': 'PWM',
            'manchester': 'MHT',
            'providence': 'PVD',
            'hartford': 'BDL',
            'newark': 'EWR',
            'jersey city': 'EWR',
            'richmond': 'RIC',
            'norfolk': 'ORF',
            'virginia beach': 'ORF',
            'raleigh': 'RDU',
            'greensboro': 'GSO',
            'charleston': 'CHS',
            'savannah': 'SAV',
            'jacksonville': 'JAX',
            'tallahassee': 'TLH',
            'gainesville': 'GNV',
            'fort lauderdale': 'FLL',
            'west palm beach': 'PBI',
            'key west': 'EYW',
            'pensacola': 'PNS',
            'mobile': 'MOB',
            'birmingham': 'BHM',
            'montgomery': 'MGM',
            'huntsville': 'HSV',
            'memphis': 'MEM',
            'knoxville': 'TYS',
            'chattanooga': 'CHA',
            'louisville': 'SDF',
            'lexington': 'LEX',
            'bowling green': 'BWG',
            'evansville': 'EVV',
            'fort wayne': 'FWA',
            'south bend': 'SBN',
            'grand rapids': 'GRR',
            'lansing': 'LAN',
            'flint': 'FNT',
            'saginaw': 'MBS',
            'marquette': 'MQT',
            'duluth': 'DLH',
            'minneapolis': 'MSP',
            'st paul': 'MSP',
            'rochester': 'RST',
            'mankato': 'MKT',
            'sioux falls': 'FSD',
            'rapid city': 'RAP',
            'bismarck': 'BIS',
            'fargo': 'FAR',
            'grand forks': 'GFK',
            'minot': 'MOT',
            'williston': 'ISN',
            'billings': 'BIL',
            'bozeman': 'BZN',
            'missoula': 'MSO',
            'kalispell': 'FCA',
            'great falls': 'GTF',
            'helena': 'HLN',
            'butte': 'BTM',
            'sidney': 'SDY',
            'glendive': 'GDV',
            'havre': 'HVR',
            'miles city': 'MLS',
            'wolf point': 'OLF',
            'plentywood': 'PWD',
            'scobey': 'SCB',
            'poplar': 'POQ',
            'malta': 'MLL',
            'glasgow': 'GGW',
            'jordan': 'JDN',
            'circle': 'CIR',
            'sidney': 'SDY',
            'glendive': 'GDV',
            'havre': 'HVR',
            'miles city': 'MLS',
            'wolf point': 'OLF',
            'plentywood': 'PWD',
            'scobey': 'SCB',
            'poplar': 'POQ',
            'malta': 'MLL',
            'glasgow': 'GGW',
            'jordan': 'JDN',
            'circle': 'CIR',
            
            # European cities
            'berlin': 'BER',
            'munich': 'MUC',
            'frankfurt': 'FRA',
            'hamburg': 'HAM',
            'cologne': 'CGN',
            'düsseldorf': 'DUS',
            'stuttgart': 'STR',
            'nuremberg': 'NUE',
            'leipzig': 'LEJ',
            'dresden': 'DRS',
            'hannover': 'HAJ',
            'bremen': 'BRE',
            'rome': 'FCO',
            'milan': 'MXP',
            'venice': 'VCE',
            'florence': 'FLR',
            'naples': 'NAP',
            'bologna': 'BLQ',
            'turin': 'TRN',
            'palermo': 'PMO',
            'catania': 'CTA',
            'madrid': 'MAD',
            'barcelona': 'BCN',
            'valencia': 'VLC',
            'seville': 'SVQ',
            'bilbao': 'BIO',
            'malaga': 'AGP',
            'alicante': 'ALC',
            'palma': 'PMI',
            'lisbon': 'LIS',
            'porto': 'OPO',
            'amsterdam': 'AMS',
            'rotterdam': 'RTM',
            'eindhoven': 'EIN',
            'brussels': 'BRU',
            'antwerp': 'ANR',
            'charleroi': 'CRL',
            'vienna': 'VIE',
            'salzburg': 'SZG',
            'innsbruck': 'INN',
            'zurich': 'ZUR',
            'geneva': 'GVA',
            'basel': 'BSL',
            'bern': 'BRN',
            'stockholm': 'ARN',
            'gothenburg': 'GOT',
            'malmo': 'MMX',
            'oslo': 'OSL',
            'bergen': 'BGO',
            'trondheim': 'TRD',
            'copenhagen': 'CPH',
            'aarhus': 'AAR',
            'helsinki': 'HEL',
            'tampere': 'TMP',
            'turku': 'TKU',
            'warsaw': 'WAW',
            'krakow': 'KRK',
            'gdansk': 'GDN',
            'wroclaw': 'WRO',
            'prague': 'PRG',
            'brno': 'BRQ',
            'budapest': 'BUD',
            'debrecen': 'DEB',
            'bucharest': 'OTP',
            'cluj': 'CLJ',
            'timisoara': 'TSR',
            'sofia': 'SOF',
            'plovdiv': 'PDV',
            'zagreb': 'ZAG',
            'split': 'SPU',
            'dubrovnik': 'DBV',
            'ljubljana': 'LJU',
            'maribor': 'MBX',
            'bratislava': 'BTS',
            'kosice': 'KSC',
            'vilnius': 'VNO',
            'kaunas': 'KUN',
            'riga': 'RIX',
            'liepaja': 'LPX',
            'tallinn': 'TLL',
            'tartu': 'TAY',
            'reykjavik': 'KEF',
            'akureyri': 'AEY',
            'dublin': 'DUB',
            'cork': 'ORK',
            'shannon': 'SNN',
            'belfast': 'BFS',
            'glasgow': 'GLA',
            'edinburgh': 'EDI',
            'aberdeen': 'ABZ',
            'manchester': 'MAN',
            'birmingham': 'BHX',
            'liverpool': 'LPL',
            'leeds': 'LBA',
            'newcastle': 'NCL',
            'bristol': 'BRS',
            'cardiff': 'CWL',
            'southampton': 'SOU',
            'bournemouth': 'BOH',
            'exeter': 'EXT',
            'plymouth': 'PLH',
            'norwich': 'NWI',
            'humberside': 'HUY',
            'durham': 'MME',
            'teesside': 'MME',
            'doncaster': 'DSA',
            'east midlands': 'EMA',
            'london luton': 'LTN',
            'london stansted': 'STN',
            'london gatwick': 'LGW',
            'london city': 'LCY',
            'london southend': 'SEN',
            'london heathrow': 'LHR',
        }
    
    def get_airport_code(self, city_name: str) -> str:
        """
        Get IATA airport code for a city name
        
        Args:
            city_name: Name of the city (e.g., "Bangalore", "Mumbai", "Paris")
            
        Returns:
            IATA airport code (e.g., "BLR", "BOM", "CDG") or "LAX" as fallback
        """
        try:
            # Clean the city name
            clean_city = city_name.strip().lower()
            
            # Direct match
            if clean_city in self.airport_database:
                code = self.airport_database[clean_city]
                logger.info(f"Found direct match: '{city_name}' -> '{code}'")
                return code
            
            # Partial match for compound names
            for key, code in self.airport_database.items():
                if key in clean_city or clean_city in key:
                    logger.info(f"Found partial match: '{city_name}' -> '{code}' (via '{key}')")
                    return code
            
            # Try common variations
            variations = [
                clean_city.replace(" ", ""),
                clean_city.split()[0] if " " in clean_city else clean_city,
                clean_city.replace("-", " "),
                clean_city.replace("_", " "),
            ]
            
            for variation in variations:
                if variation in self.airport_database:
                    code = self.airport_database[variation]
                    logger.info(f"Found variation match: '{city_name}' -> '{code}' (via '{variation}')")
                    return code
            
            # Try Amadeus location API as fallback
            try:
                amadeus_code = self._get_amadeus_city_code(city_name)
                if amadeus_code and amadeus_code != "LAX":
                    logger.info(f"Found Amadeus match: '{city_name}' -> '{amadeus_code}'")
                    return amadeus_code
            except Exception as e:
                logger.debug(f"Amadeus lookup failed for '{city_name}': {e}")
            
            logger.warning(f"No airport code found for city '{city_name}', using LAX as fallback")
            return "LAX"
            
        except Exception as e:
            logger.error(f"Error getting airport code for '{city_name}': {e}")
            return "LAX"
    
    def _get_amadeus_city_code(self, city_name: str) -> Optional[str]:
        """
        Try to get city code from Amadeus location API
        
        Args:
            city_name: Name of the city
            
        Returns:
            City code from Amadeus or None
        """
        try:
            import httpx
            from app.config import settings
            
            # Use Amadeus location API
            url = "https://test.api.amadeus.com/v1/reference-data/locations"
            params = {
                "subType": "CITY",
                "keyword": city_name
            }
            headers = {
                "Authorization": f"Bearer {self._get_amadeus_token()}"
            }
            
            with httpx.Client() as client:
                response = client.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                if data.get("data") and len(data["data"]) > 0:
                    # Return the first city code found
                    city_code = data["data"][0].get("iataCode")
                    if city_code:
                        return city_code
                
            return None
            
        except Exception as e:
            logger.debug(f"Amadeus location API error for '{city_name}': {e}")
            return None
    
    def _get_amadeus_token(self) -> str:
        """Get Amadeus access token (simplified version)"""
        try:
            import httpx
            from app.config import settings
            
            url = "https://test.api.amadeus.com/v1/security/oauth2/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": settings.amadeus_api_key,
                "client_secret": settings.amadeus_api_secret
            }
            
            with httpx.Client() as client:
                response = client.post(url, data=data, timeout=10.0)
                response.raise_for_status()
                
                token_data = response.json()
                return token_data.get("access_token", "")
                
        except Exception as e:
            logger.debug(f"Amadeus token error: {e}")
            return ""
    
    def get_airport_info(self, airport_code: str) -> Optional[Dict[str, Any]]:
        """
        Get airport information by IATA code
        
        Args:
            airport_code: IATA airport code (e.g., "BLR", "BOM")
            
        Returns:
            Dictionary with airport information or None
        """
        # This could be extended to use external APIs or databases
        # For now, return basic info
        return {
            'iata': airport_code,
            'name': f"Airport {airport_code}",
            'city': 'Unknown',
            'country': 'Unknown'
        }


# Global service instance
airport_service = AirportService()


def get_airport_service() -> AirportService:
    """Get the global airport service instance"""
    return airport_service