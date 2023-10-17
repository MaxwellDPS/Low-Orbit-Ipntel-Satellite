"""
Djano Project peeps...
Feel free to steal and fix that shit so I dont have to think about this stupid again
"""
from datetime import tzinfo
from ipaddress import ip_network, IPv4Network, IPv6Network

import pytz
import flag
import geoip2.records

networxx = IPv4Network | IPv6Network

def get_flag(iso_code: int) -> str:
    """
    Gets a ISO flag if it exists
    """
    if not iso_code:
        return None

    try:
        return flag.flag(iso_code.strip())
    except ValueError:
        pass

    return None

class Region(object):
    """
    Handle regions as a class
    """
    def __init__(self, _region: geoip2.records.Subdivision, **kwargs) -> None:
        self.name: str = _region.name if _region else None
        self.iso_code: int = _region.iso_code if _region else None
        self.confidence: int = _region.confidence if _region else None
        self.names: list[str] = _region.name if _region else None
        self.flag: str = get_flag(self.iso_code) if _region else None

class Continent(object):
    """
    Class to represent Continent
    """
    def __init__(self, _continent: geoip2.records.Continent = None, **kwargs) -> None:
        self.name: str = _continent.name
        self.names: list[str] = _continent.names
        self.code: int = _continent.code

class Country(object):
    """
    Class to represent Country
    """
    def __init__(self, _country: geoip2.records.Country = None, **kwargs) -> None:
        self.name: str = _country.name
        self.european_union: bool = _country.is_in_european_union
        self.names: list[str] = _country.names
        self.iso_code: int = _country.iso_code
        self.flag: str = get_flag(self.iso_code)
        self.confidence: int = _country.confidence

class Postal(object):
    """
    Class to represent PostalCodes
    """
    def __init__(self,  _postal: geoip2.records.Postal = None, **kwargs) -> None:
        self.code: str = _postal.code
        self.confidence: int = _postal.confidence

class ASN(object):
    """
    Class to represent ASNs
    """
    def __init__(self, _response, **kwargs) -> None:
        self.autonomous_system_organization: str = _response.autonomous_system_organization
        self.autonomous_system_number: int = _response.autonomous_system_number
        self.network: networxx = ip_network(_response.network)

class City(object):
    """
    Class to represent City
    """

    def __init__(self, _response, **kwargs) -> None:
        _city: geoip2.records.City                          = _response.city
        _subdivisions: list[geoip2.records.Subdivision]     = _response.subdivisions
        _country: geoip2.records.Continent                  = _response.country
        _continent: geoip2.records.Continent                = _response.continent
        _location: geoip2.records.Location                  = _response.location
        _go_postal: geoip2.records.Postal                   = _response.postal    # FR tho mad respect to the real bois in blue Keep that mail flowin 📫

        self.name: str                  = _city.name
        self.confidence: int            = _city.confidence
        self.names: list[str]           = _city.names

        self.country: Country           = Country(_country)
        self.continent: Continent       = Continent(_continent)
        self.postal_code: Postal        = Postal(_go_postal)

        self.regions: list[Region]      = self._populate_regions(_subdivisions)
        self.region: Region             = self.regions[0] if self.regions else None

        self.flags: list[str]           = self._get_flags()
        self.flag: str                  = self.flags[0] if self.flags else None

        self.latitude: float            = _location.latitude
        self.longitude: float           = _location.longitude
        self.metro_code: int            = _location.metro_code
        self.accuracy_radius: int       = _location.accuracy_radius
        self.average_income: int        = _location.average_income
        self.population_density: int    = _location.population_density
        self.time_zone: tzinfo          = pytz.timezone(_location.time_zone)


    def _get_flags(self):
        flags = []
        if self.country and self.country.flag:
            flags.append(self.country.flag)
        if self.region and self.region.flag:
            flags.append(self.region.flag)
        return flags

    def _populate_regions(self, subdivisions: list[geoip2.records.Subdivision]) -> list[Region]:
        results = []
        if subdivisions:
            for region in subdivisions:
                results.append(Region(region))
        return results

class GeoIP2Exception(Exception):
    """
    Django GeoIP2 Exeception
    """
