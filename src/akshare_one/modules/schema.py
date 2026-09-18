"""Schema seam.

Every provider of a domain returns a frame projected onto that domain's
declared columns, so a column the promise includes is present whether or not
the source supplied it — absent values come back as ``NaN`` — and the order is
the declared one. Each domain's contract lives in ``modules/<domain>/schema.py``;
this module owns the projection so all domains normalize identically.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def normalize(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Project ``df`` onto ``columns``.

    Args:
        df: A frame from any source of the domain.
        columns: The domain's declared columns, in output order.

    Returns:
        A frame with exactly ``columns``, missing values filled with ``NaN``.
    """
    return df.reindex(columns=list(columns))
