#!/usr/bin/env python3
"""Synthetic tests for the RBF0 token parser."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest

import rbf0_inspect as inspect
import synthetic


class ParserTests(unittest.TestCase):
    def test_versioned_document_with_every_value_type(self) -> None:
        report = inspect.inspect_bytes(synthetic.all_value_types())
        self.assertEqual(report.header["variant"], "versioned")
        self.assertEqual(report.header["version"], 1)
        self.assertEqual(report.header["number_width"], 8)
        self.assertEqual(report.header["token_start"], 8)
        self.assertEqual(report.counts["elements"], 2)
        self.assertEqual(report.counts["attributes"], 6)
        self.assertEqual(report.counts["text_nodes"], 2)
        self.assertEqual(report.counts["values_by_type"], {1: 3, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2})
        self.assertGreaterEqual(report.counts["name_definitions"], 14)
        self.assertEqual(report.counts["max_depth"], 2)

    def test_versionless_document_uses_four_byte_numbers(self) -> None:
        report = inspect.inspect_bytes(synthetic.versionless_document())
        self.assertEqual(report.header["variant"], "versionless")
        self.assertIsNone(report.header["version"])
        self.assertEqual(report.header["number_width"], 4)
        self.assertEqual(report.header["token_start"], 4)
        self.assertEqual(report.counts["values_by_type"], {1: 1, 4: 1})
        self.assertEqual(report.counts["text_nodes"], 1)

    def test_name_reuse_does_not_define_a_second_name(self) -> None:
        report = inspect.inspect_bytes(synthetic.name_reuse_document())
        self.assertEqual(report.counts["name_definitions"], 2)
        self.assertEqual(report.counts["values_by_type"], {1: 2})
        self.assertEqual(
            [entry["name_index"] for entry in report.definitions], [0, 1]
        )

    def test_nested_document_reports_depth(self) -> None:
        report = inspect.inspect_bytes(synthetic.nested_document(4))
        self.assertEqual(report.counts["max_depth"], 5)
        self.assertEqual(report.counts["elements"], 5)

    def test_depth_limit_is_an_error(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.nested_document(4), max_depth=3)
        self.assertEqual(raised.exception.token, "depth")

    def test_truncated_token(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("truncated_token"))
        self.assertEqual(raised.exception.token, "truncated_token")

    def test_truncated_version_header(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("truncated_version"))
        self.assertEqual(raised.exception.token, "header")

    def test_name_length_past_end(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("name_length_past_end"))
        self.assertEqual(raised.exception.token, "name")

    def test_text_length_past_end(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("text_length_past_end"))
        self.assertEqual(raised.exception.token, "text")

    def test_type6_length_past_end(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("type6_length_past_end"))
        self.assertEqual(raised.exception.token, "value_6")

    def test_name_index_beyond_table(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("name_index_past_table"))
        self.assertEqual(raised.exception.token, "name")
        self.assertIn("beyond the table", raised.exception.message)

    def test_unterminated_element(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("unterminated_element"))
        self.assertEqual(raised.exception.token, "unterminated")

    def test_unsupported_token_class_is_reported(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("unsupported_token"))
        self.assertEqual(raised.exception.token, "unsupported_type_7")

    def test_trailing_bytes(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("trailing_bytes"))
        self.assertEqual(raised.exception.token, "trailing")

    def test_bad_magic(self) -> None:
        with self.assertRaises(inspect.ParseError) as raised:
            inspect.inspect_bytes(synthetic.malformed("bad_magic"))
        self.assertEqual(raised.exception.token, "magic")

    def test_nonzero_reserved_word_is_reported_in_text_output(self) -> None:
        document = synthetic.nonzero_reserved_document()
        report = inspect.inspect_bytes(document)
        self.assertEqual(report.header["nonzero_reserved"][0]["value"], 0x12345678)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "reserved.rbf0")
            with open(path, "wb") as handle:
                handle.write(document)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(inspect.main([path]), 0)
        self.assertIn("nonzero reserved", output.getvalue())
        self.assertIn("0x12345678", output.getvalue())

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            good = os.path.join(directory, "good.rbf0")
            bad = os.path.join(directory, "bad.rbf0")
            with open(good, "wb") as handle:
                handle.write(synthetic.all_value_types())
            with open(bad, "wb") as handle:
                handle.write(synthetic.malformed("unterminated_element"))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(inspect.main([good]), 0)
                self.assertEqual(inspect.main([bad]), 2)
                self.assertEqual(inspect.main([good, "--json"]), 0)
                self.assertEqual(inspect.main([bad, "--json"]), 2)


if __name__ == "__main__":
    unittest.main()
