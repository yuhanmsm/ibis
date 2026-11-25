"""Reading an uploaded CSV file into rows of text.

This module only turns the bytes of an uploaded file into a header and rows of
cells. It does not decide whether those cells make sense: checking columns and
values is the job of the importer that uses it.
"""

import csv
import io
from dataclasses import dataclass

DEFAULT_MAX_BYTES = 2 * 1024 * 1024
"""The largest file accepted by default (2 MB, far more than a cohort of 300)."""


class CsvReadError(Exception):
    """Raised when an uploaded file cannot be read as a CSV file at all.

    The message is written for staff users, so it can be shown as it is.
    """


@dataclass(frozen=True)
class CsvRow:
    """One row of a CSV file, before any validation

    :param line_number: The line of the file on which the row ends, counting
    the header as line 1, so that error messages can point staff to it
    :param cells: The values of the row, with surrounding spaces removed. This
    may hold more or fewer values than the header has columns.
    """

    line_number: int
    cells: tuple[str, ...]


@dataclass(frozen=True)
class CsvTable:
    """The contents of a CSV file, before any validation

    :param header: The column names in the first row, with surrounding spaces
    removed
    :param rows: The rows after the header, leaving out blank lines
    """

    header: tuple[str, ...]
    rows: tuple[CsvRow, ...]


def read_csv(uploaded_file, max_bytes: int = DEFAULT_MAX_BYTES) -> CsvTable:
    """Read an uploaded CSV file into a header and rows of text

    The file must be UTF-8 text, as saved by Excel's "CSV UTF-8" option or any
    text editor. A byte order mark at its start is ignored. Values may be
    quoted, so a value such as "1: Asian, or Asian British" can contain commas.

    :param uploaded_file: The uploaded file, or any object whose read() returns
    bytes, such as a Django UploadedFile
    :param max_bytes: The largest file size accepted, in bytes
    :returns: The header and rows of the file
    :raises CsvReadError: If the file is too large, empty, not UTF-8 text or
    not well-formed CSV
    """
    text = _decode(_read_bytes(uploaded_file, max_bytes))
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)

    try:
        rows = [
            CsvRow(reader.line_num, tuple(cell.strip() for cell in cells))
            for cells in reader
            if not _is_blank(cells)
        ]
    except csv.Error as error:
        raise CsvReadError(
            f"Line {reader.line_num} of the file is not valid CSV ({error}). "
            "Check for a missing or misplaced quotation mark."
        ) from error

    if not rows:
        raise CsvReadError("The file is empty.")

    header, *data_rows = rows
    return CsvTable(header.cells, tuple(data_rows))


def _read_bytes(uploaded_file, max_bytes: int) -> bytes:
    content = uploaded_file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise CsvReadError(
            f"The file is larger than the limit of {max_bytes // 1024} KB."
        )
    return content


def _decode(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise CsvReadError(
            "The file is not UTF-8 text. In Excel, save it with "
            '"CSV UTF-8 (Comma delimited)".'
        ) from error


def _is_blank(cells: list[str]) -> bool:
    return all(not cell.strip() for cell in cells)
