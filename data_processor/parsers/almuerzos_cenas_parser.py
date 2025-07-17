"""
Parser for Almuerzos/Cenas DOCX files.
Handles table extraction for 6 food categories: Pollo, Carne, Vegetarianos, Cerdo, Pescado/Mariscos, Ensaladas
"""

import logging
from typing import Dict, List, Any, Optional
import re

from .base_parser import BaseDocxParser

logger = logging.getLogger(__name__)


class AlmuerzosECenasParser(BaseDocxParser):
    """
    Parser for lunch and dinner recipes organized by food categories.
    Extracts recipes from tables with standardized format.
    """
    
    # Define the 6 main food categories
    FOOD_CATEGORIES = [
        'pollo',
        'carne',
        'vegetarianos',
        'cerdo',
        'pescado',
        'mariscos',
        'ensaladas'
    ]
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.recipes = []
        self.categories_found = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse the document and extract categorized recipes."""
        self.load_document()
        
        if not self.validate_structure():
            raise ValueError("Document structure does not match expected format")
        
        # Extract recipes from each table
        recipes_by_category = self._extract_recipes_by_category()
        
        # Process and standardize recipes
        processed_recipes = self._process_recipes(recipes_by_category)
        
        return {
            'type': 'almuerzos_cenas',
            'categories': list(self.categories_found.keys()),
            'total_recipes': len(processed_recipes),
            'recipes': processed_recipes,
            'metadata': {
                'file_path': str(self.file_path),
                'categories_found': self.categories_found,
                'table_count': len(self.tables)
            }
        }
    
    def validate_structure(self) -> bool:
        """Validate that the document has the expected structure for almuerzos/cenas."""
        if not self.tables:
            logger.error("No tables found in document")
            return False
        
        # Check if we can find at least one food category
        tables_data = self.extract_tables_data()
        category_found = False
        
        for table_data in tables_data:
            if self._identify_food_category(table_data):
                category_found = True
                break
        
        if not category_found:
            logger.error("No recognized food categories found in document")
            return False
        
        return True
    
    def _extract_recipes_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract recipes organized by food category."""
        recipes_by_category = {}
        tables_data = self.extract_tables_data()
        
        for table_data in tables_data:
            category = self._identify_food_category(table_data)
            if category:
                recipes = self._extract_recipes_from_table(table_data, category)
                if recipes:
                    recipes_by_category[category] = recipes
                    self.categories_found[category] = len(recipes)
        
        return recipes_by_category
    
    def _identify_food_category(self, table_data: Dict[str, Any]) -> Optional[str]:
        """Identify the food category from table headers or content."""
        headers = table_data.get('headers', [])
        
        # Check headers for category keywords
        for header in headers:
            header_lower = header.lower()
            
            # Check for exact matches or variations
            if 'pollo' in header_lower:
                return 'pollo'
            elif 'carne' in header_lower and 'mariscos' not in header_lower:
                return 'carne'
            elif 'vegetarian' in header_lower or 'vegetariano' in header_lower:
                return 'vegetarianos'
            elif 'cerdo' in header_lower:
                return 'cerdo'
            elif 'pescado' in header_lower:
                return 'pescado'
            elif 'mariscos' in header_lower:
                return 'mariscos'
            elif 'ensalada' in header_lower:
                return 'ensaladas'
        
        # Check first few rows for category indicators
        rows = table_data.get('rows', [])
        if rows:
            first_row_text = ' '.join(rows[0]).lower()
            
            for category in self.FOOD_CATEGORIES:
                if category in first_row_text:
                    return category
        
        return None
    
    def _extract_recipes_from_table(self, table_data: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        """Extract individual recipes from a table."""
        recipes = []
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers or not rows:
            return recipes
        
        # Try to identify column structure
        column_mapping = self._identify_columns(headers)
        
        for row_index, row in enumerate(rows):
            if len(row) < len(headers):
                continue
                
            recipe = self._extract_recipe_from_row(row, column_mapping, category, row_index)
            if recipe:
                recipes.append(recipe)
        
        return recipes
    
    def _identify_columns(self, headers: List[str]) -> Dict[str, int]:
        """Identify which columns contain which type of information."""
        column_mapping = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            # Map common column types
            if any(keyword in header_lower for keyword in ['nombre', 'receta', 'plato', 'comida']):
                column_mapping['name'] = i
            elif any(keyword in header_lower for keyword in ['ingrediente', 'ingredientes']):
                column_mapping['ingredients'] = i
            elif any(keyword in header_lower for keyword in ['preparación', 'preparacion', 'instrucciones']):
                column_mapping['preparation'] = i
            elif any(keyword in header_lower for keyword in ['porción', 'porcion', 'cantidad']):
                column_mapping['portion'] = i
            elif any(keyword in header_lower for keyword in ['calorías', 'calorias', 'kcal']):
                column_mapping['calories'] = i
            elif any(keyword in header_lower for keyword in ['proteína', 'proteinas', 'protein']):
                column_mapping['protein'] = i
            elif any(keyword in header_lower for keyword in ['carbohidratos', 'carbs', 'hidratos']):
                column_mapping['carbs'] = i
            elif any(keyword in header_lower for keyword in ['grasa', 'grasas', 'fat']):
                column_mapping['fat'] = i
            elif any(keyword in header_lower for keyword in ['tiempo', 'duración', 'duracion']):
                column_mapping['cooking_time'] = i
            elif any(keyword in header_lower for keyword in ['dificultad', 'nivel']):
                column_mapping['difficulty'] = i
            elif any(keyword in header_lower for keyword in ['económico', 'economico', 'precio', 'costo']):
                column_mapping['economic_level'] = i
        
        return column_mapping
    
    def _extract_recipe_from_row(self, row: List[str], column_mapping: Dict[str, int], 
                                category: str, row_index: int) -> Optional[Dict[str, Any]]:
        """Extract a single recipe from a table row."""
        if not row or not any(row):
            return None
        
        recipe = {
            'id': f"{category}_{row_index}",
            'category': category,
            'subcategory': self._determine_subcategory(category, row),
            'name': '',
            'ingredients': [],
            'preparation': '',
            'cooking_time': None,
            'difficulty': None,
            'economic_level': None,
            'portion_size': None,
            'nutritional_info': {}
        }
        
        # Extract data based on column mapping
        for field, col_index in column_mapping.items():
            if col_index < len(row):
                value = row[col_index]
                
                if field == 'name':
                    recipe['name'] = self._clean_text(value)
                elif field == 'ingredients':
                    recipe['ingredients'] = self.extract_ingredients_list(value)
                elif field == 'preparation':
                    recipe['preparation'] = self._clean_text(value)
                elif field == 'portion':
                    recipe['portion_size'] = self._parse_portion_size(value)
                elif field == 'cooking_time':
                    recipe['cooking_time'] = self._parse_cooking_time(value)
                elif field == 'difficulty':
                    recipe['difficulty'] = self._parse_difficulty(value)
                elif field == 'economic_level':
                    recipe['economic_level'] = self._parse_economic_level(value)
                elif field in ['calories', 'protein', 'carbs', 'fat']:
                    recipe['nutritional_info'][field] = self._parse_nutritional_value(value)
        
        # If no name found, try to extract from first non-empty cell
        if not recipe['name']:
            for cell in row:
                if cell and cell.strip():
                    recipe['name'] = self._clean_text(cell)
                    break
        
        # Extract nutritional info if not already extracted
        if not recipe['nutritional_info']:
            for cell in row:
                nutritional_values = self.extract_nutritional_values(cell)
                if nutritional_values:
                    recipe['nutritional_info'].update(nutritional_values)
        
        return recipe if recipe['name'] else None
    
    def _determine_subcategory(self, category: str, row: List[str]) -> Optional[str]:
        """Determine subcategory based on category and row content."""
        row_text = ' '.join(row).lower()
        
        if category == 'pollo':
            if 'pechuga' in row_text:
                return 'pechuga'
            elif 'muslo' in row_text:
                return 'muslo'
            elif 'entero' in row_text:
                return 'entero'
                
        elif category == 'carne':
            if 'res' in row_text or 'vaca' in row_text:
                return 'res'
            elif 'ternera' in row_text:
                return 'ternera'
            elif 'cordero' in row_text:
                return 'cordero'
                
        elif category == 'pescado':
            if 'salmón' in row_text or 'salmon' in row_text:
                return 'salmon'
            elif 'atún' in row_text or 'atun' in row_text:
                return 'atun'
            elif 'merluza' in row_text:
                return 'merluza'
                
        elif category == 'ensaladas':
            if 'verde' in row_text:
                return 'verde'
            elif 'mixta' in row_text:
                return 'mixta'
            elif 'césar' in row_text or 'cesar' in row_text:
                return 'cesar'
        
        return None
    
    def _parse_portion_size(self, value: str) -> Optional[Dict[str, Any]]:
        """Parse portion size from text."""
        if not value:
            return None
        
        portions = self.extract_portions(value)
        if portions:
            return portions[0]  # Return first portion found
        
        return None
    
    def _parse_cooking_time(self, value: str) -> Optional[int]:
        """Parse cooking time in minutes."""
        if not value:
            return None
        
        # Look for time patterns
        time_patterns = [
            r'(\d+)\s*min',
            r'(\d+)\s*minutos',
            r'(\d+)\s*h',
            r'(\d+)\s*horas',
            r'(\d+)\s*hrs'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, value.lower())
            if match:
                time_value = int(match.group(1))
                # Convert hours to minutes
                if 'h' in pattern:
                    time_value *= 60
                return time_value
        
        return None
    
    def _parse_difficulty(self, value: str) -> Optional[str]:
        """Parse difficulty level."""
        if not value:
            return None
        
        value_lower = value.lower()
        
        if any(word in value_lower for word in ['fácil', 'facil', 'easy']):
            return 'facil'
        elif any(word in value_lower for word in ['medio', 'intermedio', 'medium']):
            return 'medio'
        elif any(word in value_lower for word in ['difícil', 'dificil', 'hard']):
            return 'dificil'
        
        return None
    
    def _parse_economic_level(self, value: str) -> Optional[str]:
        """Parse economic level."""
        if not value:
            return None
        
        value_lower = value.lower()
        
        if any(word in value_lower for word in ['bajo', 'barato', 'económico', 'economico']):
            return 'bajo'
        elif any(word in value_lower for word in ['medio', 'moderado']):
            return 'medio'
        elif any(word in value_lower for word in ['alto', 'caro', 'premium']):
            return 'alto'
        
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
    
    def _process_recipes(self, recipes_by_category: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Process and standardize all recipes."""
        processed_recipes = []
        
        for category, recipes in recipes_by_category.items():
            for recipe in recipes:
                processed_recipe = self._standardize_recipe(recipe)
                if processed_recipe:
                    processed_recipes.append(processed_recipe)
        
        return processed_recipes
    
    def _standardize_recipe(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize recipe format and add missing fields."""
        standardized = {
            'id': recipe.get('id'),
            'name': recipe.get('name', '').strip(),
            'category': 'almuerzos_cenas',
            'subcategory': recipe.get('category'),
            'food_type': recipe.get('subcategory'),
            'ingredients': recipe.get('ingredients', []),
            'preparation': recipe.get('preparation', ''),
            'cooking_time': recipe.get('cooking_time'),
            'difficulty': recipe.get('difficulty'),
            'economic_level': recipe.get('economic_level'),
            'portion_size': recipe.get('portion_size'),
            'nutritional_info': recipe.get('nutritional_info', {}),
            'dietary_restrictions': self._identify_dietary_restrictions(recipe),
            'tags': self._generate_tags(recipe),
            'suitable_for': self._identify_suitable_for(recipe)
        }
        
        # Validate required fields
        if not standardized['name']:
            return None
        
        return standardized
    
    def _identify_dietary_restrictions(self, recipe: Dict[str, Any]) -> List[str]:
        """Identify dietary restrictions based on recipe content."""
        restrictions = []
        
        ingredients_text = ' '.join(recipe.get('ingredients', [])).lower()
        name_text = recipe.get('name', '').lower()
        full_text = f"{name_text} {ingredients_text}"
        
        # Vegetarian/Vegan
        if recipe.get('category') == 'vegetarianos':
            restrictions.append('vegetariano')
        
        # Gluten-free indicators
        if not any(gluten in full_text for gluten in ['harina', 'pan', 'trigo', 'avena', 'cebada']):
            restrictions.append('sin_gluten')
        
        # Lactose-free indicators  
        if not any(dairy in full_text for dairy in ['leche', 'queso', 'yogur', 'crema', 'manteca']):
            restrictions.append('sin_lactosa')
        
        # Low sodium
        if 'sin sal' in full_text or 'bajo sodio' in full_text:
            restrictions.append('bajo_sodio')
        
        return restrictions
    
    def _generate_tags(self, recipe: Dict[str, Any]) -> List[str]:
        """Generate tags for recipe categorization."""
        tags = []
        
        # Add category tags
        if recipe.get('category'):
            tags.append(recipe['category'])
        
        if recipe.get('subcategory'):
            tags.append(recipe['subcategory'])
        
        # Add difficulty tag
        if recipe.get('difficulty'):
            tags.append(f"dificultad_{recipe['difficulty']}")
        
        # Add economic level tag
        if recipe.get('economic_level'):
            tags.append(f"economico_{recipe['economic_level']}")
        
        # Add cooking time tags
        cooking_time = recipe.get('cooking_time')
        if cooking_time:
            if cooking_time <= 15:
                tags.append('rapido')
            elif cooking_time <= 30:
                tags.append('medio_tiempo')
            else:
                tags.append('tiempo_largo')
        
        return tags
    
    def _identify_suitable_for(self, recipe: Dict[str, Any]) -> List[str]:
        """Identify what this recipe is suitable for."""
        suitable_for = ['almuerzo', 'cena']
        
        # Add based on category
        category = recipe.get('category')
        if category == 'ensaladas':
            suitable_for.append('entrada')
            suitable_for.append('acompañamiento')
        elif category in ['pollo', 'carne', 'pescado', 'cerdo']:
            suitable_for.append('plato_principal')
        elif category == 'vegetarianos':
            suitable_for.append('vegetariano')
            suitable_for.append('plato_principal')
        
        return suitable_for