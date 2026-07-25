"""
World Bank WITS API client module.
Provides a clean interface to fetch trade data and metadata from the World Bank.
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import config

class WITSClient:
    """Client for interacting with the World Bank WITS API."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or config.WITS_BASE_URL
        self.timeout = timeout or config.REQUEST_TIMEOUT
    
    def _make_request(self, endpoint: str) -> Optional[bytes]:
        """Make a request to the WITS API and return the response content."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    def _parse_xml(self, xml_content: bytes) -> Optional[ET.Element]:
        """Parse XML content and return the root element."""
        if not xml_content:
            return None
        
        try:
            return ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return None
    
    def get_products(self) -> pd.DataFrame:
        """
        Fetch all available products from the WITS API.
        
        Returns:
            DataFrame with columns: productcode, productdescription, grouptype
        """
        endpoint = "wits/datasource/tradestats-trade/product/ALL"
        xml_content = self._make_request(endpoint)
        
        if not xml_content:
            return pd.DataFrame()
        
        root = self._parse_xml(xml_content)
        if not root:
            return pd.DataFrame()
        
        namespaces = {
            'wits': 'http://wits.worldbank.org'
        }
        
        products = []
        # Find all product elements
        for product in root.findall('.//wits:product', namespaces):
            product_data = {}
            # Extract product code and group type from attributes
            product_data['productcode'] = product.attrib.get('productcode')
            product_data['grouptype'] = product.attrib.get('grouptype')
            # Extract product description from child element
            desc_elem = product.find('wits:productdescription', namespaces)
            if desc_elem is not None:
                product_data['productdescription'] = desc_elem.text
            else:
                product_data['productdescription'] = None
            if product_data['productcode']:
                products.append(product_data)
        return pd.DataFrame(products)
    
    def get_reporters(self) -> pd.DataFrame:
        """
        Fetch all available reporting countries from the WITS API.
        
        Returns:
            DataFrame with columns: iso3code, name, isreporter
        """
        endpoint = "wits/datasource/tradestats-trade/country/ALL"
        xml_content = self._make_request(endpoint)
        
        if not xml_content:
            return pd.DataFrame()
        
        root = self._parse_xml(xml_content)
        if not root:
            return pd.DataFrame()
        
        namespaces = {
            'wits': 'http://wits.worldbank.org'
        }
        
        countries = []
        for country in root.findall('.//wits:country', namespaces):
            country_data = {}
            
            # Extract ISO3 code
            iso3_elem = country.find('wits:iso3Code', namespaces)
            if iso3_elem is not None:
                country_data['iso3code'] = iso3_elem.text
            
            # Extract country name (note: it's 'name', not 'countryname')
            name_elem = country.find('wits:name', namespaces)
            if name_elem is not None:
                country_data['name'] = name_elem.text
            
            # Extract isreporter flag
            isreporter = country.attrib.get('isreporter', '0')
            country_data['isreporter'] = isreporter
            
            if country_data:
                countries.append(country_data)
        
        return pd.DataFrame(countries)
    
    def get_partners(self) -> pd.DataFrame:
        """
        Fetch all available partner countries from the WITS API.
        
        Returns:
            DataFrame with columns: iso3code, name, ispartner
        """
        endpoint = "wits/datasource/tradestats-trade/country/ALL"
        xml_content = self._make_request(endpoint)
        
        if not xml_content:
            return pd.DataFrame()
        
        root = self._parse_xml(xml_content)
        if not root:
            return pd.DataFrame()
        
        namespaces = {
            'wits': 'http://wits.worldbank.org'
        }
        
        countries = []
        for country in root.findall('.//wits:country', namespaces):
            country_data = {}
            
            # Extract ISO3 code
            iso3_elem = country.find('wits:iso3Code', namespaces)
            if iso3_elem is not None:
                country_data['iso3code'] = iso3_elem.text
            
            # Extract country name (note: it's 'name', not 'countryname')
            name_elem = country.find('wits:name', namespaces)
            if name_elem is not None:
                country_data['name'] = name_elem.text
            
            # Extract ispartner flag
            ispartner = country.attrib.get('ispartner', '0')
            country_data['ispartner'] = ispartner
            
            if country_data:
                countries.append(country_data)
        
        return pd.DataFrame(countries)
    
    def get_indicators(self) -> pd.DataFrame:
        """
        Fetch all available indicators from the WITS API.
        
        Returns:
            DataFrame with columns: indicatorcode, name
        """
        endpoint = "wits/datasource/tradestats-trade/indicator/ALL"
        xml_content = self._make_request(endpoint)
        
        if not xml_content:
            return pd.DataFrame()
        
        root = self._parse_xml(xml_content)
        if not root:
            return pd.DataFrame()
        
        namespaces = {
            'wits': 'http://wits.worldbank.org'
        }
        
        indicators = []
        for indicator in root.findall('.//wits:indicator', namespaces):
            indicator_data = {}
            
            # Extract indicator code
            code_elem = indicator.attrib.get('indicatorcode')
            if code_elem:
                indicator_data['indicatorcode'] = code_elem
            
            # Extract indicator name (note: it's 'name', not 'indicatorname')
            name_elem = indicator.find('wits:name', namespaces)
            if name_elem is not None:
                indicator_data['name'] = name_elem.text
            
            if indicator_data:
                indicators.append(indicator_data)
        
        return pd.DataFrame(indicators)

# Create a global client instance
_client = WITSClient()

# Convenience functions
def get_products() -> pd.DataFrame:
    """Get all available products."""
    return _client.get_products()

def get_reporters() -> pd.DataFrame:
    """Get all available reporting countries."""
    return _client.get_reporters()

def get_partners() -> pd.DataFrame:
    """Get all available partner countries."""
    return _client.get_partners()

def get_indicators() -> pd.DataFrame:
    """Get all available indicators."""
    return _client.get_indicators() 