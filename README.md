# Forecast Reports

Creates daily reports from CAMS and WMO/AEMET air quality forecast data for specified geographical areas and points.


## Examples

Examples of the output forecast reports are available in the [examples](./examples) directory.


### Live demos

- [Air quality forecast plots](https://avnigo.github.io/forecast-reports/forecast)
  - Distribution over a specified area *(CAMS)* — [five-number summary](https://en.wikipedia.org/wiki/Five-number_summary)
  - Air quality trends for a set of coordinates *(CAMS)*
  - Multi-model dust forecast trends for a specific point *(WMO/AEMET)*
  - Daily dust exceedance probabilities inside [polygon](./data/ref/cyprus.geojson) *(WMO/AEMET)*
- [Dust forecast map](https://avnigo.github.io/forecast-reports/dust-forecast-map)


## Usage

Running `forecast.py` will download the latest data from the available sources and create the forecast reports, as in the [examples](#live-demos).


## Attribution

- **CAMS** reports are generated using Copernicus Atmosphere Monitoring Service information through the CDS API.
- **WMO/AEMET** reports are derived from dust data and images provided by the WMO Barcelona Dust Regional Center and the partners of the Sand and Dust Storm Warning Advisory and Assessment System (SDS-WAS) for Northern Africa, the Middle East and Europe.
