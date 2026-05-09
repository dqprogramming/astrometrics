"""astrometrics package."""

import re
from pathlib import Path

_version_path = Path(__file__).resolve().parent.parent / "__version__.py"
_match = re.search(
    r'__version__\s*=\s*["\']([^"\']+)["\']',
    _version_path.read_text(encoding="utf-8"),
)
__version__: str = _match.group(1) if _match else "0.0.0"
