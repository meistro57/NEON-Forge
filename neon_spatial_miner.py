"""
NEON Spatial Data Miner - Access GIS layers from ArcGIS REST API
Works with the NEON ArcGIS Online portal
"""

import requests
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, shape
import folium
from typing import Optional, Dict, List

class NEONSpatialMiner:
    """
    Access NEON's ArcGIS REST API for spatial/GIS data
    """
    
    def __init__(self):
        self.arcgis_base = "https://neon.maps.arcgis.com/sharing/rest"
        self.feature_service_base = "https://services.arcgis.com"
        
    def query_feature_layer(self, service_url: str, where_clause: str = "1=1", 
                           return_geometry: bool = True, out_fields: str = "*",
                           result_record_count: int = 1000) -> Optional[gpd.GeoDataFrame]:
        """
        Query a feature layer from ArcGIS REST API
        
        Args:
            service_url: Full URL to the feature layer
            where_clause: SQL where clause (default "1=1" returns all)
            return_geometry: Whether to include geometry
            out_fields: Fields to return (* for all)
            result_record_count: Max records to return
        """
        
        query_url = f"{service_url}/query"
        
        params = {
            'where': where_clause,
            'outFields': out_fields,
            'returnGeometry': str(return_geometry).lower(),
            'f': 'geojson',
            'resultRecordCount': result_record_count
        }
        
        try:
            response = requests.get(query_url, params=params)
            
            if response.status_code == 200:
                geojson_data = response.json()
                
                if 'features' in geojson_data:
                    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
                    
                    # Set CRS if available
                    if 'crs' in geojson_data:
                        gdf.crs = "EPSG:4326"  # WGS84
                    
                    return gdf
            else:
                print(f"Error querying feature layer: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Exception querying feature layer: {e}")
            return None
    
    def get_neon_domains(self) -> Optional[gpd.GeoDataFrame]:
        """Get NEON eco-climatic domain boundaries"""
        # NEON Domains feature service
        service_url = "https://services.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NEON_Domains/FeatureServer/0"
        
        domains = self.query_feature_layer(service_url)
        
        if domains is not None:
            print(f"Retrieved {len(domains)} NEON domains")
            print(f"Columns: {list(domains.columns)}")
        
        return domains
    
    def get_neon_field_sites(self) -> Optional[gpd.GeoDataFrame]:
        """Get NEON field site locations (terrestrial and aquatic)"""
        service_url = "https://services.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NEON_Field_Sites/FeatureServer/0"
        
        sites = self.query_feature_layer(service_url)
        
        if sites is not None:
            print(f"Retrieved {len(sites)} NEON field sites")
            print(f"Columns: {list(sites.columns)}")
        
        return sites
    
    def get_neon_plot_points(self) -> Optional[gpd.GeoDataFrame]:
        """Get NEON Terrestrial Observation System (TOS) plot locations"""
        service_url = "https://services.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NEON_TOS_Plot_Points/FeatureServer/0"
        
        plots = self.query_feature_layer(service_url, result_record_count=5000)
        
        if plots is not None:
            print(f"Retrieved {len(plots)} NEON TOS plots")
            print(f"Columns: {list(plots.columns)}")
        
        return plots
    
    def get_sites_in_domain(self, domain_code: str) -> Optional[gpd.GeoDataFrame]:
        """Get all field sites within a specific domain"""
        service_url = "https://services.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NEON_Field_Sites/FeatureServer/0"
        
        where_clause = f"DomainID = '{domain_code}'"
        sites = self.query_feature_layer(service_url, where_clause=where_clause)
        
        return sites
    
    def get_sites_by_type(self, site_type: str) -> Optional[gpd.GeoDataFrame]:
        """
        Get sites filtered by type
        site_type options: 'Core Terrestrial', 'Core Aquatic', 'Relocatable Terrestrial'
        """
        service_url = "https://services.arcgis.com/C8EMgrsFcRFL6LrL/arcgis/rest/services/NEON_Field_Sites/FeatureServer/0"
        
        where_clause = f"SiteType = '{site_type}'"
        sites = self.query_feature_layer(service_url, where_clause=where_clause)
        
        return sites
    
    def create_interactive_map(self, domains: gpd.GeoDataFrame = None, 
                              sites: gpd.GeoDataFrame = None,
                              output_file: str = "neon_map.html") -> folium.Map:
        """
        Create an interactive Folium map with NEON data
        """
        
        # Create base map centered on continental US
        m = folium.Map(
            location=[39.8283, -98.5795],
            zoom_start=4,
            tiles='CartoDB positron'
        )
        
        # Add domain boundaries if provided
        if domains is not None:
            folium.GeoJson(
                domains,
                name='NEON Domains',
                style_function=lambda x: {
                    'fillColor': 'lightblue',
                    'color': 'blue',
                    'weight': 2,
                    'fillOpacity': 0.3
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['DomainName', 'DomainID'],
                    aliases=['Domain:', 'ID:']
                )
            ).add_to(m)
        
        # Add field sites if provided
        if sites is not None:
            # Color by site type
            def get_site_color(site_type):
                colors = {
                    'Core Terrestrial': 'green',
                    'Core Aquatic': 'blue',
                    'Relocatable Terrestrial': 'orange'
                }
                return colors.get(site_type, 'gray')
            
            for idx, row in sites.iterrows():
                if row.geometry:
                    folium.CircleMarker(
                        location=[row.geometry.y, row.geometry.x],
                        radius=6,
                        popup=f"<b>{row.get('SiteName', 'Unknown')}</b><br>"
                              f"Code: {row.get('SiteID', 'N/A')}<br>"
                              f"Type: {row.get('SiteType', 'N/A')}<br>"
                              f"Domain: {row.get('DomainID', 'N/A')}",
                        color=get_site_color(row.get('SiteType')),
                        fill=True,
                        fillOpacity=0.7
                    ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(output_file)
        print(f"\nInteractive map saved to: {output_file}")
        
        return m
    
    def analyze_domain_coverage(self, domains: gpd.GeoDataFrame, 
                                sites: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Analyze site coverage across domains
        """
        
        if 'DomainID' in sites.columns and 'DomainID' in domains.columns:
            coverage = sites.groupby('DomainID').agg({
                'SiteID': 'count',
                'SiteType': lambda x: x.value_counts().to_dict()
            }).reset_index()
            
            coverage.columns = ['DomainID', 'TotalSites', 'SiteTypeBreakdown']
            
            # Merge with domain names
            coverage = coverage.merge(
                domains[['DomainID', 'DomainName']].drop_duplicates(),
                on='DomainID',
                how='left'
            )
            
            return coverage
        
        return None


def example_full_workflow():
    """
    Complete workflow: Query spatial data, analyze, and visualize
    """
    
    print("=" * 70)
    print("NEON SPATIAL DATA MINING - Full Workflow")
    print("=" * 70)
    
    miner = NEONSpatialMiner()
    
    # 1. Get domain boundaries
    print("\n[1/5] Fetching NEON domain boundaries...")
    domains = miner.get_neon_domains()
    
    if domains is not None:
        print(f"✓ Retrieved {len(domains)} domains")
        print(f"  Available fields: {', '.join(domains.columns[:10])}")
        
        # Save to file
        domains.to_file("/home/claude/neon_domains.geojson", driver='GeoJSON')
        print("  Saved to: neon_domains.geojson")
    
    # 2. Get field sites
    print("\n[2/5] Fetching NEON field sites...")
    sites = miner.get_neon_field_sites()
    
    if sites is not None:
        print(f"✓ Retrieved {len(sites)} field sites")
        
        # Analyze site types
        if 'SiteType' in sites.columns:
            print("\n  Site type distribution:")
            print(sites['SiteType'].value_counts().to_string())
        
        # Save to file
        sites.to_file("/home/claude/neon_sites.geojson", driver='GeoJSON')
        print("  Saved to: neon_sites.geojson")
    
    # 3. Get plot points (sample)
    print("\n[3/5] Fetching TOS plot points...")
    plots = miner.get_neon_plot_points()
    
    if plots is not None:
        print(f"✓ Retrieved {len(plots)} plot points")
        plots.to_file("/home/claude/neon_plots.geojson", driver='GeoJSON')
        print("  Saved to: neon_plots.geojson")
    
    # 4. Analyze coverage
    print("\n[4/5] Analyzing domain coverage...")
    if domains is not None and sites is not None:
        coverage = miner.analyze_domain_coverage(domains, sites)
        
        if coverage is not None:
            print("\n  Sites per domain:")
            print(coverage[['DomainName', 'TotalSites']].to_string(index=False))
            
            coverage.to_csv("/home/claude/domain_coverage.csv", index=False)
            print("  Saved to: domain_coverage.csv")
    
    # 5. Create interactive map
    print("\n[5/5] Creating interactive map...")
    map_obj = miner.create_interactive_map(
        domains=domains, 
        sites=sites,
        output_file="/home/claude/neon_interactive_map.html"
    )
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - neon_domains.geojson")
    print("  - neon_sites.geojson")
    print("  - neon_plots.geojson")
    print("  - domain_coverage.csv")
    print("  - neon_interactive_map.html")
    print("\nOpen neon_interactive_map.html in your browser to explore!")


def example_query_specific_domain():
    """Example: Query a specific domain"""
    miner = NEONSpatialMiner()
    
    domain_code = "D01"  # Northeast
    print(f"\nQuerying sites in domain {domain_code}...")
    
    sites = miner.get_sites_in_domain(domain_code)
    
    if sites is not None:
        print(f"\nFound {len(sites)} sites in {domain_code}")
        print(sites[['SiteID', 'SiteName', 'SiteType']])


def example_query_aquatic_sites():
    """Example: Get only aquatic sites"""
    miner = NEONSpatialMiner()
    
    print("\nQuerying Core Aquatic sites...")
    aquatic = miner.get_sites_by_type('Core Aquatic')
    
    if aquatic is not None:
        print(f"\nFound {len(aquatic)} aquatic sites")
        print(aquatic[['SiteID', 'SiteName', 'DomainID']])


if __name__ == "__main__":
    # Run the full workflow
    example_full_workflow()
    
    # Uncomment to run specific examples:
    # example_query_specific_domain()
    # example_query_aquatic_sites()
