import os
import tempfile
import unittest

import pmap_heldout
import synthetic


class PmapHeldoutTests(unittest.TestCase):
    def test_predict_pads_only_between_blocks(self):
        offsets, first = pmap_heldout.predict([17, 16, 24], pad_after_last=False)
        self.assertEqual(offsets, [0x10, 0x30, 0x40])
        self.assertEqual(first, 0x58)

    def test_predict_can_pad_after_last(self):
        offsets, first = pmap_heldout.predict([17, 16, 24], pad_after_last=True)
        self.assertEqual(offsets, [0x10, 0x30, 0x40])
        self.assertEqual(first, 0x60)

    def test_designed_contrast_predicts_unaligned_payloads(self):
        aligned = pmap_heldout.payload_model(
            synthetic.pmap_document([17, 16]), "aligned"
        )
        unaligned = pmap_heldout.payload_model(
            synthetic.pmap_document([17, 16], unaligned=True), "unaligned"
        )
        result = pmap_heldout.evaluate([aligned, unaligned], held_out_count=1)
        contrast = result["designed_alignment_contrast"]
        self.assertEqual(contrast["aligned_payloads"], ["aligned"])
        self.assertEqual(contrast["unaligned_payloads"], ["unaligned"])
        self.assertEqual(contrast["passed"], 1)
        self.assertFalse(contrast["blind"])

    def test_alternative_model_fits_only_the_aligned_payload(self):
        aligned = pmap_heldout.payload_model(
            synthetic.pmap_document([17, 16]), "aligned"
        )
        unaligned = pmap_heldout.payload_model(
            synthetic.pmap_document([17, 16], unaligned=True), "unaligned"
        )
        result = pmap_heldout.evaluate([aligned, unaligned], held_out_count=1)
        self.assertEqual(result["alternative_model_fit"]["no_pad_after_last"], 2)
        self.assertEqual(result["alternative_model_fit"]["pad_after_last"], 1)

    def test_wrong_block_offset_fails_the_check(self):
        row = pmap_heldout.payload_model(
            synthetic.pmap_document([17, 16, 24]), "wrong"
        )
        row["actual_offsets"][1] += 16
        self.assertFalse(pmap_heldout.check(row, False))

    def test_output_inside_sample_directory_is_refused(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as directory:
            with open(os.path.join(directory, "sample.bin"), "wb") as handle:
                handle.write(synthetic.pmap_document())
            with contextlib.redirect_stderr(io.StringIO()):
                result = pmap_heldout.main([
                    "--samples", directory,
                    "--output", os.path.join(directory, "child.json"),
                ])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
