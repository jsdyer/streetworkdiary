"""Fetch complete ArcGIS result windows and publish a validated, atomic snapshot."""

from datetime import datetime, timezone
import json
from pathlib import Path
from time import sleep
from urllib.parse import urlencode
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/"


def query(layer, **params):
    url = BASE + layer + "/query?" + urlencode({"f": "json", **params})
    for attempt in range(3):
        try:
            with urlopen(
                Request(url, headers={"User-Agent": "CoolCode public data collector"}),
                timeout=85,
            ) as response:
                data = json.load(response)
            if "error" in data:
                raise ValueError(data["error"])
            return data
        except (OSError, ValueError):
            if attempt == 2:
                raise
            sleep(3 * (attempt + 1))


def records(layer, where, fields):
    ids = query(layer, where=where, returnIdsOnly="true")["objectIds"] or []
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate published object IDs")
    output = []
    for start in range(0, len(ids), 120):
        batch = ids[start : start + 120]
        data = query(
            layer,
            objectIds=",".join(map(str, batch)),
            outFields=fields,
            returnGeometry="false",
        )
        rows = [x["attributes"] for x in data["features"]]
        if data.get("exceededTransferLimit") or len(rows) != len(batch):
            raise ValueError("Incomplete ArcGIS result")
        output.extend(rows)
    return output


def day(epoch):
    return datetime.fromtimestamp(epoch / 1000, timezone.utc).date().isoformat()


def save(name, **payload):
    dest = ROOT / "web/data" / name
    dest.parent.mkdir(exist_ok=True)
    result = {"retrieved": datetime.now(timezone.utc).date().isoformat(), **payload}
    temp = dest.with_suffix(".tmp")
    temp.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        + "\n"
    )
    temp.replace(dest)
    print(dest.name, result["retrieved"])
