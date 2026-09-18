
from __future__ import annotations

import os
import pandas as pd

try:
    from . import config
except ImportError:
    import config

CATEGORY_1 = getattr(config, "CATEGORY_1", "category")
CATEGORY_2 = getattr(config, "CATEGORY_2", "subcategory")
MEASURE = getattr(config, "NUM_MEASURE", "value")
#to fix: catgery name s 

def _safe_load_csv() -> pd.DataFrame:

    try:
        from . import loader
    except ImportError:
        import loader
    return loader.load_csv()