# NEON Data Mining Toolkit
https://github.com/meistro57/NEON-Forge/blob/e886a19015b69b27ad6500efe0d28a6e3a7e3b3d/NEON-LOGO.gif
Complete Python toolkit for mining ecological data from the National Ecological Observatory Network (NEON).

## What You Can Mine

### 🌍 Spatial/GIS Data (neon_spatial_miner.py)
- **81 field sites** across 20 eco-climatic domains
- **Domain boundaries** - Geographic polygons for each eco-climatic region
- **Field site locations** - Precise GPS coordinates for terrestrial and aquatic sites
- **TOS plot points** - Thousands of monitoring plot locations
- **Flight boundaries** - Airborne observation platform coverage areas
- **Watershed boundaries** - Aquatic site drainage areas

### 📊 Ecological Time-Series Data (neon_data_miner.py)
- **Climate/Weather** - Temperature, precipitation, humidity, wind
- **Biodiversity** - Birds, insects, small mammals, plants
- **Soil** - Chemistry, microbes, moisture, temperature
- **Water Quality** - Chemical properties, nutrients, dissolved gases
- **Plant Phenology** - Leaf emergence, flowering, fruiting timing
- **Carbon Flux** - CO2/methane exchange between ecosystems and atmosphere
- **Remote Sensing** - LiDAR, hyperspectral imagery, high-res photography

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start Examples

### Example 1: Get All Field Sites
```python
from neon_data_miner import NEONDataMiner

miner = NEONDataMiner()
sites = miner.get_all_sites()

print(f"Total sites: {len(sites)}")
print(sites[['siteCode', 'siteName', 'domainCode', 'stateCode']].head())
```

### Example 2: Search for Specific Data
```python
# Find all bird-related datasets
bird_data = miner.search_products_by_keyword('bird')
print(bird_data[['productCode', 'productName']])

# Find soil data
soil_data = miner.search_products_by_keyword('soil')

# Find climate data
climate_data = miner.search_products_by_keyword('temperature')
```

### Example 3: Check Data Availability
```python
# Check where breeding bird count data is available
product_code = 'DP1.10003.001'  # Breeding landbird point counts
availability = miner.get_product_availability(product_code)

print(f"Available at {availability['site'].nunique()} sites")
print(f"Time range: {availability['month'].min()} to {availability['month'].max()}")
```

### Example 4: Download Actual Data Files
```python
# Get download URLs for specific site/time
files = miner.download_data_urls(
    product_code='DP1.10003.001',  # Bird counts
    site_code='HARV',              # Harvard Forest
    year_month='2023-06'           # June 2023
)

# Now you can download these files
for idx, row in files.iterrows():
    print(f"{row['name']}: {row['url']}")
```

### Example 5: Mine Spatial Data from ArcGIS
```python
from neon_spatial_miner import NEONSpatialMiner

spatial = NEONSpatialMiner()

# Get domain boundaries as GeoDataFrame
domains = spatial.get_neon_domains()
domains.to_file('neon_domains.geojson', driver='GeoJSON')

# Get all field sites
sites = spatial.get_neon_field_sites()

# Query specific domain
northeast_sites = spatial.get_sites_in_domain('D01')

# Get only aquatic sites
aquatic = spatial.get_sites_by_type('Core Aquatic')
```

### Example 6: Create Interactive Map
```python
from neon_spatial_miner import NEONSpatialMiner

spatial = NEONSpatialMiner()

domains = spatial.get_neon_domains()
sites = spatial.get_neon_field_sites()

# Creates an interactive Folium map
map_obj = spatial.create_interactive_map(
    domains=domains,
    sites=sites,
    output_file='neon_map.html'
)
# Open neon_map.html in your browser!
```

## Available Data Products (Examples)

### Organisms
- `DP1.10003.001` - Breeding landbird point counts
- `DP1.10022.001` - Beetles sampled from pitfall traps
- `DP1.10072.001` - Small mammal box trapping
- `DP1.10058.001` - Plant presence and percent cover
- `DP1.10093.001` - Ticks sampled using drag cloths

### Biogeochemistry
- `DP1.20002.001` - Chemical properties of groundwater
- `DP1.20093.001` - Chemical properties of surface water
- `DP1.10086.001` - Soil physical and chemical properties
- `DP1.00024.001` - Temperature at specific depths in soil

### Atmosphere
- `DP1.00002.001` - Single aspirated air temperature
- `DP1.00006.001` - Precipitation
- `DP1.00001.001` - 2D wind speed and direction
- `DP4.00200.001` - Bundled data products - eddy covariance

### Remote Sensing
- `DP3.30015.001` - Ecosystem structure (LiDAR point cloud)
- `DP3.30006.001` - Spectrometer orthorectified surface directional reflectance
- `DP3.30010.001` - High-resolution orthorectified camera imagery

