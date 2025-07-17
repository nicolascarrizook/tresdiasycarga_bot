"""
Nutritional Information Extractor.
Extracts and processes nutritional data from recipe content.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class NutrientType(Enum):
    """Enum for different nutrient types."""
    CALORIES = "calories"
    PROTEIN = "protein"
    CARBS = "carbs"
    FAT = "fat"
    FIBER = "fiber"
    SUGAR = "sugar"
    SODIUM = "sodium"
    CALCIUM = "calcium"
    IRON = "iron"
    VITAMIN_C = "vitamin_c"
    VITAMIN_A = "vitamin_a"


@dataclass
class NutritionalValue:
    """Represents a nutritional value with unit and confidence."""
    value: float
    unit: str
    confidence: float
    source: str
    per_unit: Optional[str] = None


class NutritionalExtractor:
    """
    Extracts nutritional information from recipe text and data.
    Handles various formats and provides standardized nutritional data.
    """
    
    def __init__(self):
        self.nutrient_patterns = self._build_nutrient_patterns()
        self.unit_conversions = self._build_unit_conversions()
        self.default_values = self._build_default_values()
        
    def _build_nutrient_patterns(self) -> Dict[NutrientType, List[str]]:
        """Build regex patterns for different nutrients."""
        return {
            NutrientType.CALORIES: [
                r'(\d+(?:\.\d+)?)\s*(?:kcal|cal|calorías|calorias|kilocalorías|kilocaloria)',
                r'(\d+(?:\.\d+)?)\s*(?:energía|energia|energy)',
                r'valor\s*energético\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.PROTEIN: [
                r'(\d+(?:\.\d+)?)\s*g?\s*(?:proteína|proteinas|protein|prot)',
                r'proteína\s*[:\s]*(\d+(?:\.\d+)?)',
                r'protein\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.CARBS: [
                r'(\d+(?:\.\d+)?)\s*g?\s*(?:carbohidratos|carbs|hidratos|carbohidrato)',
                r'carbohidratos\s*[:\s]*(\d+(?:\.\d+)?)',
                r'carbs\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.FAT: [
                r'(\d+(?:\.\d+)?)\s*g?\s*(?:grasa|grasas|fat|lípidos|lipidos)',
                r'grasa\s*[:\s]*(\d+(?:\.\d+)?)',
                r'fat\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.FIBER: [
                r'(\d+(?:\.\d+)?)\s*g?\s*(?:fibra|fiber|fibra\s*dietética|fibra\s*dietetica)',
                r'fibra\s*[:\s]*(\d+(?:\.\d+)?)',
                r'fiber\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.SUGAR: [
                r'(\d+(?:\.\d+)?)\s*g?\s*(?:azúcar|azucar|sugar|azúcares|azucares)',
                r'azúcar\s*[:\s]*(\d+(?:\.\d+)?)',
                r'sugar\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.SODIUM: [
                r'(\d+(?:\.\d+)?)\s*(?:mg|g)?\s*(?:sodio|sodium|sal)',
                r'sodio\s*[:\s]*(\d+(?:\.\d+)?)',
                r'sodium\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.CALCIUM: [
                r'(\d+(?:\.\d+)?)\s*(?:mg|g)?\s*(?:calcio|calcium)',
                r'calcio\s*[:\s]*(\d+(?:\.\d+)?)',
                r'calcium\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.IRON: [
                r'(\d+(?:\.\d+)?)\s*(?:mg|g)?\s*(?:hierro|iron)',
                r'hierro\s*[:\s]*(\d+(?:\.\d+)?)',
                r'iron\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.VITAMIN_C: [
                r'(\d+(?:\.\d+)?)\s*(?:mg|g)?\s*(?:vitamina\s*c|vitamin\s*c|ácido\s*ascórbico)',
                r'vitamina\s*c\s*[:\s]*(\d+(?:\.\d+)?)',
                r'vitamin\s*c\s*[:\s]*(\d+(?:\.\d+)?)'
            ],
            NutrientType.VITAMIN_A: [
                r'(\d+(?:\.\d+)?)\s*(?:mg|g|ui)?\s*(?:vitamina\s*a|vitamin\s*a|retinol)',
                r'vitamina\s*a\s*[:\s]*(\d+(?:\.\d+)?)',
                r'vitamin\s*a\s*[:\s]*(\d+(?:\.\d+)?)'
            ]
        }
    
    def _build_unit_conversions(self) -> Dict[str, Dict[str, float]]:
        """Build unit conversion factors."""
        return {
            'weight': {
                'g': 1.0,
                'kg': 1000.0,
                'mg': 0.001,
                'oz': 28.35,
                'lb': 453.59
            },
            'volume': {
                'ml': 1.0,
                'l': 1000.0,
                'cup': 240.0,
                'tbsp': 15.0,
                'tsp': 5.0,
                'fl_oz': 29.57
            },
            'energy': {
                'kcal': 1.0,
                'cal': 0.001,
                'kj': 0.239
            }
        }
    
    def _build_default_values(self) -> Dict[str, Dict[str, float]]:
        """Build default nutritional values per 100g for common foods."""
        return {
            'pollo_pechuga': {
                'calories': 165,
                'protein': 31,
                'carbs': 0,
                'fat': 3.6,
                'fiber': 0
            },
            'carne_vacuna': {
                'calories': 250,
                'protein': 26,
                'carbs': 0,
                'fat': 15,
                'fiber': 0
            },
            'pescado_blanco': {
                'calories': 82,
                'protein': 18,
                'carbs': 0,
                'fat': 1.2,
                'fiber': 0
            },
            'arroz_blanco': {
                'calories': 130,
                'protein': 2.7,
                'carbs': 28,
                'fat': 0.3,
                'fiber': 0.4
            },
            'pasta': {
                'calories': 131,
                'protein': 5,
                'carbs': 25,
                'fat': 1.1,
                'fiber': 1.8
            },
            'papa': {
                'calories': 77,
                'protein': 2,
                'carbs': 17,
                'fat': 0.1,
                'fiber': 2.2
            },
            'verduras_verdes': {
                'calories': 23,
                'protein': 2.9,
                'carbs': 4.6,
                'fat': 0.4,
                'fiber': 2.6
            },
            'aceite_oliva': {
                'calories': 884,
                'protein': 0,
                'carbs': 0,
                'fat': 100,
                'fiber': 0
            }
        }
    
    def extract_from_text(self, text: str) -> Dict[str, NutritionalValue]:
        """Extract nutritional information from text."""
        nutritional_data = {}
        
        if not text:
            return nutritional_data
        
        text_lower = text.lower()
        
        # Extract each nutrient type
        for nutrient_type, patterns in self.nutrient_patterns.items():
            value = self._extract_nutrient_value(text_lower, patterns, nutrient_type)
            if value:
                nutritional_data[nutrient_type.value] = value
        
        return nutritional_data
    
    def _extract_nutrient_value(self, text: str, patterns: List[str], 
                               nutrient_type: NutrientType) -> Optional[NutritionalValue]:
        """Extract a specific nutrient value from text."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    unit = self._determine_unit(pattern, nutrient_type)
                    confidence = self._calculate_confidence(match, pattern)
                    
                    return NutritionalValue(
                        value=value,
                        unit=unit,
                        confidence=confidence,
                        source='text_extraction',
                        per_unit='100g'
                    )
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _determine_unit(self, pattern: str, nutrient_type: NutrientType) -> str:
        """Determine the unit for a nutrient based on pattern and type."""
        if nutrient_type == NutrientType.CALORIES:
            return 'kcal'
        elif nutrient_type in [NutrientType.PROTEIN, NutrientType.CARBS, NutrientType.FAT, NutrientType.FIBER, NutrientType.SUGAR]:
            return 'g'
        elif nutrient_type in [NutrientType.SODIUM, NutrientType.CALCIUM, NutrientType.IRON, NutrientType.VITAMIN_C]:
            return 'mg'
        elif nutrient_type == NutrientType.VITAMIN_A:
            return 'ui'
        else:
            return 'unknown'
    
    def _calculate_confidence(self, match: re.Match, pattern: str) -> float:
        """Calculate confidence score for the extracted value."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for more specific patterns
        if 'proteína' in pattern or 'protein' in pattern:
            confidence += 0.3
        if 'calorías' in pattern or 'calories' in pattern:
            confidence += 0.3
        if r'\d+(?:\.\d+)?' in pattern:
            confidence += 0.2
        
        # Context-based confidence
        matched_text = match.group(0)
        if 'por' in matched_text or 'per' in matched_text:
            confidence += 0.2
        if '100g' in matched_text:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def extract_from_ingredients(self, ingredients: List[Dict[str, Any]]) -> Dict[str, NutritionalValue]:
        """Extract nutritional information from ingredient list."""
        total_nutrition = {}
        
        for ingredient in ingredients:
            ingredient_nutrition = self._get_ingredient_nutrition(ingredient)
            
            # Add to total nutrition
            for nutrient, value in ingredient_nutrition.items():
                if nutrient not in total_nutrition:
                    total_nutrition[nutrient] = NutritionalValue(
                        value=0,
                        unit=value.unit,
                        confidence=0,
                        source='ingredient_calculation'
                    )
                
                total_nutrition[nutrient].value += value.value
                total_nutrition[nutrient].confidence = max(
                    total_nutrition[nutrient].confidence, 
                    value.confidence
                )
        
        return total_nutrition
    
    def _get_ingredient_nutrition(self, ingredient: Dict[str, Any]) -> Dict[str, NutritionalValue]:
        """Get nutritional information for a single ingredient."""
        ingredient_name = ingredient.get('name', '').lower()
        quantity = ingredient.get('quantity', 0)
        unit = ingredient.get('unit', '')
        
        # Get base nutritional values
        base_values = self._get_base_nutritional_values(ingredient_name)
        
        if not base_values:
            return {}
        
        # Convert quantity to grams
        quantity_grams = self._convert_to_grams(quantity, unit, ingredient_name)
        
        if quantity_grams is None:
            return {}
        
        # Calculate nutritional values for the given quantity
        nutrition = {}
        for nutrient, value_per_100g in base_values.items():
            actual_value = (value_per_100g * quantity_grams) / 100
            
            nutrition[nutrient] = NutritionalValue(
                value=actual_value,
                unit=self._get_nutrient_unit(nutrient),
                confidence=0.7,
                source='ingredient_database',
                per_unit=f"{quantity_grams}g"
            )
        
        return nutrition
    
    def _get_base_nutritional_values(self, ingredient_name: str) -> Optional[Dict[str, float]]:
        """Get base nutritional values for an ingredient."""
        # Try exact match first
        if ingredient_name in self.default_values:
            return self.default_values[ingredient_name]
        
        # Try partial matches
        for key, values in self.default_values.items():
            if any(word in ingredient_name for word in key.split('_')):
                return values
        
        # Category-based matching
        if any(word in ingredient_name for word in ['pollo', 'chicken']):
            return self.default_values['pollo_pechuga']
        elif any(word in ingredient_name for word in ['carne', 'beef', 'res']):
            return self.default_values['carne_vacuna']
        elif any(word in ingredient_name for word in ['pescado', 'fish']):
            return self.default_values['pescado_blanco']
        elif any(word in ingredient_name for word in ['arroz', 'rice']):
            return self.default_values['arroz_blanco']
        elif any(word in ingredient_name for word in ['pasta', 'fideos']):
            return self.default_values['pasta']
        elif any(word in ingredient_name for word in ['papa', 'patata', 'potato']):
            return self.default_values['papa']
        elif any(word in ingredient_name for word in ['verdura', 'vegetal', 'vegetable']):
            return self.default_values['verduras_verdes']
        elif any(word in ingredient_name for word in ['aceite', 'oil']):
            return self.default_values['aceite_oliva']
        
        return None
    
    def _convert_to_grams(self, quantity: float, unit: str, ingredient_name: str) -> Optional[float]:
        """Convert quantity to grams."""
        if not quantity:
            return None
        
        unit_lower = unit.lower()
        
        # Direct weight units
        if unit_lower in self.unit_conversions['weight']:
            return quantity * self.unit_conversions['weight'][unit_lower]
        
        # Volume units - need density conversion
        if unit_lower in self.unit_conversions['volume']:
            volume_ml = quantity * self.unit_conversions['volume'][unit_lower]
            density = self._get_ingredient_density(ingredient_name)
            return volume_ml * density
        
        # Unit conversions (pieces, etc.)
        if unit_lower in ['unidad', 'unidades', 'u', 'pieza', 'piezas']:
            return self._get_unit_weight(ingredient_name) * quantity
        
        # Default: assume grams
        return quantity
    
    def _get_ingredient_density(self, ingredient_name: str) -> float:
        """Get density of ingredient (g/ml)."""
        # Common densities
        densities = {
            'leche': 1.03,
            'agua': 1.0,
            'aceite': 0.92,
            'miel': 1.4,
            'harina': 0.6,
            'azucar': 0.85,
            'sal': 1.2
        }
        
        for ingredient, density in densities.items():
            if ingredient in ingredient_name.lower():
                return density
        
        return 1.0  # Default water density
    
    def _get_unit_weight(self, ingredient_name: str) -> float:
        """Get weight of one unit of ingredient."""
        # Common unit weights in grams
        unit_weights = {
            'huevo': 60,
            'banana': 120,
            'manzana': 150,
            'papa': 100,
            'tomate': 80,
            'cebolla': 100,
            'zanahoria': 70,
            'pan': 30,  # slice
            'queso': 20  # slice
        }
        
        for ingredient, weight in unit_weights.items():
            if ingredient in ingredient_name.lower():
                return weight
        
        return 100  # Default weight
    
    def _get_nutrient_unit(self, nutrient: str) -> str:
        """Get the standard unit for a nutrient."""
        nutrient_units = {
            'calories': 'kcal',
            'protein': 'g',
            'carbs': 'g',
            'fat': 'g',
            'fiber': 'g',
            'sugar': 'g',
            'sodium': 'mg',
            'calcium': 'mg',
            'iron': 'mg',
            'vitamin_c': 'mg',
            'vitamin_a': 'ui'
        }
        
        return nutrient_units.get(nutrient, 'unknown')
    
    def calculate_per_serving(self, nutritional_data: Dict[str, NutritionalValue], 
                             servings: int) -> Dict[str, NutritionalValue]:
        """Calculate nutritional values per serving."""
        if not servings or servings <= 0:
            return nutritional_data
        
        per_serving = {}
        
        for nutrient, value in nutritional_data.items():
            per_serving[nutrient] = NutritionalValue(
                value=value.value / servings,
                unit=value.unit,
                confidence=value.confidence,
                source=value.source,
                per_unit='per_serving'
            )
        
        return per_serving
    
    def normalize_to_100g(self, nutritional_data: Dict[str, NutritionalValue], 
                         total_weight_grams: float) -> Dict[str, NutritionalValue]:
        """Normalize nutritional values to per 100g."""
        if not total_weight_grams or total_weight_grams <= 0:
            return nutritional_data
        
        normalized = {}
        factor = 100 / total_weight_grams
        
        for nutrient, value in nutritional_data.items():
            normalized[nutrient] = NutritionalValue(
                value=value.value * factor,
                unit=value.unit,
                confidence=value.confidence,
                source=value.source,
                per_unit='per_100g'
            )
        
        return normalized
    
    def validate_nutritional_data(self, nutritional_data: Dict[str, NutritionalValue]) -> Dict[str, Any]:
        """Validate nutritional data and return validation results."""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check for required nutrients
        required_nutrients = ['calories', 'protein', 'carbs', 'fat']
        for nutrient in required_nutrients:
            if nutrient not in nutritional_data:
                validation_results['warnings'].append(f"Missing {nutrient} information")
        
        # Check for reasonable values
        if 'calories' in nutritional_data:
            calories = nutritional_data['calories'].value
            if calories < 0 or calories > 900:  # per 100g
                validation_results['errors'].append(f"Unreasonable calorie value: {calories}")
                validation_results['is_valid'] = False
        
        # Check macronutrient balance
        if all(nutrient in nutritional_data for nutrient in ['protein', 'carbs', 'fat']):
            protein_cal = nutritional_data['protein'].value * 4
            carbs_cal = nutritional_data['carbs'].value * 4
            fat_cal = nutritional_data['fat'].value * 9
            
            calculated_calories = protein_cal + carbs_cal + fat_cal
            
            if 'calories' in nutritional_data:
                stated_calories = nutritional_data['calories'].value
                if abs(calculated_calories - stated_calories) > stated_calories * 0.2:
                    validation_results['warnings'].append(
                        f"Macronutrient calories ({calculated_calories}) don't match stated calories ({stated_calories})"
                    )
        
        return validation_results
    
    def generate_nutrition_summary(self, nutritional_data: Dict[str, NutritionalValue]) -> str:
        """Generate a human-readable nutrition summary."""
        if not nutritional_data:
            return "No nutritional information available."
        
        summary_parts = []
        
        # Main macronutrients
        if 'calories' in nutritional_data:
            calories = nutritional_data['calories']
            summary_parts.append(f"Calorías: {calories.value:.0f} {calories.unit}")
        
        if 'protein' in nutritional_data:
            protein = nutritional_data['protein']
            summary_parts.append(f"Proteína: {protein.value:.1f} {protein.unit}")
        
        if 'carbs' in nutritional_data:
            carbs = nutritional_data['carbs']
            summary_parts.append(f"Carbohidratos: {carbs.value:.1f} {carbs.unit}")
        
        if 'fat' in nutritional_data:
            fat = nutritional_data['fat']
            summary_parts.append(f"Grasa: {fat.value:.1f} {fat.unit}")
        
        # Additional nutrients
        if 'fiber' in nutritional_data:
            fiber = nutritional_data['fiber']
            summary_parts.append(f"Fibra: {fiber.value:.1f} {fiber.unit}")
        
        return " | ".join(summary_parts)
    
    def export_to_dict(self, nutritional_data: Dict[str, NutritionalValue]) -> Dict[str, Any]:
        """Export nutritional data to a dictionary format."""
        exported = {}
        
        for nutrient, value in nutritional_data.items():
            exported[nutrient] = {
                'value': value.value,
                'unit': value.unit,
                'confidence': value.confidence,
                'source': value.source,
                'per_unit': value.per_unit
            }
        
        return exported