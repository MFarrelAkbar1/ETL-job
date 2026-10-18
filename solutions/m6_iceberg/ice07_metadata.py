"""Kunci jawaban ICE07."""

from __future__ import annotations

import json
from pathlib import Path

from pyiceberg.table import Table


def metadata_summary(table: Table) -> dict:
    md = json.loads(Path(table.metadata_location).read_text(encoding="utf-8"))
    schema = next(s for s in md["schemas"] if s["schema-id"] == md["current-schema-id"])
    names = {f["id"]: f["name"] for f in schema["fields"]}
    spec = next(s for s in md["partition-specs"] if s["spec-id"] == md["default-spec-id"])
    current_id = md.get("current-snapshot-id")
    if current_id in (None, -1):
        current_id = None
    manifest_ok = False
    if current_id is not None:
        snap = next(s for s in md["snapshots"] if s["snapshot-id"] == current_id)
        manifest_ok = Path(snap["manifest-list"]).exists()
    return {
        "format_version": md["format-version"],
        "current_snapshot_id": current_id,
        "n_snapshots": len(md.get("snapshots", [])),
        "n_schemas": len(md["schemas"]),
        "current_schema_id": md["current-schema-id"],
        "n_previous_metadata": len(md.get("metadata-log", [])),
        "partition_fields": [(f["name"], f["transform"], names[f["source-id"]]) for f in spec["fields"]],
        "manifest_list_exists": manifest_ok,
    }
