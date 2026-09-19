from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import pandas as pd

try:
    from . import config
except ImportError:
    import config


class LoaderError(Exception):
    """Base class for all loader-related failures."""


class FileNotFoundInProjectError(LoaderError):
    """Raised when the expected data file is missing on disk."""


class ChecksumMismatchError(LoaderError):
    """Raised when the SHA-256 of the file does not match the expected value."""


class SchemaValidationError(LoaderError):
    """Raised when required columns are missing from the loaded data."""


class RowCountMismatchError(LoaderError):
    """Raised when the number of raw rows differs from the expected count."""


class SumValidationError(LoaderError):
    """Raised when the sum of the numeric measure column drifts from the
    expected reference value beyond the allowed tolerance."""


class DataQualityError(LoaderError):
    """Raised for edge-case data quality problems (nulls, dupes, negatives)."""


@dataclass
class AuditLogger:
    """In-memory logger that prints checks to the terminal without creating .txt or .json files."""

    _records: list = field(default_factory=list, init=False, repr=False)

    def _write(self, level: str, message: str, **context) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "message": message,
        }
        if context:
            entry["context"] = context

        self._records.append(entry)

        # Print log directly to terminal console
        line = f"[{timestamp}] [{level.upper()}] {message}"
        if context:
            line += f" | {context}"
        print(line)

    def info(self, message: str, **context) -> None:
        self._write("info", message, **context)

    def warning(self, message: str, **context) -> None:
        self._write("warning", message, **context)

    def error(self, message: str, **context) -> None:
        self._write("error", message, **context)

    def critical(self, message: str, **context) -> None:
        self._write("critical", message, **context)

    def check(self, description: str, passed: bool, **context) -> None:
        level = "info" if passed else "error"
        status = "PASSED" if passed else "FAILED"
        self._write(level, f"CHECK {status}: {description}", **context)

    def save_summary(self) -> None:
        """No-op: Prevents generating audit_summary.json or audit_log.txt on disk."""
        pass

    @property
    def records(self) -> list:
        return list(self._records)

    @property
    def has_errors(self) -> bool:
        return any(r["level"] in ("ERROR", "CRITICAL") for r in self._records)


def compute_sha256(path: str, chunk_size: int = 8192) -> str:
    """Stream the file in chunks and return its hex-digest SHA-256 hash."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_checksum(
    path: str,
    expected_hash: str,
    logger: Optional[AuditLogger] = None,
) -> str:
    actual_hash = compute_sha256(path)
    passed = actual_hash.lower() == expected_hash.lower()

    if logger:
        logger.check(
            "SHA-256 checksum matches expected reference value",
            passed,
            expected=expected_hash,
            actual=actual_hash,
        )

    if not passed:
        raise ChecksumMismatchError(
            f"Checksum mismatch for '{path}': expected {expected_hash}, "
            f"got {actual_hash}"
        )
    return actual_hash


def _check_file_exists(path: str, logger: AuditLogger) -> None:
    exists = os.path.isfile(path)
    logger.check(f"Data file exists at '{path}'", exists)
    if not exists:
        raise FileNotFoundInProjectError(
            f"Expected data file not found: {path}"
        )


def _check_schema(
    df: pd.DataFrame, required_columns: set, logger: AuditLogger
) -> None:
    missing = required_columns - set(df.columns)
    logger.check(
        "Required columns present",
        len(missing) == 0,
        required=sorted(required_columns),
        missing=sorted(missing),
    )
    if missing:
        raise SchemaValidationError(
            f"Missing required columns: {sorted(missing)}"
        )


def _check_row_count(
    df: pd.DataFrame, expected_rows: int, logger: AuditLogger
) -> None:
    actual_rows = len(df)
    passed = actual_rows == expected_rows
    logger.check(
        "Row count matches expected reference value",
        passed,
        expected=expected_rows,
        actual=actual_rows,
    )
    if not passed:
        raise RowCountMismatchError(
            f"Row count mismatch: expected {expected_rows}, got {actual_rows}"
        )


def _check_numeric_sum(
    df: pd.DataFrame,
    column: str,
    expected_sum: float,
    logger: AuditLogger,
    rel_tolerance: float = 1e-6,
) -> None:
    actual_sum = float(pd.to_numeric(df[column], errors="coerce").sum())
    diff = abs(actual_sum - expected_sum)
    tolerance = abs(expected_sum) * rel_tolerance
    passed = diff <= tolerance
    logger.check(
        f"Sum of '{column}' matches expected reference value",
        passed,
        expected=expected_sum,
        actual=actual_sum,
        diff=diff,
        tolerance=tolerance,
    )
    if not passed:
        raise SumValidationError(
            f"Sum mismatch for '{column}': expected {expected_sum}, "
            f"got {actual_sum} (diff={diff}, tolerance={tolerance})"
        )


def _check_nulls(df: pd.DataFrame, columns: set, logger: AuditLogger) -> None:
    null_counts = {col: int(df[col].isna().sum()) for col in columns}
    total_nulls = sum(null_counts.values())
    logger.check(
        "No nulls in required columns",
        total_nulls == 0,
        null_counts=null_counts,
    )


def _check_duplicates(df: pd.DataFrame, logger: AuditLogger) -> int:
    dupe_count = int(df.duplicated().sum())
    logger.check(
        "No fully duplicated rows",
        dupe_count == 0,
        duplicate_rows=dupe_count,
    )
    return dupe_count


def _check_negative_values(
    df: pd.DataFrame, column: str, logger: AuditLogger
) -> int:
    numeric = pd.to_numeric(df[column], errors="coerce")
    negative_count = int((numeric < 0).sum())
    logger.check(
        f"No negative values in '{column}'",
        negative_count == 0,
        negative_count=negative_count,
    )
    return negative_count


def _check_empty_dataframe(df: pd.DataFrame, logger: AuditLogger) -> None:
    is_empty = df.empty
    logger.check("DataFrame is not empty", not is_empty)
    if is_empty:
        raise DataQualityError("Loaded DataFrame is empty.")


def load_csv(
    path: str = config.DATA_PATH,
    expected_hash: str = config.EXPECTED_SHA256,
    expected_rows: int = config.EXPECTED_RAW_ROWS,
    expected_sum: float = config.EXPECTED_RAW_SUM,
    required_columns: set = config.REQUIRED_COLUMNS,
    numeric_column: str = config.NUM_MEASURE,
    logger: Optional[AuditLogger] = None,
    strict: bool = True,
) -> pd.DataFrame:
    logger = logger or AuditLogger()
    logger.info("Starting dataset load", path=path)

    try:
        _check_file_exists(path, logger)
        verify_checksum(path, expected_hash, logger)

        logger.info("Reading CSV into memory")
        try:
            df = pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(
                path, encoding="latin1"
            )  # Fallback for Windows/ISO-8859 encoded files

        _check_empty_dataframe(df, logger)
        _check_schema(df, required_columns, logger)
        _check_row_count(df, expected_rows, logger)
        _check_numeric_sum(df, numeric_column, expected_sum, logger)

        _check_nulls(df, required_columns, logger)
        _check_duplicates(df, logger)
        _check_negative_values(df, numeric_column, logger)

        logger.info(
            "Dataset load completed successfully",
            rows=len(df),
            columns=len(df.columns),
        )
        return df

    except LoaderError as exc:
        logger.critical(f"Load aborted: {exc}")
        if strict:
            raise
        return pd.DataFrame()
    finally:
        logger.save_summary()


if __name__ == "__main__":
    audit_logger = AuditLogger()
    dataframe = load_csv(logger=audit_logger)
    print(dataframe.head())
