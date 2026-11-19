from collections import defaultdict
from datetime import date, timedelta
from source import day, query, records, save

MAIN = "Cityworks_Service_Requests/FeatureServer/0"
CUSTOM = "Cityworks_Service_Requests_Custom_Fields/FeatureServer/0"
TYPES = ("Street Surface Maintenance", "ROW Litter", "Graffiti")
# Only publish known category labels. The municipal service also accepts free text.
LITTER_LABELS = {
    label.casefold(): label
    for label in (
        "Tires",
        "Loose/Scattered Debris, Garbage Bags",
        "Broken Glass, Sharp Objects, Metals",
        "Other",
        "Needles",
        "Construction Materials",
        "Shopping Carts",
        "Overflowing Garbage Cans or Receptacles",
        "Furniture and Electronics",
        "Human Feces, Vomit, Bodily Fluids",
    )
}


def window(start, end):
    dates = f"DATE_INITIATED >= DATE '{start}' AND DATE_INITIATED < DATE '{end}'"
    types = " OR ".join(f"DESCRIPTION LIKE '{t}%'" for t in TYPES)
    fields = "REQUEST_ID,DESCRIPTION,COMMUNITY,DATE_INITIATED,DATE_CLOSED,STATUS,RESOLUTION,WORK_ORDER"
    base = records(MAIN, dates + " AND (" + types + ")", fields)
    if not base:
        raise ValueError("Empty street-service week")
    ids = sorted(r["REQUEST_ID"] for r in base)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate request ID")
    marks = defaultdict(set)
    litter = defaultdict(set)
    for start_at in range(0, len(ids), 65):
        batch = ids[start_at : start_at + 65]
        result = records(
            CUSTOM,
            "REQUESTID IN (" + ",".join(map(str, batch)) + ")",
            "REQUESTID,CUSTOM_FIELD_NAME,CUSTOM_FIELD_VALUE",
        )
        for row in result:
            request_id = row["REQUESTID"]
            field = (row["CUSTOM_FIELD_NAME"] or "Unlabelled").strip()
            marks[request_id].add(field)
            if field.casefold() == "type of litter/issue":
                label = LITTER_LABELS.get(
                    (row["CUSTOM_FIELD_VALUE"] or "").strip().casefold()
                )
                if label:
                    litter[request_id].add(label)
    rows = []
    for r in base:
        rid = r["REQUEST_ID"]
        duration = None
        if r["DATE_CLOSED"] and r["DATE_CLOSED"] >= r["DATE_INITIATED"]:
            duration = round((r["DATE_CLOSED"] - r["DATE_INITIATED"]) / 86400000, 2)
        rows.append(
            [
                rid,
                r["DESCRIPTION"].strip(),
                (r["COMMUNITY"] or "Unspecified").strip(),
                day(r["DATE_INITIATED"]),
                r["STATUS"],
                duration,
                bool(str(r["RESOLUTION"] or "").strip()),
                sorted(marks[rid]),
                r["WORK_ORDER"] == "Y",
                sorted(litter[rid]),
            ]
        )
    return {
        "start": str(start),
        "end": str(end - timedelta(days=1)),
        "rows": sorted(rows),
    }


def community_boundaries(periods):
    names = {row[2] for period in periods for row in period["rows"]}
    # HRM publishes E911 community polygons. Request a generalized display edition.
    data = query(
        "GSA/FeatureServer/0", where="1=1", outFields="GSA_NAME",
        returnGeometry="true", outSR=4326, maxAllowableOffset=0.0015,
        geometryPrecision=4, f="geojson",
    )
    if data.get("exceededTransferLimit"):
        raise ValueError("Incomplete community boundary edition")
    polygons = {}
    for feature in data["features"]:
        name = feature["properties"]["GSA_NAME"]
        if name not in names:
            continue
        shape = feature["geometry"]
        if name in polygons or shape["type"] not in ("Polygon", "MultiPolygon") or not shape["coordinates"]:
            raise ValueError("Review community polygons")
        polygons[name] = shape
    if not polygons:
        raise ValueError("No request communities matched municipal boundaries")
    return polygons


def main():
    last = query(
        MAIN,
        where="1=1",
        outFields="DATE_INITIATED",
        returnGeometry="false",
        orderByFields="DATE_INITIATED DESC",
        resultRecordCount=1,
    )
    latest = date.fromisoformat(
        day(last["features"][0]["attributes"]["DATE_INITIATED"])
    )
    end = latest - timedelta(days=latest.weekday())
    fixed = date(2025, 4, 1)
    periods = [
        window(fixed, fixed + timedelta(days=7)),
        window(end - timedelta(days=7), end),
    ]
    if periods[0]["start"] == periods[1]["start"]:
        periods = periods[:1]
    save(
        "requests.json",
        count=sum(len(p["rows"]) for p in periods),
        sourceThrough=str(latest),
        periods=periods,
        communities=community_boundaries(periods),
    )


if __name__ == "__main__":
    main()
