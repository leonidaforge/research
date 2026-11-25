#!/usr/bin/env python3
"""Reproduce the texture-dictionary and drawable-reference aggregates.

The script reads extracted nested archives and the JSON listings produced by
``lforge archive ls <ARCHIVE> --json``. It selects rows by the local CLI type
ID, reconstructs the stored rows with ``page_reconstruct``, parses dictionaries
with ``texture_dictionary`` and walks drawable shader chains with
``pool_reference``. Every aggregate quoted in the resource documents is
produced here.

Usage:

    python dictionary_census.py \
        --dictionary ARCHIVE LISTING [--dictionary ...] \
        --drawable ARCHIVE LISTING [--drawable ...] \
        --negative ARCHIVE LISTING TYPE [TYPE ...] \
        [--json]

A listing is the JSON object printed by ``lforge archive ls``. The selection
rule is the ``type_id`` field in that listing: dictionaries are type 5 and
drawables are type 2. The archive and listing paths are caller supplied; the
script reads them only and invokes no application code.
"""

from __future__ import annotations

import argparse
import json
import random
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass

import page_reconstruct
import pool_reference
import texture_dictionary

# The six constant texture-parameter values recorded by DRAW-F18. They are
# compared with the drawable name-record values; no value is resolved to a name.
DRAW_F18_CONSTANTS = {
    0xC8E8C282,
    0x739E3D0D,
    0x2C8D7182,
    0x0CD27763,
    0xC6F46E79,
    0x1E77BF4C,
}
CONTROL_TRIALS = 10000
MAX_ROWS = 1_000_000


class CensusError(Exception):
    pass


@dataclass
class Source:
    archive: str
    listing: str
    types: set | None = None


def rows(source: Source, types=None):
    with open(source.listing, encoding="utf-8") as handle:
        listing = json.load(handle)
    entries = listing.get("rows", [])
    if len(entries) > MAX_ROWS:
        raise CensusError(
            f"{source.listing} holds {len(entries)} rows, above the {MAX_ROWS} cap"
        )
    for entry in entries:
        if types is None or entry.get("type_id") in types:
            yield entry


def decode(source: Source, entry):
    offset = int(entry["payload_offset"], 16)
    length = entry["stored_size"]
    with open(source.archive, "rb") as handle:
        handle.seek(offset)
        buffer = handle.read(length)
    layout = page_reconstruct.analyze_bytes(
        buffer, source.archive, logical_size=entry.get("logical_size")
    )
    if layout.status != "complete" or layout.page_map is None:
        codes = ", ".join(issue.code for issue in layout.issues) or "no page map"
        raise CensusError(f"{source.archive} row {entry['row']}: {codes}")
    system_size = sum(page.size for page in layout.pages if page.segment == "system")
    decoded = b"".join(chunk.data for chunk in layout.chunks)
    return decoded[:system_size], decoded[system_size:]


def dictionary_census(sources):
    hash_records = defaultdict(list)
    stats = Counter()
    issues = Counter()
    formats = Counter()
    mips = Counter()
    dimensions = set()
    record_counts = []
    for source in sources:
        for entry in rows(source, {5}):
            try:
                system, graphics = decode(source, entry)
                dictionary = texture_dictionary.parse_dictionary(system, len(graphics))
            except (CensusError, texture_dictionary.TextureDictionaryError) as err:
                stats["decode_or_parse_fail"] += 1
                stats[f"fail:{type(err).__name__}"] += 1
                continue
            stats["rows"] += 1
            stats["empty"] += int(dictionary.record_count == 0)
            stats["nonempty"] += int(dictionary.record_count > 0)
            stats["records"] += dictionary.record_count
            record_counts.append(dictionary.record_count)
            stats["counts_equal"] += int(dictionary.hash_count == dictionary.value_count)
            stats["capacities_ok"] += int(
                dictionary.hash_capacity >= dictionary.hash_count
                and dictionary.value_capacity >= dictionary.value_count
            )
            stats["in_bounds"] += int(dictionary.allocations_in_bounds)
            stats["sum_ok"] += int(dictionary.allocation_sum_ok)
            checked, matched = texture_dictionary.check_names(system, dictionary)
            stats["names_checked"] += checked
            stats["names_matched"] += matched
            for issue in dictionary.issues:
                issues[issue.code] += 1
            for record in dictionary.records:
                hash_records[record.name_hash].append(
                    (source.archive, entry["row"], record.index)
                )
                formats[record.format_id] += 1
                mips[record.mip_levels] += 1
                dimensions.add((record.width, record.height))
    multiplicities = Counter(len(value) for value in hash_records.values())
    format_values = sorted(formats)
    mip_values = sorted(mips)
    return {
        "stats": dict(stats),
        "issues": dict(issues),
        "formats": dict(formats),
        "format_ids": len(format_values),
        "format_min": format_values[0] if format_values else None,
        "format_max": format_values[-1] if format_values else None,
        "mips": dict(mips),
        "mip_min": mip_values[0] if mip_values else None,
        "mip_max": mip_values[-1] if mip_values else None,
        "distinct_dimensions": len(dimensions),
        "dimension_min": min(dimensions) if dimensions else None,
        "dimension_max": max(dimensions) if dimensions else None,
        "records_min": min(record_counts) if record_counts else None,
        "records_max": max(record_counts) if record_counts else None,
        "records_min_nonempty": min((value for value in record_counts if value), default=None),
        "distinct_hashes": len(hash_records),
        "hash_multiplicity": dict(multiplicities),
    }, hash_records


