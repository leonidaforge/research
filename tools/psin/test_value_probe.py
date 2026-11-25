import contextlib
import io
import os
import tempfile
import unittest
import zlib

import synthetic
import value_probe
from psin_inspect import PsinError


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

    def test_empty_psch_body_is_a_typed_error(self):
        with self.assertRaises(PsinError) as context:
            value_probe.psch_values_body(b"")
        self.assertIn("shorter than 4", str(context.exception))

    def test_output_inside_sample_directory_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "sample.bin"), "wb") as handle:
                handle.write(synthetic.pmap_document())
            with contextlib.redirect_stderr(io.StringIO()):
                result = value_probe.main([
                    "--samples", directory,
                    "--output", os.path.join(directory, "child.json"),
                ])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
