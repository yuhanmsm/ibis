import io
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from allocations.services.csv_reader import CsvReadError, CsvRow, read_csv

SAMPLE_COHORT = Path(__file__).parent.parent / "fixtures" / "sample_student_cohort_data.csv"


def upload(text: str, encoding: str = "utf-8") -> SimpleUploadedFile:
    """Create an uploaded CSV file containing the given text."""
    return SimpleUploadedFile("cohort.csv", text.encode(encoding), "text/csv")


class ReadSampleCohortTest(SimpleTestCase):
    """The sample file supplied with the assignment."""

    def setUp(self):
        with SAMPLE_COHORT.open("rb") as file:
            self.table = read_csv(file)

    def test_reads_header(self):
        self.assertEqual(
            self.table.header,
            (
                "first_name",
                "last_name",
                "email",
                "gender",
                "ethnicity",
                "c-score",
                "schedule",
                "ambition",
            ),
        )

    def test_reads_every_student(self):
        self.assertEqual(len(self.table.rows), 300)

    def test_every_row_has_one_value_per_column(self):
        for row in self.table.rows:
            self.assertEqual(len(row.cells), 8, f"line {row.line_number}")

    def test_keeps_commas_inside_quoted_values(self):
        first_row = self.table.rows[0]
        self.assertEqual(
            first_row.cells,
            (
                "Rahul",
                "Khan",
                "rahul.khan@students.example",
                "2: Man",
                "1: Asian, or Asian British",
                "57",
                "1: Yes",
                "1: Exceed workload",
            ),
        )

    def test_numbers_rows_by_line_in_file(self):
        self.assertEqual(self.table.rows[0].line_number, 2)
        self.assertEqual(self.table.rows[-1].line_number, 301)


class ReadCsvTest(SimpleTestCase):
    def test_reads_header_and_rows(self):
        table = read_csv(upload("first_name,last_name\nAda,Lovelace\n"))
        self.assertEqual(table.header, ("first_name", "last_name"))
        self.assertEqual(table.rows, (CsvRow(2, ("Ada", "Lovelace")),))

    def test_reads_header_without_rows(self):
        table = read_csv(upload("first_name,last_name,email\n"))
        self.assertEqual(table.header, ("first_name", "last_name", "email"))
        self.assertEqual(table.rows, ())

    def test_ignores_byte_order_mark(self):
        table = read_csv(upload("﻿first_name,last_name\nAda,Lovelace\n"))
        self.assertEqual(table.header[0], "first_name")

    def test_reads_windows_line_endings(self):
        table = read_csv(upload("first_name,last_name\r\nAda,Lovelace\r\n"))
        self.assertEqual(table.rows, (CsvRow(2, ("Ada", "Lovelace")),))

    def test_reads_file_without_final_line_ending(self):
        table = read_csv(upload("first_name\nAda"))
        self.assertEqual(table.rows, (CsvRow(2, ("Ada",)),))

    def test_removes_spaces_around_values_and_column_names(self):
        table = read_csv(upload(" first_name , email \n Ada , ada@example.org \n"))
        self.assertEqual(table.header, ("first_name", "email"))
        self.assertEqual(table.rows[0].cells, ("Ada", "ada@example.org"))

    def test_keeps_empty_values(self):
        table = read_csv(upload("first_name,gender,c-score\nAda,,\n"))
        self.assertEqual(table.rows[0].cells, ("Ada", "", ""))

    def test_skips_blank_lines_but_keeps_line_numbers(self):
        table = read_csv(upload("first_name\n\nAda\n , \nGrace\n\n"))
        self.assertEqual(
            table.rows, (CsvRow(3, ("Ada",)), CsvRow(5, ("Grace",)))
        )

    def test_skips_blank_lines_before_header(self):
        table = read_csv(upload("\n\nfirst_name\nAda\n"))
        self.assertEqual(table.header, ("first_name",))
        self.assertEqual(table.rows, (CsvRow(4, ("Ada",)),))

    def test_keeps_rows_with_too_many_or_too_few_values(self):
        table = read_csv(upload("first_name,last_name\nAda\nGrace,Hopper,extra\n"))
        self.assertEqual(table.rows[0].cells, ("Ada",))
        self.assertEqual(table.rows[1].cells, ("Grace", "Hopper", "extra"))

    def test_keeps_line_breaks_inside_quoted_values(self):
        table = read_csv(upload('first_name,note\nAda,"two\nlines"\nGrace,x\n'))
        self.assertEqual(table.rows[0].cells, ("Ada", "two\nlines"))
        self.assertEqual(table.rows[1].line_number, 4)

    def test_reads_any_file_like_object(self):
        table = read_csv(io.BytesIO(b"first_name\nAda\n"))
        self.assertEqual(table.rows, (CsvRow(2, ("Ada",)),))


class ReadInvalidCsvTest(SimpleTestCase):
    def assert_read_error(self, uploaded_file, expected_message, **kwargs):
        with self.assertRaises(CsvReadError) as context:
            read_csv(uploaded_file, **kwargs)
        self.assertIn(expected_message, str(context.exception))

    def test_rejects_empty_file(self):
        self.assert_read_error(upload(""), "The file is empty.")

    def test_rejects_file_of_blank_lines(self):
        self.assert_read_error(upload("\n \n,,\n"), "The file is empty.")

    def test_rejects_file_that_is_not_utf8(self):
        self.assert_read_error(
            upload("first_name\nZoë\n", encoding="latin-1"), "not UTF-8 text"
        )

    def test_rejects_binary_file(self):
        self.assert_read_error(
            SimpleUploadedFile("cohort.xlsx", b"PK\x03\x04\xff\xfe\x00"),
            "not UTF-8 text",
        )

    def test_rejects_unclosed_quotation_mark(self):
        self.assert_read_error(
            upload('first_name,ethnicity\nAda,"1: Asian\n'), "not valid CSV"
        )

    def test_rejects_text_after_closing_quotation_mark(self):
        self.assert_read_error(
            upload('first_name,ethnicity\nAda,"1: Asian"x\n'), "Line 2"
        )

    def test_rejects_file_over_size_limit(self):
        self.assert_read_error(
            upload("first_name\n" + "Ada\n" * 10), "larger than the limit", max_bytes=20
        )

    def test_accepts_file_exactly_at_size_limit(self):
        text = "first_name\nAda\n"
        table = read_csv(upload(text), max_bytes=len(text))
        self.assertEqual(table.rows, (CsvRow(2, ("Ada",)),))