def drawable_census(sources, hash_records):
    stats = Counter()
    states = Counter()
    name_hashes = Counter()
    matched = Counter()
    per_drawable = Counter()
    bound_per_drawable = Counter()
    matched_multiplicity = Counter()
    drawduplicate = Counter()
    key_halves = Counter()
    for source in sources:
        for entry in rows(source, {2}):
            try:
                system, graphics = decode(source, entry)
                report = pool_reference.parse_shader_pool(
                    system, graphics_length=len(graphics)
                )
            except (CensusError, pool_reference.PoolReferenceError) as err:
                stats["decode_or_parse_fail"] += 1
                stats[f"fail:{type(err).__name__}"] += 1
                continue
            stats["drawables"] += 1
            stats["shaders"] += len(report.shaders)
            stats["other_entries"] += report.other_entries
            stats["other_accepted"] += report.other_accepted
            matched_here = 0
            bound_here = 0
            for shader in report.shaders:
                for reference in shader.references:
                    stats["texture_entries"] += 1
                    states[reference.state] += 1
                    if reference.index is not None:
                        stats["index_in"] += 1
                        stats["index_eq_parameter"] += int(reference.index == reference.parameter)
                    if reference.state != "bound":
                        continue
                    stats["bound"] += 1
                    bound_here += 1
                    if reference.key64 is not None:
                        key = reference.key64
                        key_halves["low_match"] += int(
                            (key & 0xFFFFFFFF) in hash_records
                        )
                        key_halves["high_match"] += int((key >> 32) in hash_records)
                    if reference.name_hash is None:
                        stats["name_variant_other"] += 1
                        continue
                    stats["name_hash_present"] += 1
                    name_hashes[reference.name_hash] += 1
                    candidates = hash_records.get(reference.name_hash)
                    if not candidates:
                        stats["namespace_unmatched"] += 1
                        continue
                    stats["namespace_matched"] += 1
                    matched_here += 1
                    matched[reference.name_hash] += 1
                    if reference.name_hash in DRAW_F18_CONSTANTS:
                        stats["draw_f18_overlap"] += 1
            if matched_here:
                per_drawable[matched_here] += 1
            else:
                drawduplicate["no_match"] += 1
            bound_per_drawable[bound_here] += 1
    for value in matched:
        matched_multiplicity[len(hash_records[value])] += 1
    stats["drawables_with_match"] = sum(per_drawable.values())
    stats["drawables_without_match"] = drawduplicate["no_match"]
    return {
        "stats": {
            "drawables": stats["drawables"],
            "shaders": stats["shaders"],
            "texture_entries": stats["texture_entries"],
            "index_in": stats["index_in"],
            "index_eq_parameter": stats["index_eq_parameter"],
            "other_entries": stats["other_entries"],
            "other_accepted": stats["other_accepted"],
            "bound": stats["bound"],
            "name_hash_present": stats["name_hash_present"],
            "name_variant_other": stats["name_variant_other"],
            "namespace_matched": stats["namespace_matched"],
            "namespace_unmatched": stats["namespace_unmatched"],
            "drawables_with_match": stats["drawables_with_match"],
            "drawables_without_match": stats["drawables_without_match"],
            "draw_f18_overlap": stats["draw_f18_overlap"],
            "decode_or_parse_fail": stats["decode_or_parse_fail"],
        },
        "states": {key: states[key] for key in ("bound", "null", "class", "index", "bad")},
        "distinct_name_hashes": len(name_hashes),
        "distinct_matched_hashes": len(matched),
        "matched_hash_multiplicity": dict(matched_multiplicity),
        "matched_hash_record_counts": sorted(len(hash_records[value]) for value in matched),
        "per_drawable_match_counts": dict(per_drawable),
        "bound_per_drawable": {
            "distribution": dict(bound_per_drawable),
            "minimum": min(bound_per_drawable) if bound_per_drawable else 0,
            "maximum": max(bound_per_drawable) if bound_per_drawable else 0,
            "drawables_with_bound": sum(bound_per_drawable.values()),
        },
        "key_halves": {
            "low_match": key_halves["low_match"],
            "high_match": key_halves["high_match"],
        },
    }


