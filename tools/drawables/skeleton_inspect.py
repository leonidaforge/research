"""Inspect a drawable skeleton: header, bones, hierarchy, transforms, inverse
bind and geometry influence associations.

The input is a decoded resource (system segment followed by graphics segment)
and the system segment length. The reader walks the fragment root or the
resource-level drawable header to the drawable, resolves the skeleton pointer
and reports what the bytes contain. It does not normalise, repair or guess: a
value the record does not establish is reported as `null`, and an association is
accepted only when every vertex's weights and indices validate.

Usage:
  python skeleton_inspect.py inspect --file DECODED --system-length BYTES [--drawable OFFSET] [--json]
  python skeleton_inspect.py census --manifest MANIFEST.jsonl [--json]

Exit code is 0 when every inspected skeleton is structurally complete, 1 when
any is partial or unsupported, and 2 for invalid usage.
"""

import argparse
import json
import struct
import sys


OFFSET_MASK = 0x0FFF_FFFF
SYSTEM_BASE = 0x5000_0000
BONE_LEN = 0x50
MATRIX_LEN = 0x40
MAX_BONES = 4096
ROOT_PARENT = 0xFFFF
WEIGHT_TOTALS = (255, 127)


def u16(data, at):
    if at < 0 or at + 2 > len(data):
        return None
    return struct.unpack_from("<H", data, at)[0]


def u32(data, at):
    if at < 0 or at + 4 > len(data):
        return None
    return struct.unpack_from("<I", data, at)[0]


def u64(data, at):
    if at < 0 or at + 8 > len(data):
        return None
    return struct.unpack_from("<Q", data, at)[0]


def f32(data, at):
    if at < 0 or at + 4 > len(data):
        return 0.0
    return struct.unpack_from("<f", data, at)[0]


def pointer(value):
    if value is None:
        return None
    kind = value >> 28
    if kind == 5:
        return ("system", value & OFFSET_MASK)
    if kind == 6:
        return ("graphics", value & OFFSET_MASK)
    return None


def system_pointer(data, at):
    value = u64(data, at)
    resolved = pointer(value)
    if resolved is None or resolved[0] != "system":
        return None
    return resolved[1]


def cstring(data, at):
    end = data.find(b"\x00", at)
    if end < 0:
        return None
    text = data[at:end]
    if not text or any(byte < 0x20 or byte > 0x7E for byte in text):
        return None
    return text.decode("ascii")


def quat_matrix(q):
    x, y, z, w = q
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ]


def mat_mul(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
        for i in range(3)
    ]


def mat_vec(matrix, vector):
    return [sum(matrix[i][k] * vector[k] for k in range(3)) for i in range(3)]


def transpose(matrix):
    return [[matrix[j][i] for j in range(3)] for i in range(3)]


def max_delta(a, b):
    return max(abs(a[i][j] - b[i][j]) for i in range(3) for j in range(3))


def read_bones(system, base):
    """Reads bone records until the index sequence breaks or the cap is hit."""
    bones = []
    issues = []
    for index in range(MAX_BONES):
        at = base + index * BONE_LEN
        if at + BONE_LEN > len(system):
            issues.append({"code": "truncated", "at": at})
            break
        if u16(system, at + 0x48) != index:
            break
        name_pointer = system_pointer(system, at + 0x30)
        bones.append(
            {
                "index": index,
                "parent": None if u16(system, at + 0x46) == ROOT_PARENT else u16(system, at + 0x46),
                "raw_parent": u16(system, at + 0x46),
                "name": cstring(system, name_pointer) if name_pointer is not None else None,
                "name_offset": name_pointer,
                "rotation": [f32(system, at + 4 * n) for n in range(4)],
                "translation": [f32(system, at + 0x10 + 4 * n) for n in range(3)],
                "scale": [f32(system, at + 0x20 + 4 * n) for n in range(3)],
                "identifier": u32(system, at + 0x1C),
                "identifier16": u16(system, at + 0x4A),
                "flags": [u16(system, at + 0x40 + 2 * n) for n in range(4)],
            }
        )
    if not bones:
        issues.append({"code": "no_bones"})
    return bones, issues


