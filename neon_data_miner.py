"""
NEON Data Miner - Access National Ecological Observatory Network Data
Demonstrates various ways to extract and analyze NEON ecological data
"""

import requests
import json
import pandas as pd
from datetime import datetime

class NEONDataMiner:
    """
    Interface to NEON's API for ecological data mining
    """
    
    def __init__(self):
        self.base_url = "https://data.neonscience.org/api/v0"
        
    def get_all_sites(self):
        """Get list of all NEON field sites with metadata"""
        endpoint = f"{self.base_url}/sites"
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()
            sites_df = pd.DataFrame(data['data'])
            return sites_df
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def get_site_details(self, site_code):
        """Get detailed information about a specific site"""
        endpoint = f"{self.base_url}/sites/{site_code}"
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            return response.json()['data']
        return None
    
    def get_available_products(self):
        """Get all available data products"""
        endpoint = f"{self.base_url}/products"
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            products = response.json()['data']
            products_df = pd.DataFrame(products)
            return products_df
        return None
    
    def get_product_details(self, product_code):
        """Get details about a specific data product"""
        endpoint = f"{self.base_url}/products/{product_code}"
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            return response.json()['data']
        return None
    
    def get_product_availability(self, product_code, site_code=None):
        """
        Check data availability for a product, optionally filtered by site
        Example product codes:
        - DP1.10003.001: Breeding landbird point counts
        - DP1.20002.001: Chemical properties of groundwater
        - DP1.10055.001: Plant phenology observations
        """
        endpoint = f"{self.base_url}/products/{product_code}"
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()['data']
            
            # Get site-month combinations
            if 'siteCodes' in data:
                availability = []
                for site in data['siteCodes']:
                    if site_code is None or site['siteCode'] == site_code:
                        for month in site.get('availableMonths', []):
                            availability.append({
                                'site': site['siteCode'],
                                'month': month,
                                'data_urls': site.get('availableDataUrls', [])
                            })
                
                return pd.DataFrame(availability)
        return None
    
    def download_data_urls(self, product_code, site_code, year_month):
        """
        Get download URLs for specific product/site/time
        year_month format: 'YYYY-MM'
        """
        endpoint = f"{self.base_url}/data/{product_code}/{site_code}/{year_month}"
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            data = response.json()['data']
            files = data.get('files', [])
            
            file_info = []
            for f in files:
                file_info.append({
                    'name': f.get('name'),
                    'url': f.get('url'),
                    'size': f.get('size'),
                    'crc32': f.get('crc32')
                })
            
            return pd.DataFrame(file_info)
        return None
    
    def search_products_by_keyword(self, keyword):
        """Search for data products containing a keyword"""
        products = self.get_available_products()
        
        if products is not None:
            mask = products['productName'].str.contains(keyword, case=False, na=False) | \
                   products['productDescription'].str.contains(keyword, case=False, na=False)
            return products[mask]
        return None
    
    def get_spatial_data(self):
        """
        Get spatial data endpoints
        Note: Actual shapefiles need to be downloaded separately from:
        https://www.neonscience.org/data-samples/data/spatial-data-maps
        """
        spatial_info = {
            'domains': 'https://www.neonscience.org/sites/default/files/NEON_Domains_0.zip',
            'field_sites': 'https://www.neonscience.org/sites/default/files/NEON_Field_Sites.zip',
            'plot_locations': 'https://www.neonscience.org/sites/default/files/NEON_TOS_Plot_Points.zip',
            'flight_boundaries': 'https://www.neonscience.org/sites/default/files/NEON_AOP_flightboxes.zip'
        }
        return spatial_info


# Example Usage Functions
def example_explore_sites(miner):
    """Explore all NEON sites"""
    print("\n=== EXPLORING NEON SITES ===")
    sites = miner.get_all_sites()
    
    if sites is not None:
        print(f"\nTotal sites: {len(sites)}")
        print("\nSite types:")
        print(sites['siteType'].value_counts())
        print("\nSample sites:")
        print(sites[['siteCode', 'siteName', 'siteType', 'domainCode', 'stateCode']].head(10))
        
        return sites
    return None


def example_search_bird_data(miner):
    """Find bird-related data products"""
    print("\n=== SEARCHING FOR BIRD DATA ===")
    bird_products = miner.search_products_by_keyword('bird')
    
    if bird_products is not None:
        print(f"\nFound {len(bird_products)} bird-related products")
        print("\nProducts:")
        print(bird_products[['productCode', 'productName']].to_string(index=False))
        
        return bird_products
    return None


def example_get_product_availability(miner, product_code='DP1.10003.001'):
    """Check where and when breeding bird data is available"""
    print(f"\n=== CHECKING AVAILABILITY FOR {product_code} ===")
    
    # Get product details
    details = miner.get_product_details(product_code)
    if details:
        print(f"\nProduct: {details['productName']}")
        print(f"Description: {details['productDescription'][:200]}...")
    
    # Get availability
    availability = miner.get_product_availability(product_code)
    
    if availability is not None:
        print(f"\nTotal site-months available: {len(availability)}")
        print(f"\nSites with data: {availability['site'].nunique()}")
        print("\nSample availability:")
        print(availability.head(10))
        
        return availability
    return None


def example_download_urls(miner, product_code='DP1.10003.001', 
                         site_code='HARV', year_month='2023-06'):
    """Get actual download URLs for specific data"""
    print(f"\n=== GETTING DOWNLOAD URLS ===")
    print(f"Product: {product_code}")
    print(f"Site: {site_code}")
    print(f"Month: {year_month}")
    
    files = miner.download_data_urls(product_code, site_code, year_month)
    
    if files is not None:
        print(f"\nAvailable files: {len(files)}")
        print("\nFile details:")
        print(files[['name', 'size']].head(10))
        print(f"\nTotal data size: {files['size'].sum() / 1_000_000:.2f} MB")
        
        return files
    return None


def main():
    """Main demonstration of NEON data mining capabilities"""
    
    print("=" * 60)
    print("NEON DATA MINER - Ecological Observatory Network")
    print("=" * 60)
    
    # Initialize miner
    miner = NEONDataMiner()
    
    # Example 1: Explore all sites
    sites = example_explore_sites(miner)
    
    # Example 2: Search for specific data types
    bird_products = example_search_bird_data(miner)
    
    # Example 3: Check product availability
    availability = example_get_product_availability(miner)
    
    # Example 4: Get actual download URLs
    files = example_download_urls(miner)
    
    # Show spatial data sources
    print("\n=== SPATIAL DATA SOURCES ===")
    spatial = miner.get_spatial_data()
    for name, url in spatial.items():
        print(f"{name}: {url}")
    
    print("\n" + "=" * 60)
    print("Mining complete! Check the DataFrames for analysis.")
    print("=" * 60)


if __name__ == "__main__":
    main()
