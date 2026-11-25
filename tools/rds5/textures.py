#!/usr/bin/env python3
"""Candidate pixel-format and mip-layout analysis for decoded RDS5 textures.

This module does not identify a codec. It models the decoded byte stream of one
descriptor as a reverse-ordered mip chain and reports scalar consistency facts:
level sizes, slot layout, observed block boundaries, a box-downsample error for
levels that are whole storage blocks, and first-byte statistics of fixed-size
block candidates.

It reads inputs through the read-only RDS5 parser and never writes files. It
prints sizes, offsets, counts and scalar metrics only; decoded image bytes are
never printed.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rds5  # noqa: E402

PAGE = 0x1000
MIN_SLOT = 0x100
MAX_LEVELS = 16

UNITS = ("B8", "B16", "L4", "L2", "L1")

# Observed storage unit per format id. These are size fits, not codec names.
# ``None`` means the format id was not measured; pass --unit explicitly.
OBSERVED_UNITS: Dict[int, str] = {
    28: "L4",
    54: "L2",
    71: "B8",
    72: "B8",
    77: "B16",
    80: "B8",
    83: "B16",
    98: "B16",
    99: "B16",
}


def level_bytes(width: int, height: int, unit: str) -> int:
    """Content bytes of one level. ``unit`` is a storage unit, not a codec."""
    w, h = max(1, width), max(1, height)
    if unit == "B8":
        return ((w + 3) // 4) * ((h + 3) // 4) * 8
    if unit == "B16":
        return ((w + 3) // 4) * ((h + 3) // 4) * 16
    if unit == "L4":
        return w * h * 4
    if unit == "L2":
        return w * h * 2
    if unit == "L1":
        return w * h
    raise ValueError(f"unknown storage unit {unit!r}; expected one of {UNITS}")


def level_sizes(width: int, height: int, levels: int, unit: str) -> List[int]:
    if levels < 1:
        raise ValueError("level count must be at least 1")
    return [level_bytes(width >> i, height >> i, unit) for i in range(levels)]


def slot_layout(width: int, height: int, levels: int, unit: str) -> dict:
    """Model the decoded stream as smallest mip first.

    Each level occupies ``max(size, MIN_SLOT)`` bytes. The stream is padded at
    the front to a PAGE multiple. Returns level entries in stream order
    (smallest level first), each as ``(level, offset, size, slot)``.
    """
    sizes = level_sizes(width, height, levels, unit)
    slots = [max(size, MIN_SLOT) for size in sizes]
    content = sum(slots)
    total = (content + PAGE - 1) & ~(PAGE - 1)
    prelude = total - content
    entries = []
    offset = prelude
    for level in range(levels - 1, -1, -1):
        entries.append((level, offset, sizes[level], slots[level]))
        offset += slots[level]
    return {"levels": levels, "unit": unit, "total": total, "content": content,
            "prelude": prelude, "entries": entries}


def size_candidates(decoded_total: int, width: int, height: int, unit: str,
                    max_levels: int = MAX_LEVELS) -> List[int]:
    """Level counts whose modeled stream length equals the decoded total."""
    out = []
    for levels in range(1, max_levels + 1):
        if slot_layout(width, height, levels, unit)["total"] == decoded_total:
            out.append(levels)
    return out


def aligned_levels(block_sizes: Sequence[int], width: int, height: int, unit: str,
                   max_levels: int = MAX_LEVELS) -> Tuple[List[Tuple[int, int, int]], str]:
    """Peel whole levels from the end while each level start is a block start.

    Returns ``(levels, reason)`` where each level entry is
    ``(level, offset, size)`` and ``level`` 0 is the largest. ``reason`` is
    ``"end of stream"`` on success or the offset that was not a block boundary.
    """
    total = sum(block_sizes)
    boundaries = set()
    cursor = 0
    for size in block_sizes:
        boundaries.add(cursor)
        cursor += size
    if cursor != total:
        raise ValueError("block sizes do not sum to the stream length")
    boundaries.add(total)
    levels = []
    consumed = 0
    for level in range(max_levels):
        size = level_bytes(width >> level, height >> level, unit)
        start = total - consumed - size
        if start < 0:
            return levels, "start below 0"
        if start not in boundaries:
            return levels, f"level {level} start {start} is not a block boundary"
        levels.append((level, start, size))
        consumed += size
    return levels, "level cap reached"


def _rgb565(value: int) -> Tuple[int, int, int]:
    r = (value >> 11) & 0x1F
    g = (value >> 5) & 0x3F
    b = value & 0x1F
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2))


def decode_bc1_block(block: bytes) -> List[Tuple[int, int, int]]:
    """Decode one 8-byte BC1 candidate block. A candidate, not a format id."""
    if len(block) != 8:
        raise ValueError("a BC1 candidate block is 8 bytes")
    c0 = block[0] | (block[1] << 8)
    c1 = block[2] | (block[3] << 8)
    p0 = _rgb565(c0)
    p1 = _rgb565(c1)
    if c0 > c1:
        palette = [p0, p1,
                   tuple((2 * a + b) // 3 for a, b in zip(p0, p1)),
                   tuple((a + 2 * b) // 3 for a, b in zip(p0, p1))]
    else:
        palette = [p0, p1,
                   tuple((a + b) // 2 for a, b in zip(p0, p1)),
                   (0, 0, 0)]
    rows = []
    for y in range(4):
        row = []
        for x in range(4):
            i = y * 4 + x
            sel = (block[4 + (i >> 2)] >> (2 * (i & 3))) & 3
            row.append(palette[sel])
        rows.append(row)
    return rows


def decode_bc1(data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int]]]:
    bw, bh = (width + 3) // 4, (height + 3) // 4
    need = bw * bh * 8
    if len(data) < need:
        raise ValueError(f"BC1 candidate needs {need} bytes, got {len(data)}")
    img = [[(0, 0, 0)] * width for _ in range(height)]
    for by in range(bh):
        for bx in range(bw):
            pixels = decode_bc1_block(data[(by * bw + bx) * 8:(by * bw + bx) * 8 + 8])
            for y in range(4):
                for x in range(4):
                    yy, xx = by * 4 + y, bx * 4 + x
                    if yy < height and xx < width:
                        img[yy][xx] = pixels[y][x]
    return img


def decode_channels(data: bytes, width: int, height: int, channels: int
                    ) -> List[List[Tuple[int, ...]]]:
    if channels < 1:
        raise ValueError("channel count must be positive")
    need = width * height * channels
    if len(data) < need:
        raise ValueError(f"linear candidate needs {need} bytes, got {len(data)}")
    img = []
    for y in range(height):
        row = []
        for x in range(width):
            o = (y * width + x) * channels
            row.append(tuple(data[o:o + channels]))
        img.append(row)
    return img


def decode_bc4_block(block: bytes):
    """Decode one 8-byte single-channel candidate block."""
    if len(block) != 8:
        raise ValueError("a BC4 candidate block is 8 bytes")
    a0, a1 = block[0], block[1]
    if a0 > a1:
        palette = [a0, a1] + [((7 - i) * a0 + i * a1) // 7 for i in range(1, 7)]
    else:
        palette = [a0, a1, (4 * a0 + a1) // 5, (3 * a0 + 2 * a1) // 5,
                   (2 * a0 + 3 * a1) // 5, (a0 + 4 * a1) // 5, 0, 255]
    bits = int.from_bytes(block[2:8], "little")
    return [palette[(bits >> (3 * i)) & 7] for i in range(16)]


def decode_bc4(data: bytes, width: int, height: int, block_bytes: int,
               planes: int):
    """Decode one or two 8-byte channel blocks per 4x4 tile."""
    if block_bytes not in (8, 16):
        raise ValueError("BC4 candidate stride is 8 or 16 bytes")
    if planes < 1 or planes > block_bytes // 8:
        raise ValueError("plane count does not fit the block stride")
    bw, bh = (width + 3) // 4, (height + 3) // 4
    need = bw * bh * block_bytes
    if len(data) < need:
        raise ValueError(f"BC4 candidate needs {need} bytes, got {len(data)}")
    img = [[tuple([0] * planes)] * width for _ in range(height)]
    for by in range(bh):
        for bx in range(bw):
            o = (by * bw + bx) * block_bytes
            values = []
            for plane in range(planes):
                values.append(decode_bc4_block(data[o + 8 * plane:o + 8 * plane + 8]))
            for y in range(4):
                for x in range(4):
                    yy, xx = by * 4 + y, bx * 4 + x
                    if yy < height and xx < width:
                        img[yy][xx] = tuple(v[y * 4 + x] for v in values)
    return img


def decode_level(data: bytes, width: int, height: int, decoder: str,
                 channels: int = 1, unit: str = "L1", planes: int = 1):
    if decoder == "bc1":
        return decode_bc1(data, width, height)
    if decoder == "bc4":
        return decode_bc4(data, width, height,
                          16 if unit == "B16" else 8, planes)
    if decoder == "channels":
        return decode_channels(data, width, height, channels)
    raise ValueError(f"unknown decoder {decoder!r}")


def box_down(img):
    height, width = len(img), len(img[0])
    out = []
    for y in range(height // 2):
        row = []
        for x in range(width // 2):
            values = (img[2 * y][2 * x], img[2 * y][2 * x + 1],
                      img[2 * y + 1][2 * x], img[2 * y + 1][2 * x + 1])
            row.append(tuple(sum(v[c] for v in values) / 4.0
                             for c in range(len(values[0]))))
        out.append(row)
    return out


def mean_abs_error(a, b) -> float:
    if not a or not b or not a[0] or not b[0]:
        return float("nan")
    total = 0.0
    count = 0
    for row_a, row_b in zip(a, b):
        for pa, pb in zip(row_a, row_b):
            if isinstance(pa, tuple):
                total += sum(abs(x - y) for x, y in zip(pa, pb)) / len(pa)
            else:
                total += abs(pa - pb)
            count += 1
    return total / count if count else float("nan")


def block_first_byte_stats(data: bytes, block_size: int) -> dict:
    """First-byte statistics of fixed-size candidate blocks (no pixel output)."""
    if block_size <= 0:
        raise ValueError("block size must be positive")
    first = [data[i] for i in range(0, len(data) - block_size + 1, block_size)]
    if not first:
        return {"blocks": 0}
    modes = collections.Counter()
    zeros = 0
    for value in first:
        if value == 0:
            zeros += 1
            continue
        modes[(value & -value).bit_length() - 1] += 1
    return {
        "blocks": len(first),
        "distinct_first_bytes": len(set(first)),
        "zero_first_bytes": zeros,
        "multiple_of_16_fraction": round(
            sum(1 for value in first if value % 16 == 0) / len(first), 4),
        "all_byte_multiple_of_16_fraction": round(
            sum(1 for value in data if value % 16 == 0) / len(data), 4),
        "lowest_set_bit_counts": {str(k): modes[k] for k in sorted(modes)},
    }


def descriptor_blocks(info: rds5.Rds5File, descriptor_index: int):
    start, end = rds5.descriptor_page_range(info, descriptor_index)
    indices = rds5.blocks_in_range(info, start, end)
    if not indices:
        raise rds5.Rds5Error(f"descriptor {descriptor_index} references no block")
    return start, end, indices


def analyse(path: str, info: rds5.Rds5File, descriptor_index: int, unit: str,
            levels: Optional[int] = None, decoder: str = "none",
            channels: int = 1, planes: int = 1,
            max_uncompressed: int = rds5.DEFAULT_MAX_UNCOMPRESSED,
            max_block_bytes: int = rds5.DEFAULT_MAX_BLOCK_BYTES,
            max_total_bytes: int = rds5.DEFAULT_MAX_TOTAL_BYTES,
            threshold: float = 25.0) -> dict:
    descriptor = info.descriptors[descriptor_index]
    start, end, indices = descriptor_blocks(info, descriptor_index)
    chunks = []
    sizes = []
    classes = []
    for index in indices:
        remaining = max_total_bytes - sum(sizes)
        if remaining <= 0:
            raise rds5.Rds5Error(f"decoded total exceeds cap {max_total_bytes}")
        decoded = rds5.decode_block(
            path, info, index,
            max_uncompressed=min(max_uncompressed, remaining),
            max_block_bytes=max_block_bytes,
        )
        sizes.append(len(decoded.data))
        chunks.append(decoded.data)
        classes.append(decoded.storage_class)
    blob = b"".join(chunks)
    total = len(blob)

    report = {
        "descriptor": descriptor_index,
        "width": descriptor.width,
        "height": descriptor.height,
        "mip_field": descriptor.mip,
        "flags": descriptor.flags,
        "format_id": descriptor.format_id,
        "kind": descriptor.kind,
        "tile_mode": descriptor.tile_mode,
        "page": descriptor.first_page,
        "range_start": start,
        "range_end": end,
        "range_bytes": end - start,
        "block_indices": list(indices),
        "block_classes": [f"0x{c:02x}" for c in classes],
        "block_sizes": sizes,
        "decoded_bytes": total,
        "storage_unit": unit,
        "unit_source": "format table" if OBSERVED_UNITS.get(descriptor.format_id) == unit
                       else "argument",
    }

    candidate_counts = size_candidates(total, descriptor.width, descriptor.height, unit)
    report["size_candidate_levels"] = candidate_counts
    report["size_candidate_unique"] = len(candidate_counts) == 1
    by_field = descriptor.mip + 1
    report["mip_field_plus_one_size_matches"] = by_field in candidate_counts

    aligned, reason = aligned_levels(sizes, descriptor.width, descriptor.height, unit)
    report["aligned_levels"] = [
        {"level": level, "offset": offset, "size": size}
        for level, offset, size in aligned
    ]
    report["aligned_stop"] = reason

    if levels is not None:
        layout = slot_layout(descriptor.width, descriptor.height, levels, unit)
        report["layout"] = {
            "levels": levels,
            "total": layout["total"],
            "prelude": layout["prelude"],
            "entries": [
                {"level": level, "offset": offset, "size": size, "slot": slot}
                for level, offset, size, slot in layout["entries"]
            ],
        }

    if decoder != "none":
        if len(aligned) < 2:
            report["mip_check"] = {"performed": False,
                                   "reason": "fewer than two block-aligned levels"}
        else:
            pairs = []
            images = {}
            for level, offset, size in aligned:
                images[level] = decode_level(
                    blob[offset:offset + size], max(1, descriptor.width >> level),
                    max(1, descriptor.height >> level), decoder, channels, unit, planes)
            for level in range(len(aligned) - 1):
                a = images[level]
                b = images[level + 1]
                if len(a) < 2 or len(a[0]) < 2:
                    continue
                pairs.append({"from_level": level, "to_level": level + 1,
                              "mean_abs_error": round(mean_abs_error(box_down(a), b), 3)})
            worst = max((p["mean_abs_error"] for p in pairs), default=float("nan"))
            report["mip_check"] = {
                "performed": True,
                "decoder": decoder,
                "channels": channels if decoder == "channels" else None,
                "planes": planes if decoder == "bc4" else None,
                "levels_decoded": len(aligned),
                "pairs": pairs,
                "worst_error": worst,
                "threshold": threshold,
                "pass": bool(pairs) and worst < threshold,
            }

    if descriptor.format_id in OBSERVED_UNITS:
        block_size = {"B8": 8, "B16": 16}.get(unit)
        if block_size:
            report["block_first_bytes"] = block_first_byte_stats(blob, block_size)

    return report


def _limits(args: argparse.Namespace) -> rds5.Limits:
    return rds5.Limits(
        max_file_size=args.max_file_size,
        max_records=args.max_records,
        max_etpf_entries=args.max_etpf_entries,
        max_block_bytes=args.max_block_bytes,
    )


def cmd_probe(args: argparse.Namespace) -> int:
    info = rds5.parse(args.path, _limits(args))
    if args.descriptor < 0 or args.descriptor >= len(info.descriptors):
        print(f"error: descriptor {args.descriptor} is outside the table of "
              f"{len(info.descriptors)} entries", file=sys.stderr)
        return 1
    unit = args.unit or OBSERVED_UNITS.get(info.descriptors[args.descriptor].format_id)
    if unit is None:
        print("error: no observed unit for this format id; pass --unit", file=sys.stderr)
        return 1
    report = analyse(args.path, info, args.descriptor, unit,
                     levels=args.levels, decoder=args.decoder,
                     channels=args.channels, planes=args.planes,
                     max_uncompressed=args.max_uncompressed,
                     max_block_bytes=args.max_block_bytes,
                     max_total_bytes=args.max_total_bytes,
                     threshold=args.threshold)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
    return 0


def cmd_units(_args: argparse.Namespace) -> int:
    for fmt in sorted(OBSERVED_UNITS):
        print(f"{fmt}\t{OBSERVED_UNITS[fmt]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Candidate pixel/mip analysis for one decoded RDS5 texture")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--max-file-size", type=int, default=rds5.DEFAULT_MAX_FILE_SIZE)
        sp.add_argument("--max-records", type=int, default=rds5.DEFAULT_MAX_RECORDS)
        sp.add_argument("--max-etpf-entries", type=int,
                        default=rds5.DEFAULT_MAX_ETPF_ENTRIES)
        sp.add_argument("--max-block-bytes", type=int,
                        default=rds5.DEFAULT_MAX_BLOCK_BYTES)

    probe = sub.add_parser("probe", help="analyse one descriptor's decoded stream")
    probe.add_argument("path")
    probe.add_argument("--descriptor", type=int, required=True)
    probe.add_argument("--unit", choices=UNITS,
                       help="storage unit; defaults to the observed format table")
    probe.add_argument("--levels", type=int, help="also print the slot layout for N levels")
    probe.add_argument("--decoder", choices=("none", "bc1", "bc4", "channels"),
                       default="none")
    probe.add_argument("--channels", type=int, default=1)
    probe.add_argument("--planes", type=int, default=1,
                       help="BC4 planes: 1 or 2 (2 only for 16-byte blocks)")
    probe.add_argument("--threshold", type=float, default=25.0)
    probe.add_argument("--json", action="store_true")
    probe.add_argument("--max-uncompressed", type=int,
                       default=rds5.DEFAULT_MAX_UNCOMPRESSED)
    probe.add_argument("--max-total-bytes", type=int,
                       default=rds5.DEFAULT_MAX_TOTAL_BYTES)
    common(probe)
    probe.set_defaults(func=cmd_probe)

    units = sub.add_parser("units", help="print the observed format-id unit table")
    units.set_defaults(func=cmd_units)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (rds5.Rds5Error, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
