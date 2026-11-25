import contextlib
import io
import os
import unittest
import zlib

import blob_probe
import synthetic


class BlobProbeTests(unittest.TestCase):
    def test_zlib_blob_is_detected(self):
        blob = zlib.compress(b"texture" * 100)
        data = synthetic.edup_document([], blob)
        report = blob_probe.probe_document(data, "zlib")
        self.assertTrue(report["decoders"]["zlib"]["ok"])
        self.assertGreater(report["decoders"]["zlib"]["output_length"], 0)

    def test_random_blob_is_negative(self):
        blob = bytes((index * 37 + 11) & 0xFF for index in range(160))
        data = synthetic.edup_document([], blob)
        report = blob_probe.probe_document(data, "random")
        self.assertFalse(any(value["ok"] for value in report["decoders"].values()))
        self.assertFalse(report["signatures"]["zstd"])

    def test_common_divisors_include_eight_and_sixteen(self):
        reports = [
            blob_probe.probe_document(synthetic.edup_document([], b"\xA5" * 16), "a"),
            blob_probe.probe_document(synthetic.edup_document([], b"\xA5" * 160), "b"),
        ]
        summary = blob_probe.aggregate(reports)
        self.assertEqual(summary["common_divisors_1_to_64"], [1, 2, 4, 8, 16])
        self.assertEqual(summary["common_divisors_above_16"], [])

    def test_width_table_can_match_entry_count_when_present(self):
        # A 16-byte blob at width 16 has one record; the table has one entry.
        data = synthetic.edup_document([(1, 2)], b"\xA5" * 16)
        report = blob_probe.probe_document(data, "one")
        check = next(item for item in report["width_checks"] if item["width"] == 16)
        self.assertTrue(check["matches_entry_count"])
        self.assertEqual(check["records"], 1)

    def test_zstd_signature_is_detected(self):
        data = synthetic.edup_document([], b"\x28\xb5\x2f\xfd" + b"\0" * 12)
        report = blob_probe.probe_document(data, "zstd")
        self.assertTrue(report["signatures"]["zstd"])

    def test_store_key_hit_is_detected(self):
        key = 0x1122334455667788
        blob = key.to_bytes(8, "little") + b"\0" * 24
        data = synthetic.edup_document([], blob)
        report = blob_probe.probe_document(data, "key", store_keys={"store": {key}})
        self.assertEqual(report["store_key_hits"], 1)
        self.assertEqual(report["store_key_hits_be"], 0)

    def test_store_key_absence_is_reported(self):
        blob = b"\xA5" * 32
        data = synthetic.edup_document([], blob)
        report = blob_probe.probe_document(data, "none", store_keys={"store": {1, 2, 3}})
        self.assertEqual(report["store_key_hits"], 0)
        self.assertEqual(report["store_key_hits_be"], 0)

    def test_output_refuses_an_input_path(self):
        path = "blob-input.tmp"
        with open(path, "wb") as handle:
            handle.write(synthetic.edup_document([], b"\0" * 16))
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                result = blob_probe.main([path, "--output", path])
        finally:
            os.remove(path)
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
