from __future__ import annotations

import hashlib
import json
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

    log_dir: str = config.OUTPUT_DIR
    log_name: str = "audit_log.txt"
    summary_name: str = "audit_summary.json"
    _records: list = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, self.log_name)
        self.summary_path = os.path.join(self.log_dir, self.summary_name)


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

        line = f"[{timestamp}] [{level.upper()}] {message}"
        if context:
            line += f" | {context}"
        print(line)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

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


    def save_summary(self) -> str:
        with open(self.summary_path, "w", encoding="utf-8") as f:
            json.dump(self._records, f, indent=2)
        return self.summary_path