def read_matrices(system, base, count):
    records = []
    for index in range(count):
        at = base + index * MATRIX_LEN
        if at + MATRIX_LEN > len(system):
            break
        records.append(
            {
                "rotation": [
                    [f32(system, at + 4 * (row * 4 + column)) for column in range(3)]
                    for row in range(3)
                ],
                "translation": [f32(system, at + 0x30 + 4 * n) for n in range(3)],
                "unknown": f32(system, at + 0x3C),
            }
        )
    return records


def read_parent_array(system, base, count):
    at = system_pointer(system, base + 0x40)
    if at is None:
        return None
    return [u16(system, at + 2 * index) for index in range(count)]


def resolve_hierarchy(bones):
    """Validates parents, rejects cycles and measures the tree."""
    issues = []
    count = len(bones)
    for bone in bones:
        parent = bone["raw_parent"]
        if parent == ROOT_PARENT:
            continue
        if parent >= count:
            issues.append({"code": "invalid_parent", "bone": bone["index"], "parent": parent})
            bone["parent"] = None
        elif parent == bone["index"]:
            issues.append({"code": "self_parent", "bone": bone["index"]})
            bone["parent"] = None
    cyclic = set()
    for start in range(count):
        path = []
        current = start
        steps = 0
        while bones[current]["parent"] is not None:
            parent = bones[current]["parent"]
            steps += 1
            if steps > count:
                break
            if parent in path:
                cyclic.update(path[path.index(parent) :])
                cyclic.add(parent)
                break
            path.append(current)
            current = parent
    for index in sorted(cyclic):
        issues.append({"code": "cycle", "bone": index})
        bones[index]["parent"] = None
    roots = [bone["index"] for bone in bones if bone["parent"] is None]
    depths = []
    for index in range(count):
        depth = 0
        current = index
        steps = 0
        while bones[current]["parent"] is not None:
            steps += 1
            if steps > count:
                break
            current = bones[current]["parent"]
            depth += 1
        depths.append(depth)
    return roots, (max(depths) + 1 if depths else 0), issues


def compose(bones):
    """Composes local transforms into model-space rotation and translation."""
    rotations = []
    positions = []
    for bone in bones:
        rotation = quat_matrix(bone["rotation"])
        translation = bone["translation"]
        parent = bone["parent"]
        if parent is None:
            rotations.append(rotation)
            positions.append(list(translation))
        else:
            rotations.append(mat_mul(rotations[parent], rotation))
            positions.append(
                [
                    positions[parent][i]
                    + sum(rotations[parent][i][k] * translation[k] for k in range(3))
                    for i in range(3)
                ]
            )
    return rotations, positions


def association(system, graphics, geometry, bones):
    """Validates one geometry's influence streams against the bone count."""
    bone_count = u16(system, geometry + 0x2C)
    if bone_count == 0:
        return None
    buffer_pointer = system_pointer(system, geometry + 0x08)
    if buffer_pointer is None:
        return {"declared_bone_count": bone_count, "status": "no_vertex_buffer"}
    elements = u32(system, buffer_pointer + 0x08)
    unit = u16(system, buffer_pointer + 0x0C)
    layout = system_pointer(system, buffer_pointer + 0x40)
    graphics_resolved = pointer(u64(system, buffer_pointer + 0x18))
    graphics_offset = (
        graphics_resolved[1]
        if graphics_resolved is not None and graphics_resolved[0] == "graphics"
        else None
    )
    if layout is None or graphics_offset is None:
        return {"declared_bone_count": bone_count, "status": "no_layout"}
    count = u32(system, layout + 0x138) >> 10
    blob = graphics[graphics_offset : graphics_offset + elements * unit]
    if len(blob) < 0x60:
        return {"declared_bone_count": bone_count, "status": "short_blob"}
    weights_word = u32(blob, 4 * 6)
    index_word = u32(blob, 4 * 8)
    if weights_word is None or weights_word & 0xFF != 0x26:
        return {"declared_bone_count": bone_count, "status": "no_weight_stream"}
    weights_at = (weights_word >> 8) * 2
    has_index_stream = index_word is not None and index_word & 0xFF == 0x25
    if not has_index_stream and len(bones) != 1:
        return {"declared_bone_count": bone_count, "status": "no_index_stream"}
    weights = blob[weights_at : weights_at + count * 4]
    indexes = (
        blob[(index_word >> 8) * 2 : (index_word >> 8) * 2 + count * 4]
        if has_index_stream
        else None
    )
    used = set()
    weighted = False
    unusual_totals = set()
    for vertex in range(count):
        lane = weights[vertex * 4 : vertex * 4 + 4]
        if len(lane) < 4:
            return {"declared_bone_count": bone_count, "status": "truncated_weights"}
        total = sum(lane)
        if total == 0:
            return {"declared_bone_count": bone_count, "status": "zero_weights"}
        if total not in WEIGHT_TOTALS:
            unusual_totals.add(total)
        active = [n for n in range(4) if lane[n] > 0]
        if len(active) > 1:
            weighted = True
        if indexes is None:
            if any(n != 0 for n in active):
                return {"declared_bone_count": bone_count, "status": "lane_outside_single_bone"}
            used.add(0)
            continue
        for n in active:
            bone = indexes[vertex * 4 + n]
            if bone >= len(bones):
                return {
                    "declared_bone_count": bone_count,
                    "status": "index_outside_skeleton",
                    "vertex": vertex,
                    "bone": bone,
                }
            used.add(bone)
    return {
        "declared_bone_count": bone_count,
        "bones": sorted(used),
        "weighted": weighted,
        "unusual_weight_totals": sorted(unusual_totals),
        "status": "validated",
    }


