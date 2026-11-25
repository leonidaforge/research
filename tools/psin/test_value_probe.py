import contextlib
import io
import os
import unittest
import zlib

import synthetic
import value_probe


class ValueProbeTests(unittest.TestCase):
    def test_zlib_value_is_detected(self):
        value = zlib.compress(b"value" * 100)
        data = synthetic.pmap_document(psch_values=[value])
        report = value_probe.probe(data, "zlib")
        self.assertEqual(report["values"]["decoders"]["zlib"], 1)

    def test_zstd_signature_is_detected(self):
        data = synthetic.pmap_document(psch_values=[b"\x28\xb5\x2f\xfd" + b"\0" * 12])
        report = value_probe.probe(data, "zstd")
        self.assertEqual(report["values"]["signatures"]["zstd"], 1)

    def test_width_summary_reports_common_divisors(self):
        summary = value_probe.width_summary([b"A" * 16, b"B" * 20])
        self.assertEqual(summary["common_divisors_1_to_64"], [1, 2, 4])
        self.assertEqual(summary["divisors_above_8"], [])

    def test_output_refuses_the_sample_directory(self):
        with contextlib.redirect_stderr(io.StringIO()):
            result = value_probe.main(["--samples", ".", "--output", "."])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
