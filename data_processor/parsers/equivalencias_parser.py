"""
Parser for Equivalencias calóricas DOCX files.
Handles extraction of portion exchanges and caloric equivalencies.
"""

import logging
from typing import Dict, List, Any, Optional
import re

from .base_parser import BaseDocxParser

logger = logging.getLogger(__name__)


class EquivalenciasParser(BaseDocxParser):
    """
    Parser for caloric equivalencies and portion exchanges.
    Extracts food substitution tables and portion conversion data.
    """
    
    # Define food groups for equivalencies
    FOOD_GROUPS = {
        'cereales': ['cereal', 'cereales', 'granos', 'grain', 'grains'],
        'proteinas': ['proteína', 'proteinas', 'protein', 'carne', 'pollo', 'pescado'],
        'lacteos': ['lácteo', 'lacteo', 'lacteos', 'leche', 'dairy', 'queso'],
        'frutas': ['fruta', 'frutas', 'fruit', 'fruits'],
        'verduras': ['verdura', 'verduras', 'vegetable', 'vegetables', 'vegetal'],
        'grasas': ['grasa', 'grasas', 'fat', 'fats', 'aceite', 'oil'],
        'azucares': ['azúcar', 'azucar', 'sugar', 'dulce', 'sweet'],
        'legumbres': ['legumbre', 'legumbres', 'legume', 'legumes', 'lenteja', 'garbanzo']
    }
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.equivalencies = []
        self.food_groups_found = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse the document and extract equivalencies."""
        self.load_document()
        
        if not self.validate_structure():
            raise ValueError("Document structure does not match expected format")
        
        # Extract equivalencies from tables
        equivalencies_by_group = self._extract_equivalencies_by_group()
        
        # Process and standardize equivalencies
        processed_equivalencies = self._process_equivalencies(equivalencies_by_group)
        
        return {
            'type': 'equivalencias_caloricas',
            'food_groups': list(self.food_groups_found.keys()),
            'total_equivalencies': len(processed_equivalencies),
            'equivalencies': processed_equivalencies,
            'metadata': {
                'file_path': str(self.file_path),
                'food_groups_found': self.food_groups_found,
                'table_count': len(self.tables)
            }
        }
    
    def validate_structure(self) -> bool:
        """Validate that the document has the expected structure."""
        if not self.tables:
            logger.error("No tables found in document")
            return False
        
        # Check if we can find at least one food group
        tables_data = self.extract_tables_data()
        group_found = False
        
        for table_data in tables_data:
            if self._identify_food_group(table_data):
                group_found = True
                break
        
        if not group_found:
            logger.error("No recognized food groups found in document")
            return False
        
        return True
    
    def _extract_equivalencies_by_group(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract equivalencies organized by food group."""
        equivalencies_by_group = {}
        tables_data = self.extract_tables_data()
        
        for table_data in tables_data:
            food_group = self._identify_food_group(table_data)
            if food_group:
                equivalencies = self._extract_equivalencies_from_table(table_data, food_group)
                if equivalencies:
                    equivalencies_by_group[food_group] = equivalencies
                    self.food_groups_found[food_group] = len(equivalencies)
        
        return equivalencies_by_group
    
    def _identify_food_group(self, table_data: Dict[str, Any]) -> Optional[str]:
        """Identify the food group from table headers or content."""
        headers = table_data.get('headers', [])
        
        # Check headers for food group keywords
        for header in headers:
            header_lower = header.lower()
            
            for group, keywords in self.FOOD_GROUPS.items():
                if any(keyword in header_lower for keyword in keywords):
                    return group
        
        # Check first few rows for food group indicators
        rows = table_data.get('rows', [])
        if rows:
            first_row_text = ' '.join(rows[0]).lower()
            
            for group, keywords in self.FOOD_GROUPS.items():
                if any(keyword in first_row_text for keyword in keywords):
                    return group
        
        return None
    
    def _extract_equivalencies_from_table(self, table_data: Dict[str, Any], food_group: str) -> List[Dict[str, Any]]:
        """Extract equivalencies from a table."""
        equivalencies = []
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers or not rows:
            return equivalencies
        
        # Try to identify column structure
        column_mapping = self._identify_columns(headers)
        
        for row_index, row in enumerate(rows):
            if len(row) < len(headers):
                continue
                
            equivalency = self._extract_equivalency_from_row(row, column_mapping, food_group, row_index)
            if equivalency:
                equivalencies.append(equivalency)
        
        return equivalencies
    
    def _identify_columns(self, headers: List[str]) -> Dict[str, int]:
        """Identify which columns contain which type of information."""
        column_mapping = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            # Map common column types
            if any(keyword in header_lower for keyword in ['alimento', 'food', 'ingrediente']):
                column_mapping['food'] = i
            elif any(keyword in header_lower for keyword in ['cantidad', 'porción', 'porcion']):
                column_mapping['portion'] = i
            elif any(keyword in header_lower for keyword in ['peso', 'gramos', 'g']):
                column_mapping['weight'] = i
            elif any(keyword in header_lower for keyword in ['calorías', 'calorias', 'kcal']):
                column_mapping['calories'] = i
            elif any(keyword in header_lower for keyword in ['proteína', 'proteinas', 'protein']):
                column_mapping['protein'] = i
            elif any(keyword in header_lower for keyword in ['carbohidratos', 'carbs', 'hidratos']):
                column_mapping['carbs'] = i
            elif any(keyword in header_lower for keyword in ['grasa', 'grasas', 'fat']):
                column_mapping['fat'] = i
            elif any(keyword in header_lower for keyword in ['fibra', 'fiber']):
                column_mapping['fiber'] = i
            elif any(keyword in header_lower for keyword in ['equivale', 'equivalencia', 'substitute']):
                column_mapping['equivalent'] = i
            elif any(keyword in header_lower for keyword in ['intercambio', 'exchange']):
                column_mapping['exchange'] = i
        
        return column_mapping
    
    def _extract_equivalency_from_row(self, row: List[str], column_mapping: Dict[str, int], 
                                     food_group: str, row_index: int) -> Optional[Dict[str, Any]]:
        """Extract a single equivalency from a table row."""
        if not row or not any(row):
            return None
        
        equivalency = {
            'id': f"{food_group}_{row_index}",
            'food_group': food_group,
            'food_name': '',
            'portion': None,
            'weight': None,
            'calories': None,
            'protein': None,
            'carbs': None,
            'fat': None,
            'fiber': None,
            'equivalent_to': [],
            'exchange_unit': None,
            'nutritional_info': {}
        }
        
        # Extract data based on column mapping
        for field, col_index in column_mapping.items():
            if col_index < len(row):
                value = row[col_index]
                
                if field == 'food':
                    equivalency['food_name'] = self._clean_text(value)
                elif field == 'portion':
                    equivalency['portion'] = self._parse_portion_description(value)
                elif field == 'weight':
                    equivalency['weight'] = self._parse_weight(value)
                elif field == 'calories':
                    equivalency['calories'] = self._parse_nutritional_value(value)
                elif field == 'protein':
                    equivalency['protein'] = self._parse_nutritional_value(value)
                elif field == 'carbs':
                    equivalency['carbs'] = self._parse_nutritional_value(value)
                elif field == 'fat':
                    equivalency['fat'] = self._parse_nutritional_value(value)
                elif field == 'fiber':
                    equivalency['fiber'] = self._parse_nutritional_value(value)
                elif field == 'equivalent':
                    equivalency['equivalent_to'] = self._parse_equivalents(value)
                elif field == 'exchange':
                    equivalency['exchange_unit'] = self._parse_exchange_unit(value)
        
        # If no food name found, try to extract from first non-empty cell
        if not equivalency['food_name']:
            for cell in row:
                if cell and cell.strip():
                    equivalency['food_name'] = self._clean_text(cell)
                    break
        
        # Build nutritional info dict
        equivalency['nutritional_info'] = {
            'calories': equivalency['calories'],
            'protein': equivalency['protein'],
            'carbs': equivalency['carbs'],
            'fat': equivalency['fat'],
            'fiber': equivalency['fiber']
        }
        
        return equivalency if equivalency['food_name'] else None
    
    def _parse_portion_description(self, value: str) -> Optional[Dict[str, Any]]:
        """Parse portion description from text."""
        if not value:
            return None
        
        # Common portion descriptions
        portion_patterns = [
            r'(\d+(?:\.\d+)?)\s*(taza|tazas|cup|cups)',
            r'(\d+(?:\.\d+)?)\s*(cucharada|cucharadas|cda|cdas|tbsp)',
            r'(\d+(?:\.\d+)?)\s*(cucharadita|cucharaditas|cdita|cditas|tsp)',
            r'(\d+(?:\.\d+)?)\s*(unidad|unidades|u|pieza|piezas)',
            r'(\d+(?:\.\d+)?)\s*(rodaja|rodajas|slice|slices)',
            r'(\d+(?:\.\d+)?)\s*(porción|porciones|portion|portions)',
            r'(\d+(?:\.\d+)?)\s*(g|gr|gramos?|kg|kilogramos?)',
            r'(\d+(?:\.\d+)?)\s*(ml|cc|litros?)'
        ]
        
        for pattern in portion_patterns:
            match = re.search(pattern, value.lower())
            if match:
                try:
                    amount = float(match.group(1))
                    unit = match.group(2)
                    return {
                        'amount': amount,
                        'unit': unit,
                        'description': value.strip()
                    }
                except (ValueError, IndexError):
                    continue
        
        # If no pattern matches, return as description
        return {
            'amount': None,
            'unit': None,
            'description': value.strip()
        }
    
    def _parse_weight(self, value: str) -> Optional[float]:
        """Parse weight in grams."""
        if not value:
            return None
        
        # Extract numeric value and convert to grams
        weight_patterns = [
            r'(\d+(?:\.\d+)?)\s*g',
            r'(\d+(?:\.\d+)?)\s*gr',
            r'(\d+(?:\.\d+)?)\s*gramos?',
            r'(\d+(?:\.\d+)?)\s*kg',
            r'(\d+(?:\.\d+)?)\s*kilogramos?'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, value.lower())
            if match:
                try:
                    weight = float(match.group(1))
                    # Convert kg to grams
                    if 'kg' in pattern:
                        weight *= 1000
                    return weight
                except ValueError:
                    continue
        
        return None
    
    def _parse_nutritional_value(self, value: str) -> Optional[float]:
        """Parse nutritional value from text."""
        if not value:
            return None
        
        # Extract numeric value
        match = re.search(r'(\d+(?:\.\d+)?)', value)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None
    
    def _parse_equivalents(self, value: str) -> List[Dict[str, Any]]:
        """Parse equivalent foods from text."""
        if not value:
            return []
        
        equivalents = []
        
        # Split by common delimiters
        items = re.split(r'[,;]|=|equivale a|igual a', value.lower())
        
        for item in items:
            item = item.strip()
            if not item:
                continue
                
            # Try to extract portion information
            portions = self.extract_portions(item)
            if portions:
                equivalents.append({
                    'food': item,
                    'portion': portions[0],
                    'description': item
                })
            else:
                equivalents.append({
                    'food': item,
                    'portion': None,
                    'description': item
                })
        
        return equivalents
    
    def _parse_exchange_unit(self, value: str) -> Optional[str]:
        """Parse exchange unit from text."""
        if not value:
            return None
        
        value_lower = value.lower()
        
        # Common exchange units
        if any(unit in value_lower for unit in ['intercambio', 'exchange']):
            return 'intercambio'
        elif any(unit in value_lower for unit in ['porción', 'porcion', 'portion']):
            return 'porcion'
        elif any(unit in value_lower for unit in ['unidad', 'unit']):
            return 'unidad'
        
        return value.strip()
    
    def _process_equivalencies(self, equivalencies_by_group: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Process and standardize all equivalencies."""
        processed_equivalencies = []
        
        for food_group, equivalencies in equivalencies_by_group.items():
            for equivalency in equivalencies:
                processed_equivalency = self._standardize_equivalency(equivalency)
                if processed_equivalency:
                    processed_equivalencies.append(processed_equivalency)
        
        return processed_equivalencies
    
    def _standardize_equivalency(self, equivalency: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize equivalency format and add missing fields."""
        standardized = {
            'id': equivalency.get('id'),
            'food_name': equivalency.get('food_name', '').strip(),
            'food_group': equivalency.get('food_group'),
            'portion': equivalency.get('portion'),
            'weight_grams': equivalency.get('weight'),
            'calories_per_portion': equivalency.get('calories'),
            'macronutrients': {
                'protein': equivalency.get('protein'),
                'carbs': equivalency.get('carbs'),
                'fat': equivalency.get('fat'),
                'fiber': equivalency.get('fiber')
            },
            'equivalent_foods': equivalency.get('equivalent_to', []),
            'exchange_unit': equivalency.get('exchange_unit'),
            'nutritional_density': self._calculate_nutritional_density(equivalency),
            'substitution_category': self._determine_substitution_category(equivalency),
            'usage_notes': self._generate_usage_notes(equivalency),
            'conversion_factors': self._calculate_conversion_factors(equivalency)
        }
        
        # Validate required fields
        if not standardized['food_name']:
            return None
        
        return standardized
    
    def _calculate_nutritional_density(self, equivalency: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate nutritional density per 100g."""
        weight = equivalency.get('weight')
        if not weight or weight == 0:
            return {}
        
        density = {}
        
        # Calculate per 100g
        factor = 100 / weight
        
        for nutrient in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
            value = equivalency.get(nutrient)
            if value is not None:
                density[f"{nutrient}_per_100g"] = value * factor
        
        return density
    
    def _determine_substitution_category(self, equivalency: Dict[str, Any]) -> str:
        """Determine the substitution category based on macronutrient profile."""
        protein = equivalency.get('protein', 0) or 0
        carbs = equivalency.get('carbs', 0) or 0
        fat = equivalency.get('fat', 0) or 0
        
        total_macros = protein + carbs + fat
        
        if total_macros == 0:
            return 'unknown'
        
        # Calculate percentages
        protein_pct = (protein * 4) / (total_macros * 4) * 100
        carbs_pct = (carbs * 4) / (total_macros * 4) * 100
        fat_pct = (fat * 9) / (total_macros * 4) * 100
        
        # Determine category
        if protein_pct > 50:
            return 'alto_proteina'
        elif carbs_pct > 60:
            return 'alto_carbohidrato'
        elif fat_pct > 60:
            return 'alto_grasa'
        else:
            return 'mixto'
    
    def _generate_usage_notes(self, equivalency: Dict[str, Any]) -> List[str]:
        """Generate usage notes for the equivalency."""
        notes = []
        
        food_group = equivalency.get('food_group')
        food_name = equivalency.get('food_name', '').lower()
        
        # Add group-specific notes
        if food_group == 'cereales':
            notes.append("Preferir versiones integrales cuando sea posible")
        elif food_group == 'proteinas':
            notes.append("Variar entre fuentes animales y vegetales")
        elif food_group == 'lacteos':
            notes.append("Elegir opciones bajas en grasa si es necesario")
        elif food_group == 'frutas':
            notes.append("Consumir preferentemente enteras, no en jugos")
        elif food_group == 'verduras':
            notes.append("Incluir variedad de colores")
        elif food_group == 'grasas':
            notes.append("Usar con moderación")
        
        # Add specific food notes
        if 'frito' in food_name:
            notes.append("Limitar consumo por alto contenido de grasas")
        elif 'integral' in food_name:
            notes.append("Excelente fuente de fibra")
        elif 'light' in food_name:
            notes.append("Opción reducida en calorías")
        
        return notes
    
    def _calculate_conversion_factors(self, equivalency: Dict[str, Any]) -> Dict[str, float]:
        """Calculate conversion factors for common portions."""
        weight = equivalency.get('weight')
        if not weight:
            return {}
        
        conversion_factors = {}
        
        # Common conversions
        conversion_factors['per_gram'] = 1 / weight
        conversion_factors['per_100g'] = 100 / weight
        
        # Add specific conversions based on food group
        food_group = equivalency.get('food_group')
        
        if food_group == 'cereales':
            conversion_factors['per_cup'] = 240 / weight if weight else 0
        elif food_group == 'lacteos':
            conversion_factors['per_cup'] = 240 / weight if weight else 0
        elif food_group == 'grasas':
            conversion_factors['per_tbsp'] = 15 / weight if weight else 0
        
        return conversion_factors