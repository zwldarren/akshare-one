"""The news domain's column contract."""

from __future__ import annotations

#: keyword, title, content, publish_time, source, url
#: ``source`` is where the item came from: the outlet that published it, or
#: the collection it was read out of when the source states no outlet.
COLUMNS = (
    "keyword",
    "title",
    "content",
    "publish_time",
    "source",
    "url",
)
