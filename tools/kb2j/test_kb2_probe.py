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
        self.assertEqual(table["max_interval"], total - 0x49)
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


class RejectionTests(unittest.TestCase):
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
