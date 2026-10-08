#!/usr/bin/env python3
"""Inventory AIID tar.bz2 snapshot without selecting incidents or extracting files."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import tarfile

def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--out", type=Path, default=Path("aiid_screening"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "snapshot_file": args.snapshot.name,
        "sha256": sha256(args.snapshot),
        "status": "SCHEMA_REVIEW_REQUIRED",
        "members": [],
    }
    with tarfile.open(args.snapshot, "r:bz2") as archive:
        for member in archive:
            if not member.isfile():
                continue
            row = {"path": member.name, "bytes": member.size}
            if member.name.lower().endswith(".csv"):
                try:
                    handle = archive.extractfile(member)
                    reader = csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", errors="replace", newline=""))
                    row["columns"] = reader.fieldnames
                    row["sample_rows"] = [
                        {k: v[:150] if isinstance(v, str) else v for k, v in item.items()}
                        for _, item in zip(range(2), reader)
                    ]
                except Exception as exc:
                    row["inspection_error"] = str(exc)
            manifest["members"].append(row)
    destination = args.out / "snapshot_inventory.json"
    destination.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(destination)
    print("Inspect schema and define screening frame before selecting any incidents.")

if __name__ == "__main__":
    main()
