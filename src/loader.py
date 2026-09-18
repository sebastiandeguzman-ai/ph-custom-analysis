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
