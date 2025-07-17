"""
DOCX Parsers Module.
Contains parsers for different types of DOCX files.
"""

from .base_parser import BaseDocxParser
from .almuerzos_cenas_parser import AlmuerzosECenasParser
from .desayunos_meriendas_parser import DesayunosYMeriendasParser
from .equivalencias_parser import EquivalenciasParser
from .recetas_detalladas_parser import RecetasDetalladasParser

__all__ = [
    'BaseDocxParser',
    'AlmuerzosECenasParser',
    'DesayunosYMeriendasParser',
    'EquivalenciasParser',
    'RecetasDetalladasParser'
]