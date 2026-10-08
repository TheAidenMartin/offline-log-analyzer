import os
from typing import Iterable, Iterator, List
from itertools import islice

def load_logs_lazily(file_path: str) -> Iterator[str]:
    """Yields clean, non-empty lines from a log file one by one."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            if clean_line:
                yield clean_line

def chunk_iterable(iterable: Iterable[str], chunk_size: int = 5) -> Iterator[List[str]]:
    """Lazily chunks any iterable stream into discrete lists."""
    iterator = iter(iterable)
    while True:
        # islice grabs exactly 'chunk_size' items without loading the rest
        chunk = list(islice(iterator, chunk_size))
        if not chunk:
            break
        yield chunk