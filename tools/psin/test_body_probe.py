import contextlib
import io
import os
import struct
import tempfile
import unittest

import body_probe
import synthetic


class BodyProbeTests(unittest.TestCase):
    def test_lsch_and_lenm_counts(self):
        raw = synthetic.lsch_document([4], sections=[
            (b"LSCH", b"\x11" * 8 + synthetic.le32(3) + synthetic.le32(0)
             + synthetic.AA + struct.pack("<IHH", 4, 0, 1) + b"\0" * 16),
            (b"LENM", b"\x01" * 8 + b"\xEE" * 8 + synthetic.le32(3)
             + b"\0" * 12
             + b"\x02" * 8 + synthetic.le32(1) + synthetic.le32(0)
             + b"\x03" * 8 + synthetic.le32(2) + synthetic.le32(0)
             + b"\x04" * 8),
            (b"LSNS", synthetic.be32(0)),
            (b"LGID", b""),
            (b"LRSC", b"\0" * 80),
        ])
        report = body_probe.inspect_payload(raw, "lsch")
        self.assertEqual(report["lsch"]["marker_count"], 1)
        self.assertEqual(report["lenm"]["count"], 3)
        self.assertTrue(report["lenm"]["header_multiple_8"])

    def test_pmap_names_and_psch_unused_ids(self):
        raw = synthetic.pmap_document()
        report = body_probe.inspect_payload(raw, "pmap")
        self.assertTrue(report["names"]["block"])
        self.assertEqual(report["names"]["count"], 2)
        self.assertGreaterEqual(report["psch"]["unused_by_blocks"], 0)

    def test_output_inside_sample_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "sample.bin"), "wb") as handle:
                handle.write(synthetic.pmap_document())
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = body_probe.main([
                    "--samples", directory,
                    "--output", os.path.join(directory, "child.json"),
                    "--summary-only",
                ])
        self.assertEqual(result, 1)
        self.assertIn("inside the sample directory", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