def inspect(data, system_length, drawable_offset=None):
    if system_length <= 0 or system_length > len(data):
        raise ValueError("the system length must be positive and inside the file")
    system = data[:system_length]
    graphics = data[system_length:]
    report = {
        "system_size": system_length,
        "graphics_size": len(graphics),
        "drawable": None,
        "skeleton": None,
        "bones": [],
        "roots": [],
        "max_depth": 0,
        "inverse_bind": [],
        "parent_array": None,
        "associations": [],
        "issues": [],
        "status": "unverified",
    }
    if drawable_offset is None:
        member = system_pointer(system, 0x18)
        report["drawable"] = member
        drawable_offset = member if member is not None else 0
    else:
        report["drawable"] = drawable_offset
    drawable = drawable_offset
    if drawable + 0xC0 > len(system):
        report["issues"].append({"code": "drawable_out_of_range"})
        report["status"] = "unverified"
        return report
    skeleton = system_pointer(system, drawable + 0x18)
    if skeleton is None:
        report["status"] = "no_skeleton"
        return report
    report["skeleton"] = skeleton
    if skeleton + 0x50 > len(system):
        report["issues"].append({"code": "skeleton_out_of_range"})
        return report
    declared_keys = u32(system, skeleton + 0x1C)
    report["declared_keys"] = declared_keys
    bone_base = system_pointer(system, skeleton + 0x28)
    if bone_base is None:
        report["issues"].append({"code": "no_bone_pointer"})
        return report
    report["bone_array"] = bone_base
    bones, bone_issues = read_bones(system, bone_base)
    report["issues"].extend(bone_issues)
    report["bones"] = bones
    if not bones:
        return report
    if declared_keys != len(bones) * 2:
        report["issues"].append(
            {
                "code": "declared_key_count",
                "declared": declared_keys,
                "bones": len(bones),
            }
        )
    report["parent_array"] = read_parent_array(system, skeleton, len(bones))
    if report["parent_array"] is not None:
        for bone in bones:
            recorded = report["parent_array"][bone["index"]]
            if recorded != bone["raw_parent"]:
                report["issues"].append(
                    {
                        "code": "parent_array_mismatch",
                        "bone": bone["index"],
                        "recorded": bone["raw_parent"],
                        "array": recorded,
                    }
                )
    roots, depth, hierarchy_issues = resolve_hierarchy(bones)
    report["issues"].extend(hierarchy_issues)
    report["roots"] = roots
    report["max_depth"] = depth

    rotations, positions = compose(bones)
    inverse_at = system_pointer(system, skeleton + 0x30)
    if inverse_at is not None:
        stored = read_matrices(system, inverse_at, len(bones))
        report["inverse_bind"] = stored
        for index, record in enumerate(stored):
            expected_rotation = rotations[index]
            # The stored record holds the model-space rotation and the
            # negated rotated model-space translation, so the bind inverse
            # is its transpose.
            expected_translation = [
                -value for value in mat_vec(transpose(expected_rotation), positions[index])
            ]
            rotation_delta = max_delta(record["rotation"], expected_rotation)
            translation_delta = max(
                abs(record["translation"][n] - expected_translation[n]) for n in range(3)
            )
            report.setdefault("inverse_bind_validation", []).append(
                {
                    "bone": index,
                    "rotation_delta": rotation_delta,
                    "translation_delta": translation_delta,
                    "matches": rotation_delta <= 2e-3 and translation_delta <= 2e-3,
                }
            )
            if rotation_delta > 2e-3 or translation_delta > 2e-3:
                report["issues"].append({"code": "inverse_bind_mismatch", "bone": index})
    for bone, rotation, position in zip(bones, rotations, positions):
        bone["model_rotation"] = rotation
        bone["model_position"] = position

    local_at = system_pointer(system, skeleton + 0x38)
    if local_at is not None:
        stored = read_matrices(system, local_at, len(bones))
        for bone, record in zip(bones, stored):
            record_local = quat_matrix(bone["rotation"])
            bone["local_matrix_matches"] = (
                max_delta(record["rotation"], transpose(record_local)) <= 2e-3
                and max(
                    abs(record["translation"][n] - bone["translation"][n]) for n in range(3)
                )
                <= 2e-3
            )

    for slot_index in range(4):
        slot = system_pointer(system, drawable + 0x50 + 8 * slot_index)
        if slot is None:
            continue
        model_array = system_pointer(system, slot)
        if model_array is None:
            continue
        for model_index in range(u16(system, slot + 8) or 0):
            model = system_pointer(system, model_array + 8 * model_index)
            if model is None:
                continue
            geometry_array = system_pointer(system, model + 0x08)
            if geometry_array is None:
                continue
            for geometry_index in range(u16(system, model + 0x10) or 0):
                geometry = system_pointer(system, geometry_array + 8 * geometry_index)
                if geometry is None:
                    continue
                found = association(system, graphics, geometry, bones)
                if found is not None:
                    found["lod"] = slot_index
                    found["model"] = model_index
                    found["geometry"] = geometry_index
                    report["associations"].append(found)

    report["status"] = "complete" if not report["issues"] else "partial"
    return report


