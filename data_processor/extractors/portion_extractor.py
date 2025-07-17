"""
Portion Size Extractor.
Extracts and processes portion information from recipe content.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PortionType(Enum):
    """Enum for portion types."""
    WEIGHT = "weight"
    VOLUME = "volume"
    UNIT = "unit"
    SERVING = "serving"
    DESCRIPTIVE = "descriptive"


@dataclass
class Portion:
    """Represents a portion with all its properties."""
    amount: Optional[float]
    unit: Optional[str]
    portion_type: PortionType
    description: str
    grams_equivalent: Optional[float]
    calories_per_portion: Optional[float]
    original_text: str
    confidence: float


class PortionExtractor:
    """
    Extracts portion information from recipe text and data.
    """
    
    def __init__(self):
        self.portion_patterns = self._build_portion_patterns()
        self.unit_conversions = self._build_unit_conversions()
        self.descriptive_portions = self._build_descriptive_portions()
        
    def _build_portion_patterns(self) -> Dict[str, List[str]]:
        """Build portion extraction patterns by type."""
        return {
            'weight': [
                r'(\d+(?:\.\d+)?)\s*(g|gr|gramos?|kg|kilogramos?)',
                r'(\d+(?:\.\d+)?)\s*(onza|onzas|oz|libra|libras|lb)'
            ],
            'volume': [
                r'(\d+(?:\.\d+)?)\s*(ml|cc|mililitros?|l|lt|litros?)',
                r'(\d+(?:\.\d+)?)\s*(taza|tazas|cup|cups)',
                r'(\d+(?:\.\d+)?)\s*(cucharada|cucharadas|cda|cdas|tbsp)',
                r'(\d+(?:\.\d+)?)\s*(cucharadita|cucharaditas|cdita|cditas|tsp)',
                r'(\d+(?:\.\d+)?)\s*(vaso|vasos|copa|copas)'
            ],
            'unit': [
                r'(\d+(?:\.\d+)?)\s*(unidad|unidades|u|ud|pieza|piezas)',
                r'(\d+(?:\.\d+)?)\s*(rodaja|rodajas|slice|slices)',
                r'(\d+(?:\.\d+)?)\s*(diente|dientes|clove|cloves)',
                r'(\d+(?:\.\d+)?)\s*(hoja|hojas|leaf|leaves)',
                r'(\d+(?:\.\d+)?)\s*(rama|ramas|sprig|sprigs)'
            ],
            'serving': [
                r'(\d+(?:\.\d+)?)\s*(porción|porciones|serving|servings)',
                r'(\d+(?:\.\d+)?)\s*(ración|raciones|portion|portions)',
                r'(\d+(?:\.\d+)?)\s*(persona|personas|people)',
                r'rinde\s+(\d+(?:\.\d+)?)',
                r'para\s+(\d+(?:\.\d+)?)\s*personas?'
            ],
            'descriptive': [
                r'una?\s+pizca\s+de',
                r'al\s+gusto',
                r'a\s+gusto',
                r'un\s+poco\s+de',
                r'media\s+([a-zA-Z]+)',
                r'medio\s+([a-zA-Z]+)',
                r'un\s+puñado\s+de',
                r'cantidad\s+necesaria',
                r'c\.n\.',
                r'q\.s\.',
                r'cantidad\s+suficiente'
            ]
        }
    
    def _build_unit_conversions(self) -> Dict[str, float]:
        """Build unit conversion factors to grams."""
        return {
            # Weight units
            'g': 1.0,
            'gr': 1.0,
            'gramos': 1.0,
            'kg': 1000.0,
            'kilogramos': 1000.0,
            'oz': 28.35,
            'onza': 28.35,
            'onzas': 28.35,
            'lb': 453.59,
            'libra': 453.59,
            'libras': 453.59,
            
            # Volume units (approximations)
            'ml': 1.0,
            'cc': 1.0,
            'mililitros': 1.0,
            'l': 1000.0,
            'lt': 1000.0,
            'litros': 1000.0,
            'taza': 240.0,
            'tazas': 240.0,
            'cup': 240.0,
            'cups': 240.0,
            'cucharada': 15.0,
            'cucharadas': 15.0,
            'cda': 15.0,
            'cdas': 15.0,
            'tbsp': 15.0,
            'cucharadita': 5.0,
            'cucharaditas': 5.0,
            'cdita': 5.0,
            'cditas': 5.0,
            'tsp': 5.0,
            'vaso': 200.0,
            'vasos': 200.0,
            'copa': 150.0,
            'copas': 150.0,
            
            # Common unit weights
            'unidad': 100.0,
            'unidades': 100.0,
            'u': 100.0,
            'ud': 100.0,
            'pieza': 100.0,
            'piezas': 100.0,
            'rodaja': 20.0,
            'rodajas': 20.0,
            'slice': 20.0,
            'slices': 20.0,
            'diente': 3.0,
            'dientes': 3.0,
            'clove': 3.0,
            'cloves': 3.0,
            'hoja': 0.5,
            'hojas': 0.5,
            'leaf': 0.5,
            'leaves': 0.5,
            'rama': 2.0,
            'ramas': 2.0,
            'sprig': 2.0,
            'sprigs': 2.0
        }
    
    def _build_descriptive_portions(self) -> Dict[str, float]:
        """Build descriptive portion equivalents in grams."""
        return {
            'una pizca': 0.5,
            'un poco': 5.0,
            'puñado': 30.0,
            'al gusto': 2.0,
            'a gusto': 2.0,
            'cantidad necesaria': 10.0,
            'cantidad suficiente': 10.0,
            'media': 0.5,
            'medio': 0.5
        }
    
    def extract_from_text(self, text: str) -> List[Portion]:
        """Extract portions from text."""
        if not text:
            return []
        
        portions = []
        text_lower = text.lower()
        
        # Extract different types of portions
        for portion_type, patterns in self.portion_patterns.items():
            type_portions = self._extract_portions_by_type(text_lower, patterns, portion_type)
            portions.extend(type_portions)
        
        return portions
    
    def _extract_portions_by_type(self, text: str, patterns: List[str], portion_type: str) -> List[Portion]:
        """Extract portions of specific type."""
        portions = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                portion = self._create_portion_from_match(match, portion_type)
                if portion:
                    portions.append(portion)
        
        return portions
    
    def _create_portion_from_match(self, match: re.Match, portion_type: str) -> Optional[Portion]:
        """Create portion object from regex match."""
        try:
            matched_text = match.group(0)
            
            if portion_type == 'descriptive':
                return self._create_descriptive_portion(matched_text)
            
            # Extract amount and unit
            amount_str = match.group(1) if match.groups() else None
            unit = match.group(2) if len(match.groups()) > 1 else None
            
            if amount_str:
                amount = float(amount_str)
            else:
                amount = None
            
            # Calculate grams equivalent
            grams_equivalent = self._calculate_grams_equivalent(amount, unit)
            
            # Determine confidence
            confidence = self._calculate_confidence(matched_text, amount, unit)
            
            return Portion(
                amount=amount,
                unit=unit,
                portion_type=PortionType(portion_type),
                description=matched_text,
                grams_equivalent=grams_equivalent,
                calories_per_portion=None,
                original_text=matched_text,
                confidence=confidence
            )
            
        except (ValueError, IndexError) as e:
            logger.warning(f"Error creating portion from match: {e}")
            return None
    
    def _create_descriptive_portion(self, text: str) -> Portion:
        """Create portion for descriptive amounts."""
        grams_equivalent = None
        
        # Check for known descriptive portions
        for desc, grams in self.descriptive_portions.items():
            if desc in text.lower():
                grams_equivalent = grams
                break
        
        return Portion(
            amount=None,
            unit=None,
            portion_type=PortionType.DESCRIPTIVE,
            description=text,
            grams_equivalent=grams_equivalent,
            calories_per_portion=None,
            original_text=text,
            confidence=0.6
        )
    
    def _calculate_grams_equivalent(self, amount: Optional[float], unit: Optional[str]) -> Optional[float]:
        """Calculate grams equivalent for portion."""
        if not amount or not unit:
            return None
        
        unit_lower = unit.lower()
        conversion_factor = self.unit_conversions.get(unit_lower)
        
        if conversion_factor:
            return amount * conversion_factor
        
        return None
    
    def _calculate_confidence(self, text: str, amount: Optional[float], unit: Optional[str]) -> float:
        """Calculate confidence score for portion extraction."""
        confidence = 0.5
        
        # Higher confidence for numeric amounts
        if amount is not None:
            confidence += 0.2
        
        # Higher confidence for recognized units
        if unit and unit.lower() in self.unit_conversions:
            confidence += 0.3
        
        # Higher confidence for complete expressions
        if amount and unit:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def extract_servings(self, text: str) -> Optional[int]:
        """Extract number of servings from text."""
        serving_patterns = [
            r'(\d+)\s*porcion',
            r'(\d+)\s*serving',
            r'(\d+)\s*personas?',
            r'(\d+)\s*people',
            r'rinde\s+(\d+)',
            r'para\s+(\d+)',
            r'serves\s+(\d+)'
        ]
        
        text_lower = text.lower()
        
        for pattern in serving_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def normalize_portion(self, portion: Portion, target_unit: str = 'g') -> Optional[Portion]:
        """Normalize portion to target unit."""
        if not portion.grams_equivalent:
            return portion
        
        if target_unit == 'g':
            return Portion(
                amount=portion.grams_equivalent,
                unit='g',
                portion_type=PortionType.WEIGHT,
                description=f"{portion.grams_equivalent}g",
                grams_equivalent=portion.grams_equivalent,
                calories_per_portion=portion.calories_per_portion,
                original_text=portion.original_text,
                confidence=portion.confidence
            )
        
        # Add more target units as needed
        return portion
    
    def convert_to_servings(self, portions: List[Portion], servings: int) -> List[Portion]:
        """Convert portions to per-serving amounts."""
        if not servings or servings <= 0:
            return portions
        
        converted = []
        for portion in portions:
            converted_portion = Portion(
                amount=portion.amount / servings if portion.amount else None,
                unit=portion.unit,
                portion_type=portion.portion_type,
                description=f"{portion.description} (per serving)",
                grams_equivalent=portion.grams_equivalent / servings if portion.grams_equivalent else None,
                calories_per_portion=portion.calories_per_portion / servings if portion.calories_per_portion else None,
                original_text=portion.original_text,
                confidence=portion.confidence
            )
            converted.append(converted_portion)
        
        return converted
    
    def standardize_portions(self, portions: List[Portion]) -> List[Dict[str, Any]]:
        """Standardize portions to common format."""
        standardized = []
        
        for portion in portions:
            standardized_portion = {
                'amount': portion.amount,
                'unit': portion.unit,
                'portion_type': portion.portion_type.value,
                'description': portion.description,
                'grams_equivalent': portion.grams_equivalent,
                'calories_per_portion': portion.calories_per_portion,
                'confidence': portion.confidence,
                'original_text': portion.original_text
            }
            standardized.append(standardized_portion)
        
        return standardized
    
    def validate_portions(self, portions: List[Portion]) -> Dict[str, Any]:
        """Validate portion data."""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        if not portions:
            validation_results['warnings'].append("No portions found")
            return validation_results
        
        # Check for portions without equivalents
        no_equivalent = [p for p in portions if not p.grams_equivalent]
        if no_equivalent:
            validation_results['warnings'].append(f"{len(no_equivalent)} portions without gram equivalents")
        
        # Check for very large portions
        large_portions = [p for p in portions if p.grams_equivalent and p.grams_equivalent > 1000]
        if large_portions:
            validation_results['warnings'].append(f"{len(large_portions)} portions larger than 1kg")
        
        # Check for very small portions
        small_portions = [p for p in portions if p.grams_equivalent and p.grams_equivalent < 1]
        if small_portions:
            validation_results['warnings'].append(f"{len(small_portions)} portions smaller than 1g")
        
        return validation_results
    
    def export_to_dict(self, portions: List[Portion]) -> List[Dict[str, Any]]:
        """Export portions to dictionary format."""
        return [
            {
                'amount': p.amount,
                'unit': p.unit,
                'portion_type': p.portion_type.value,
                'description': p.description,
                'grams_equivalent': p.grams_equivalent,
                'calories_per_portion': p.calories_per_portion,
                'confidence': p.confidence,
                'original_text': p.original_text
            }
            for p in portions
        ]