def negative_census(sources):
    stats = Counter()
    by_type = Counter()
    for source in sources:
        types = source.types
        for entry in rows(source, types):
            by_type[entry["type_id"]] += 1
            try:
                system, graphics = decode(source, entry)
            except CensusError:
                stats["decode_fail"] += 1
                continue
            try:
                dictionary = texture_dictionary.parse_dictionary(system, len(graphics))
            except texture_dictionary.TextureDictionaryError:
                stats["rejected_structural"] += 1
                continue
            stats["accepted"] += 1
            stats["accepted_empty"] += int(dictionary.record_count == 0)
            stats["accepted_nonempty"] += int(dictionary.record_count > 0)
    return {
        "stats": {
            "selected": sum(by_type.values()),
            "decode_fail": stats["decode_fail"],
            "rejected_structural": stats["rejected_structural"],
            "accepted": stats["accepted"],
            "accepted_empty": stats["accepted_empty"],
            "accepted_nonempty": stats["accepted_nonempty"],
        },
        "selected_by_type": dict(by_type),
    }


def control_census(hash_records):
    rng = random.Random(0)
    slot_accepted = 0
    for _ in range(CONTROL_TRIALS):
        if pool_reference.decode_slot_reference(rng.getrandbits(32), 8)[0]:
            slot_accepted += 1
    rng = random.Random(1)
    hash_matched = 0
    for _ in range(CONTROL_TRIALS):
        if rng.getrandbits(32) in hash_records:
            hash_matched += 1
    return {
        "trials": CONTROL_TRIALS,
        "slot_accepted": slot_accepted,
        "slot_threshold": CONTROL_TRIALS // 100,
        "hash_matched": hash_matched,
        "hash_threshold": CONTROL_TRIALS // 100,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dictionary", nargs=2, action="append", default=[],
                        metavar=("ARCHIVE", "LISTING"))
    parser.add_argument("--drawable", nargs=2, action="append", default=[],
                        metavar=("ARCHIVE", "LISTING"))
    parser.add_argument("--negative", nargs="+", action="append", default=[],
                        metavar=("ARCHIVE LISTING TYPE"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    dictionary_sources = [Source(*pair) for pair in args.dictionary]
    drawable_sources = [Source(*pair) for pair in args.drawable]
    negative_sources = []
    for group in args.negative:
        if len(group) < 3:
            parser.error("--negative needs ARCHIVE LISTING TYPE [TYPE ...]")
        source = Source(group[0], group[1])
        source.types = {int(value, 0) for value in group[2:]}
        negative_sources.append(source)

    if not dictionary_sources:
        parser.error("at least one --dictionary source is required")
    try:
        dictionary, hash_records = dictionary_census(dictionary_sources)
        drawables = drawable_census(drawable_sources, hash_records) if drawable_sources else None
        negatives = negative_census(negative_sources) if negative_sources else None
    except CensusError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    out = {
        "selection": {
            "dictionary_sources": [[s.archive, s.listing] for s in dictionary_sources],
            "drawable_sources": [[s.archive, s.listing] for s in drawable_sources],
            "negative_sources": [[s.archive, s.listing, sorted(s.types)]
                                 for s in negative_sources],
            "dictionary_select": "type_id == 5",
            "drawable_select": "type_id == 2",
        },
        "dictionaries": dictionary,
        "drawables": drawables,
        "negatives": negatives,
        "control": control_census(hash_records),
    }
    if args.json:
        json.dump(out, sys.stdout, indent=2)
        print()
    else:
        print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