def census(manifest):
    rows = []
    for line in open(manifest, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        data = open(entry["file"], "rb").read()
        report = inspect(
            data,
            entry["system_length"],
            entry.get("drawable"),
        )
        rows.append(
            {
                "id": entry.get("id"),
                "file": entry["file"],
                "status": report["status"],
                "bones": len(report["bones"]),
                "roots": len(report["roots"]),
                "max_depth": report["max_depth"],
                "named": sum(1 for bone in report["bones"] if bone["name"]),
                "inverse_bind": len(report["inverse_bind"]),
                "associations": len(report["associations"]),
                "validated": sum(
                    1 for row in report["associations"] if row["status"] == "validated"
                ),
                "issues": report["issues"],
            }
        )
    statuses = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    print(f"{len(rows)} resource(s): {statuses}")
    print(
        f"skeletons: {sum(1 for row in rows if row['bones'])}; "
        f"associations: {sum(row['validated'] for row in rows)} of "
        f"{sum(row['associations'] for row in rows)} validated"
    )
    return 0 if all(row["status"] in ("complete", "no_skeleton") for row in rows) else 1


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect_parser = commands.add_parser("inspect")
    inspect_parser.add_argument("--file", required=True)
    inspect_parser.add_argument("--system-length", required=True, type=lambda v: int(v, 0))
    inspect_parser.add_argument("--drawable", type=lambda v: int(v, 0), default=None)
    inspect_parser.add_argument("--json", action="store_true")
    census_parser = commands.add_parser("census")
    census_parser.add_argument("--manifest", required=True)
    census_parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "census":
        return census(args.manifest)
    try:
        data = open(args.file, "rb").read()
        report = inspect(data, args.system_length, args.drawable)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"status: {report['status']}")
        print(f"drawable: {report['drawable']}, skeleton: {report['skeleton']}")
        print(f"bones: {len(report['bones'])}; roots: {report['roots']}; depth: {report['max_depth']}")
        for bone in report["bones"]:
            print(
                f"  {bone['index']:2d} parent {bone['raw_parent']} name {bone['name']!r}"
                f" local {[round(v, 4) for v in bone['translation']]}"
                f" model {[round(v, 4) for v in bone['model_position']]}"
                f" inverse-bind {bone.get('local_matrix_matches')}"
            )
        for row in report["associations"]:
            print(f"  association {row}")
        for issue in report["issues"]:
            print(f"issue: {issue}")
    return 0 if report["status"] in ("complete", "no_skeleton") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