## API Endpoints Used

### NEON Data API
- Base: `https://data.neonscience.org/api/v0`
- Sites: `/sites`
- Products: `/products`
- Data: `/data/{productCode}/{siteCode}/{year-month}`

### NEON ArcGIS Services
- Domains: `https://services.arcgis.com/.../NEON_Domains/FeatureServer/0`
- Sites: `https://services.arcgis.com/.../NEON_Field_Sites/FeatureServer/0`
- Plots: `https://services.arcgis.com/.../NEON_TOS_Plot_Points/FeatureServer/0`

## Data Analysis Ideas

### Climate Change Research
```python
# Get 30 years of temperature data across all domains
# Compare warming trends by latitude/elevation
# Correlate with species migration patterns
```

### Biodiversity Monitoring
```python
# Track bird population changes over time
# Identify declining species across ecosystems
# Correlate biodiversity with habitat fragmentation
```

### Ecosystem Health
```python
# Monitor soil health indicators
# Track water quality trends
# Analyze carbon sequestration rates
```

### Spatial Analysis
```python
# Calculate biodiversity hotspots
# Model species habitat suitability
# Predict climate change impacts by region
```

## Advanced Features

### Batch Download Multiple Sites
```python
sites_to_download = ['HARV', 'BART', 'SCBI']
product = 'DP1.10003.001'
months = ['2023-05', '2023-06', '2023-07']

for site in sites_to_download:
    for month in months:
        files = miner.download_data_urls(product, site, month)
        # Process files...
```

### Spatial Queries with SQL-like Filters
```python
# Get sites in specific states
sites = spatial.query_feature_layer(
    service_url,
    where_clause="StateCode IN ('MA', 'NH', 'VT')"
)

# Get sites above certain elevation
sites = spatial.query_feature_layer(
    service_url,
    where_clause="Elevation > 1000"
)
```

### Export to Multiple Formats
```python
# GeoJSON for web mapping
gdf.to_file('output.geojson', driver='GeoJSON')

# Shapefile for GIS software
gdf.to_file('output.shp')

# CSV for spreadsheets
gdf.to_csv('output.csv')

# GeoPackage for modern GIS
gdf.to_file('output.gpkg', driver='GPKG')
```

## Rate Limits & Best Practices

- NEON API has no documented rate limits but be respectful
- Use `result_record_count` parameter to limit query sizes
- Cache downloaded data locally - don't re-download
- For large datasets, consider NEON's data portal bulk download
- ArcGIS services limit 1000-2000 records per query (paginate if needed)

## Common Use Cases

### 1. Environmental Monitoring Dashboard
Pull real-time climate data from multiple sites and visualize trends

### 2. Species Distribution Models
Combine occurrence data with climate/habitat variables

### 3. Citizen Science Integration
Overlay NEON data with eBird, iNaturalist observations

### 4. Machine Learning Training Data
30+ years of standardized ecological observations

### 5. Climate Impact Assessment
Before/after analysis of ecological changes

### 6. Grant Writing & Research Planning
Identify data availability for proposal sites

## Data Format Notes

### GeoJSON/Shapefiles
- Coordinate system: WGS84 (EPSG:4326)
- Geometry types: Point, Polygon, MultiPolygon
- Can be opened in QGIS, ArcGIS, Google Earth Pro

### CSV/Tabular Data
- UTF-8 encoding
- Headers included
- Timestamps in ISO format
- Missing values as NA or blank

### Time Series Data
- Monthly aggregations available
- Some products have sub-daily resolution
- Metadata includes collection methods, QA flags

## Troubleshooting

**"ProxyError" or connection issues:**
- Script is being run in an environment with restricted network access
- Try running on a system with direct internet access

**"No features returned":**
- Check your where_clause SQL syntax
- Verify the field names match the service
- Some queries may legitimately return no results

**"Too many records":**
- Increase `result_record_count` parameter
- Or implement pagination with offset parameter

## Resources

- NEON Website: https://www.neonscience.org
- Data Portal: https://data.neonscience.org
- API Documentation: https://data.neonscience.org/data-api
- Spatial Data: https://www.neonscience.org/data-samples/data/spatial-data-maps
- ArcGIS Hub: https://neon.maps.arcgis.com

## License

These scripts are for accessing publicly available NEON data.
NEON data is freely available under CC0 1.0 Universal license.

## Contributing

Feel free to extend these scripts with:
- Additional data product parsers
- Visualization functions
- Analysis workflows
- Integration with other ecological databases

---

**Built for the Quantum Minds United ecosystem**
*Connecting consciousness with ecological data*
