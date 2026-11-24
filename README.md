# Streetwork Diary

[Open Streetwork Diary](https://coolcode.ca/streetworkdiary/). Explore two Halifax Cityworks reporting weeks.

<!-- coolcode:guide -->
Choose a shaded community to filter the records for that area. Start with street-surface requests for April 1–7, 2025. Compare closed counts, published resolution coverage and custom-field coverage, then switch to another request type.
<!-- /coolcode:guide -->

The litter issue breakdown counts each request once per recognized municipal category. Only known labels from “Type of Litter/Issue” are included. The number of matching custom rows can therefore exceed the number with a displayed issue.

## Sources and interpretation

<p>The <a href="https://www.arcgis.com/home/item.html?id=d2b7dd138adb468293183926a1a7a81c">Halifax Cityworks service-request table</a> records administrative status, closure dates and resolution fields. The <a href="https://www.arcgis.com/home/item.html?id=81703e2cda974ffb8d4ba1f313d18429">custom-fields table</a> supplies additional fields for some requests. Requests are counted once by ID, including those with no matching detail row. A closed request can represent a referral or other administrative action. These records alone do not verify a completed repair.</p><p>The archive comparison uses the week beginning April 1, 2025 and the latest complete Monday–Sunday week before the newest published request. It includes street-surface maintenance, right-of-way litter and graffiti categories. Dates and boundaries use the published UTC timestamps. Elapsed time uses valid date pairs. A populated resolution field means text was provided. Addresses, resolution text and other free text are omitted from this snapshot. <a href="https://data-hrm.hub.arcgis.com/pages/open-data-licence">HRM Open Data Licence</a>.</p>

## Maintaining the tool

The map matches request community names to [published HRM community boundaries](https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/GSA/FeatureServer/0) under the HRM Open Data Licence. Boundaries are generalized for display. Each polygon shows the selected week and category total. Requests lacking a matching community remain in the table and selection total. The map never assigns individual request locations. The published app reads its bundled JSON without contacting the municipality. OpenStreetMap receives street-tile requests for the displayed area. Leaflet is bundled under the licence in web/vendor. A scheduled GitHub Action runs the collector, validates the result, and rebuilds Pages when the snapshot changes. Run `python3 scripts/refresh.py`, `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests`, then `python3 scripts/build.py`. Browser checks run against the built site at its repository subpath. The collector writes atomically after verifying complete ArcGIS ID batches.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

## Search metadata

The build emits a descriptive page title, canonical URL, social preview metadata and
static `WebApplication` JSON-LD for the free browser tool. The visible application
name stays unchanged. Edit the search title in `web/index.html`; application details
come from `tool.json`. No ratings or reviews are invented.
