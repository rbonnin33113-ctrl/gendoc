"""Generateur de fiches techniques Delagrave."""
from importlib.metadata import version as _get_version
try:
    __version__ = _get_version('gendoc-delagrave')
except Exception:
    __version__ = "0.0.0"
