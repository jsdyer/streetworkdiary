# Streetwork Diary

[Open Streetwork Diary](https://coolcode.ca/streetworkdiary/). Explore two Halifax Cityworks reporting weeks.

<!-- coolcode:guide -->
Start with street-surface requests for April 1–7, 2025. Compare closed counts, published resolution coverage and custom-field coverage, then switch to another request type.
<!-- /coolcode:guide -->

## Sources and interpretation

<p>The <a href="https://www.arcgis.com/home/item.html?id=d2b7dd138adb468293183926a1a7a81c">Halifax Cityworks service-request table</a> records administrative status, closure dates and resolution fields. The <a href="https://www.arcgis.com/home/item.html?id=81703e2cda974ffb8d4ba1f313d18429">custom-fields table</a> supplies additional fields for some requests. Requests are counted once by ID, including those with no matching detail row. A closed request can represent a referral or other administrative action. These records alone do not verify a completed repair.</p><p>The archive comparison uses the week beginning April 1, 2025 and the latest complete Monday–Sunday week before the newest published request. It includes street-surface maintenance, right-of-way litter and graffiti categories. Dates and boundaries use the published UTC timestamps. Elapsed time uses valid date pairs. A populated resolution field means text was provided. Addresses, resolution text and other free text are omitted from this snapshot. <a href="https://data-hrm.hub.arcgis.com/pages/open-data-licence">HRM Open Data Licence</a>.</p>

## Maintaining the tool

The published app reads its bundled JSON without contacting the municipality. A scheduled GitHub Action runs the collector, validates the result, and rebuilds Pages when the snapshot changes. Run `python3 scripts/refresh.py`, `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests`, then `python3 scripts/build.py`. Browser checks run against the built site at its repository subpath. The collector writes atomically after verifying complete ArcGIS ID batches.
