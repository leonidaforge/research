import json
import os
import struct
import tempfile
import unittest
from pathlib import Path

import kb2_probe as probe


def header(signature, size, frames, largest, width, height, audio_count, variant):
    data = bytearray(probe.HEADER_SIZE)
    data[0:4] = signature
    struct.pack_into("<I", data, 0x04, size)
    struct.pack_into("<I", data, 0x08, frames)
    struct.pack_into("<I", data, 0x0C, largest)
    struct.pack_into("<I", data, 0x10, frames)
    struct.pack_into("<I", data, 0x14, width)
    struct.pack_into("<I", data, 0x18, height)
    struct.pack_into("<I", data, 0x1C, 30)
    struct.pack_into("<I", data, 0x20, 1)
    struct.pack_into("<H", data, 0x24, 18)
    struct.pack_into("<H", data, 0x26, 16)
    struct.pack_into("<I", data, 0x28, audio_count)
    struct.pack_into("<I", data, 0x2C, variant)
    return data


def write_payload(directory, name, body):
    path = Path(directory) / name
    path.write_bytes(body)
    return str(path)


class VideoOnlyTests(unittest.TestCase):
    def test_kb2j_header_and_frame_table(self):
        frames = 3
        total = 0x50
        table_end = 0x30 + 4 * (frames + 1)
        offsets = [table_end + 1, 0x45, 0x49, total]
        body = header(b"KB2j", total - 8, frames, 8, 16, 16, 0, 0x02070D00)
        body += struct.pack(f"<{len(offsets)}I", *offsets)
        body += bytes(total - len(body))

        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(write_payload(directory, "sample.bin", body))

        self.assertEqual(result["signature"], "KB2j")
        self.assertEqual(result["declared_size"], total)
        self.assertTrue(result["size_field_matches_file"])
        self.assertEqual(result["frame_count"], frames)
        self.assertEqual(result["width"], 16)
        self.assertEqual(result["height"], 16)
        self.assertEqual(result["rate_numerator"], 30)
        self.assertEqual(result["rate_denominator"], 1)
        self.assertEqual(result["audio_track_count"], 0)
        self.assertEqual(result["variant"], "0x02070D00")
        table = result["frame_table"]
        self.assertTrue(table["monotonic"])
        self.assertTrue(table["first_is_end_plus_one"])
        self.assertTrue(table["last_is_file_size"])
        self.assertEqual(table["max_interval"], total - 0x48)
        self.assertTrue(table["max_interval_within_largest"])
        self.assertTrue(probe._valid(result))


class AudioTests(unittest.TestCase):
    def test_kb2n_audio_descriptors(self):
        frames = 2
        total = 0x60
        table_end = 0x30 + 12 + 4 * (frames + 1)
        offsets = [table_end + 1, 0x4D, total]
        body = header(b"KB2n", total - 8, frames, 32, 32, 32, 1, 0x87E90500)
        body += struct.pack("<III", 145920, 0x7000BB80, 0)
        body += struct.pack(f"<{len(offsets)}I", *offsets)
        body += bytes(total - len(body))

        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(write_payload(directory, "sample.bin", body))

        self.assertEqual(result["signature"], "KB2n")
        self.assertEqual(result["audio_track_count"], 1)
        self.assertEqual(result["variant"], "0x87E90500")
        self.assertEqual(len(result["audio_tracks"]), 1)
        track = result["audio_tracks"][0]
        self.assertEqual(track["sample_rate"], 48000)
        self.assertEqual(track["flags"], 0x7000)
        self.assertEqual(track["size_value"], 145920)
        self.assertEqual(result["frame_table"]["start"], 0x3C)
        self.assertTrue(probe._valid(result))


