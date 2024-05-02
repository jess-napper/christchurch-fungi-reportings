# Data
Format: CSV
Data and metadata are different end points
- URL/data?q=xxxxxx
- URL/data?data>=2024-03-21&format=CSV (if no date is given, all data comes back (metadata id is included))(format = JSON, CSV, ... etc)
- URL/metadata?v=1.1.1

## metadataVersion      unique id   DATE            temp    GEO     WeatherStation
V1.1.1                  1           2021-03-05      10      xxx-xx  CHCH34

# Metadata
Needs version - should give all previous metadata
V1.1.1 (V dimension.measure.code)
## Dimension   DimensionUnit   Description
DATE        yyyy-mm-dd      Date forecast was made
GEO         ([lat, long])

## Measure     MeasureUnit      Description
Temp        degrees C           Temperature...
Rain        see attributes

# Rain Attribute table (Code list)

Code    Description
1       Yes, there is rain
2       No, there is no rain

Unique title works as a unique ID (could be mistakenly changed)
URL - if you pay for and maintain the url