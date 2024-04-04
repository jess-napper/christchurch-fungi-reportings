# iNaturalist Fungi Observations Data Contract

1. Access
   - API Endpoint: https://api.inaturalist.org/v1/observations
   - Authentication: None required for public data
   - Rate Limit: 10,000 requests per day, 60 requests per minute
   - Pagination: `page` and `per_page` parameters

2. Schema (using SDMX)
```xml
<structure>
  <id>inaturalist_fungi_observations</id>
  <name>iNaturalist Fungi Observations</name>
  <attributes>
    <attribute>
      <id>id</id>
      <name>ID</name>
      <type>integer</type>
    </attribute>
    <attribute>
      <id>species_guess</id>
      <name>Species Guess</name>
      <type>string</type>
    </attribute>
    <attribute>
      <id>observed_on</id>
      <name>Observed On</name>
      <type>date</type>
    </attribute>
    <attribute>
      <id>place_guess</id>
      <name>Place Guess</name>
      <type>string</type>
    </attribute>
    <attribute>
      <id>latitude</id>
      <name>Latitude</name>
      <type>float</type>
    </attribute>
    <attribute>
      <id>longitude</id>
      <name>Longitude</name>
      <type>float</type>
    </attribute>
    <attribute>
      <id>user_login</id>
      <name>User Login</name>
      <type>string</type>
    </attribute>
    <attribute>
      <id>created_at</id>
      <name>Created At</name>
      <type>datetime</type>
    </attribute>
  </attributes>
</structure>
```

3. Structural Quality
   - Missing Values: Less than 5% for each attribute
   - Data Volume: Varies based on observation activity, typically less than 1,000 records per week for the specified criteria
   - Update Frequency: Near real-time as observations are submitted and verified
   - Completeness: 100% for `id`, `observed_on`, and `created_at` attributes; other attributes may have missing values
   - Freshness: Data should not be older than 1 week from the current date

4. Statistical Quality
   - Anomaly Detection: Not applicable for this dataset
   - Outlier Threshold: Not applicable for this dataset

5. Error Handling
   - HTTP Status Codes: Use standard codes (e.g., 200, 400, 500)
   - Error Messages: Provide clear and descriptive error messages in the API response

6. Versioning
   - API Version: v1
   - Schema Version: 1.0

7. Support
   - Documentation: https://api.inaturalist.org/v1/docs/
   - Contact: help@inaturalist.org

8. Service Level Agreement (SLA)
   - Uptime: 99.5%
   - Response Time: Less than 1000ms for 95% of requests

9. Data Lineage
   - Source: iNaturalist user observations
   - Transformations: Filtered by location, taxon, and quality grade; attributes selected and renamed

10. Data Governance
    - Data Steward: iNaturalist Data Team (data@inaturalist.org)
    - Compliance: iNaturalist Terms of Service and Privacy Policy
    - Retention Policy: Observation data retained indefinitely unless explicitly deleted by the user or iNaturalist administrators