class ValidationTests(unittest.TestCase):
    def test_flags_are_one_u32_with_alpha_bit(self):
        total = 0x60
        body = header(b"KB2j", total - 8, 1, 8, 16, 16, 0, 0)
        body += struct.pack("<III", 0x41, total, 0)
        body += bytes(total - len(body))
        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(write_payload(directory, "sample.bin", body))
        self.assertEqual(result["flags"], "0x00100012")
        self.assertEqual(result["flags_low16"], 18)
        self.assertEqual(result["flags_high16"], 16)
        self.assertTrue(result["alpha_bit"])

    def test_frame_offsets_use_bit_zero_as_keyframe(self):
        frames = 3
        total = 0x60
        table_end = 0x30 + 4 * (frames + 1)
        offsets = [table_end + 1, table_end + 8, (table_end + 8) | 1, total]
        body = header(b"KB2j", total - 8, frames, 32, 16, 16, 0, 0)
        body += struct.pack(f"<{len(offsets)}I", *offsets)
        body += bytes(total - len(body))
        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(write_payload(directory, "sample.bin", body))
        table = result["frame_table"]
        self.assertTrue(table["first_is_end_plus_one"])
        self.assertTrue(table["first_masked_is_table_end"])
        self.assertTrue(table["masked_monotonic"])
        self.assertTrue(table["last_is_file_size"])
        self.assertTrue(table["last_is_even"])
        self.assertTrue(result["validation"]["keyframe_entries"] >= 1)

    def test_audio_record_layout(self):
        frames = 2
        total = 0x70
        table_end = 0x48
        offsets = [table_end + 1, 0x60, total]
        body = header(b"KB2n", total - 8, frames, 32, 32, 32, 1, 0x87E90500)
        body += struct.pack("<III", 145920, 0x7000BB80, 0)
        body += struct.pack(f"<{len(offsets)}I", *offsets)
        body += struct.pack("<II", 20, 145920) + bytes(16)
        body += struct.pack("<II", 12, 7680) + bytes(8)
        self.assertEqual(len(body), total)
        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(
                write_payload(directory, "sample.bin", body), validate_frames=True
            )
        audio = result["audio_validation"]
        self.assertEqual(audio["frames"], 2)
        self.assertEqual(audio["packets"], 2)
        self.assertEqual(audio["zero_packets"], 0)
        self.assertEqual(audio["max_packet"], 20)
        self.assertEqual(audio["max_decoded"], 145920)
        self.assertEqual(audio["array1"], 145920)
        self.assertTrue(audio["array1_is_max_decoded"])
        self.assertEqual(audio["violations"], [])

    def test_audio_record_past_frame_is_reported(self):
        frames = 1
        total = 0x58
        table_end = 0x44
        offsets = [table_end + 1, total]
        body = header(b"KB2n", total - 8, frames, 32, 32, 32, 1, 0x87E90500)
        body += struct.pack("<III", 145920, 0x7000BB80, 0)
        body += struct.pack(f"<{len(offsets)}I", *offsets)
        body += struct.pack("<II", 64, 145920) + bytes(total - len(body) - 8)
        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(
                write_payload(directory, "sample.bin", body), validate_frames=True
            )
        kinds = {item["kind"] for item in result["audio_validation"]["violations"]}
        self.assertIn("record_past_frame", kinds)

    def test_manifest_summary(self):
        first_total = 0x50
        first = header(b"KB2j", first_total - 8, 1, 8, 16, 16, 0, 0)
        first += struct.pack("<II", 0x41, first_total)
        first += bytes(first_total - len(first))

        second_total = 0x70
        second = header(b"KB2n", second_total - 8, 2, 32, 32, 32, 1, 0x87E90500)
        second += struct.pack("<III", 145920, 0x7000BB80, 0)
        second += struct.pack("<III", 0x49, 0x60, second_total)
        second += struct.pack("<II", 20, 145920) + bytes(16)
        second += struct.pack("<II", 12, 7680) + bytes(8)

        with tempfile.TemporaryDirectory() as directory:
            archive = os.path.join(directory, "archive.bin")
            with open(archive, "wb") as handle:
                handle.write(first)
                handle.write(second)
            manifest = os.path.join(directory, "rows.jsonl")
            with open(manifest, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps({
                    "kind": "row", "row": 0, "payload_offset": "0x0",
                    "logical_size": len(first),
                }) + "\n")
                handle.write(json.dumps({
                    "kind": "row", "row": 1, "payload_offset": hex(len(first)),
                    "logical_size": len(second),
                }) + "\n")
            results = probe.probe_manifest(
                archive, manifest, validate_frames=True
            )
        summary = probe.summarize(results)
        self.assertEqual(summary["samples"], 2)
        self.assertEqual(summary["signatures"], {"KB2j": 1, "KB2n": 1})
        self.assertEqual(summary["audio_rows"], 1)
        self.assertEqual(summary["frames"], 2)
        self.assertEqual(summary["packets"], 2)
        self.assertEqual(summary["array1_is_max_decoded"], 1)

    def test_atomic_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "report.json")
            probe._write_atomic(target, "content\n")
            with open(target, encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "content\n")


class RejectionTests(unittest.TestCase):
    def test_zero_frame_payload_is_rejected(self):
        total = 0x40
        body = header(b"KB2j", total - 8, 0, 0, 16, 16, 0, 0)
        body += struct.pack("<I", total)
        body += bytes(total - len(body))
        with tempfile.TemporaryDirectory() as directory:
            path = write_payload(directory, "sample.bin", body)
            with self.assertRaises(probe.Kb2Error):
                probe.probe_file(path)

    def test_unknown_signature_is_rejected(self):
        body = header(b"XXXX", 0x48, 1, 8, 16, 16, 0, 0)
        body += struct.pack("<II", 0x41, 0x50)
        body += bytes(0x50 - len(body))
        with tempfile.TemporaryDirectory() as directory:
            path = write_payload(directory, "sample.bin", body)
            with self.assertRaises(probe.Kb2Error):
                probe.probe_file(path)

    def test_non_monotonic_table_is_reported(self):
        frames = 2
        total = 0x50
        table_end = 0x30 + 4 * (frames + 1)
        offsets = [0x41, 0x50, 0x45, total]
        body = header(b"KB2j", total - 8, frames, 32, 16, 16, 0, 0)
        body += struct.pack(f"<{len(offsets)}I", *offsets)
        body += bytes(total - len(body))
        with tempfile.TemporaryDirectory() as directory:
            result = probe.probe_file(write_payload(directory, "sample.bin", body))
        self.assertFalse(result["frame_table"]["monotonic"])
        self.assertFalse(probe._valid(result))

    def test_table_limit_is_enforced(self):
        frames = 4
        total = 0x60
        body = header(b"KB2j", total - 8, frames, 8, 16, 16, 0, 0)
        body += bytes(total - len(body))
        with tempfile.TemporaryDirectory() as directory:
            path = write_payload(directory, "sample.bin", body)
            with self.assertRaises(probe.Kb2Error):
                probe.probe_file(path, max_table_bytes=4)

    def test_truncated_table_is_rejected(self):
        body = header(b"KB2j", 0x08, 100, 8, 16, 16, 0, 0)
        with tempfile.TemporaryDirectory() as directory:
            path = write_payload(directory, "sample.bin", body)
            with self.assertRaises(probe.Kb2Error):
                probe.probe_file(path)


if __name__ == "__main__":
    unittest.main()
