"""
Parser for Desayunos/Meriendas DOCX files.
Handles extraction of breakfast and snack recipes organized in dulces, salados, and colaciones.
"""

import logging
from typing import Dict, List, Any, Optional
import re

from .base_parser import BaseDocxParser

logger = logging.getLogger(__name__)


class DesayunosYMeriendasParser(BaseDocxParser):
    """
    Parser for breakfast and snack recipes organized by sweet, savory, and snack categories.
    """
    
    # Define the main categories
    CATEGORIES = {
        'dulces': ['dulce', 'dulces', 'sweet', 'postre', 'postres'],
        'salados': ['salado', 'salados', 'savory', 'salty'],
        'colaciones': ['colación', 'colaciones', 'snack', 'snacks', 'merienda', 'meriendas']
    }
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.recipes = []
        self.categories_found = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse the document and extract breakfast/snack recipes."""
        self.load_document()
        
        if not self.validate_structure():
            raise ValueError("Document structure does not match expected format")
        
        # Extract recipes from each category
        recipes_by_category = self._extract_recipes_by_category()
        
        # Process and standardize recipes
        processed_recipes = self._process_recipes(recipes_by_category)
        
        return {
            'type': 'desayunos_meriendas',
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
        """Validate that the document has the expected structure."""
        if not self.tables:
            logger.error("No tables found in document")
            return False
        
        # Check if we can find at least one category
        tables_data = self.extract_tables_data()
        category_found = False
        
        for table_data in tables_data:
            if self._identify_category(table_data):
                category_found = True
                break
        
        if not category_found:
            logger.error("No recognized categories found in document")
            return False
        
        return True
    
    def _extract_recipes_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract recipes organized by category."""
        recipes_by_category = {}
        tables_data = self.extract_tables_data()
        
        for table_data in tables_data:
            category = self._identify_category(table_data)
            if category:
                recipes = self._extract_recipes_from_table(table_data, category)
                if recipes:
                    recipes_by_category[category] = recipes
                    self.categories_found[category] = len(recipes)
        
        return recipes_by_category
    
    def _identify_category(self, table_data: Dict[str, Any]) -> Optional[str]:
        """Identify the category from table headers or content."""
        headers = table_data.get('headers', [])
        
        # Check headers for category keywords
        for header in headers:
            header_lower = header.lower()
            
            for category, keywords in self.CATEGORIES.items():
                if any(keyword in header_lower for keyword in keywords):
                    return category
        
        # Check first few rows for category indicators
        rows = table_data.get('rows', [])
        if rows:
            first_row_text = ' '.join(rows[0]).lower()
            
            for category, keywords in self.CATEGORIES.items():
                if any(keyword in first_row_text for keyword in keywords):
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
            if any(keyword in header_lower for keyword in ['nombre', 'receta', 'opción', 'opcion']):
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
            elif any(keyword in header_lower for keyword in ['momento', 'horario', 'cuando']):
                column_mapping['meal_time'] = i
            elif any(keyword in header_lower for keyword in ['tipo', 'clasificación', 'clasificacion']):
                column_mapping['type'] = i
        
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
            'meal_time': None,
            'recipe_type': None,
            'portion_size': None,
            'nutritional_info': {},
            'suitable_for': []
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
                elif field == 'meal_time':
                    recipe['meal_time'] = self._parse_meal_time(value)
                elif field == 'type':
                    recipe['recipe_type'] = self._clean_text(value)
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
        
        # Determine suitable meal times
        recipe['suitable_for'] = self._determine_suitable_for(recipe)
        
        return recipe if recipe['name'] else None
    
    def _determine_subcategory(self, category: str, row: List[str]) -> Optional[str]:
        """Determine subcategory based on category and row content."""
        row_text = ' '.join(row).lower()
        
        if category == 'dulces':
            if any(keyword in row_text for keyword in ['batido', 'smoothie', 'licuado']):
                return 'batidos'
            elif any(keyword in row_text for keyword in ['yogur', 'yogurt']):
                return 'yogures'
            elif any(keyword in row_text for keyword in ['avena', 'oatmeal']):
                return 'avena'
            elif any(keyword in row_text for keyword in ['fruta', 'frutas']):
                return 'frutas'
            elif any(keyword in row_text for keyword in ['cereal', 'cereales']):
                return 'cereales'
            elif any(keyword in row_text for keyword in ['panqueque', 'pancake', 'tortita']):
                return 'panqueques'
                
        elif category == 'salados':
            if any(keyword in row_text for keyword in ['tostada', 'tostadas', 'toast']):
                return 'tostadas'
            elif any(keyword in row_text for keyword in ['huevo', 'huevos', 'egg']):
                return 'huevos'
            elif any(keyword in row_text for keyword in ['sandwich', 'sándwich']):
                return 'sandwiches'
            elif any(keyword in row_text for keyword in ['omelet', 'omelette', 'tortilla']):
                return 'omelettes'
            elif any(keyword in row_text for keyword in ['queso', 'cheese']):
                return 'quesos'
                
        elif category == 'colaciones':
            if any(keyword in row_text for keyword in ['fruto seco', 'frutos secos', 'nuts']):
                return 'frutos_secos'
            elif any(keyword in row_text for keyword in ['barra', 'barras', 'bar']):
                return 'barras'
            elif any(keyword in row_text for keyword in ['galleta', 'galletas', 'cookie']):
                return 'galletas'
            elif any(keyword in row_text for keyword in ['crackers', 'galletitas']):
                return 'crackers'
        
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
    
    def _parse_meal_time(self, value: str) -> Optional[str]:
        """Parse meal time from text."""
        if not value:
            return None
        
        value_lower = value.lower()
        
        if any(keyword in value_lower for keyword in ['desayuno', 'breakfast', 'mañana']):
            return 'desayuno'
        elif any(keyword in value_lower for keyword in ['media mañana', 'colación mañana']):
            return 'media_mañana'
        elif any(keyword in value_lower for keyword in ['merienda', 'tarde', 'afternoon']):
            return 'merienda'
        elif any(keyword in value_lower for keyword in ['colación tarde', 'media tarde']):
            return 'media_tarde'
        elif any(keyword in value_lower for keyword in ['noche', 'evening', 'cena']):
            return 'noche'
        
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
    
    def _determine_suitable_for(self, recipe: Dict[str, Any]) -> List[str]:
        """Determine what meal times this recipe is suitable for."""
        suitable_for = []
        
        category = recipe.get('category')
        meal_time = recipe.get('meal_time')
        
        # Add based on explicit meal time
        if meal_time:
            suitable_for.append(meal_time)
        
        # Add based on category
        if category == 'dulces':
            suitable_for.extend(['desayuno', 'merienda', 'media_mañana'])
        elif category == 'salados':
            suitable_for.extend(['desayuno', 'media_mañana'])
        elif category == 'colaciones':
            suitable_for.extend(['media_mañana', 'merienda', 'media_tarde'])
        
        # Add based on name analysis
        name = recipe.get('name', '').lower()
        if any(keyword in name for keyword in ['desayuno', 'breakfast']):
            suitable_for.append('desayuno')
        elif any(keyword in name for keyword in ['merienda', 'tarde']):
            suitable_for.append('merienda')
        elif any(keyword in name for keyword in ['colación', 'snack']):
            suitable_for.extend(['media_mañana', 'media_tarde'])
        
        # Remove duplicates
        return list(set(suitable_for))
    
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
            'category': 'desayunos_meriendas',
            'subcategory': recipe.get('category'),  # dulces, salados, colaciones
            'food_type': recipe.get('subcategory'),  # More specific type
            'ingredients': recipe.get('ingredients', []),
            'preparation': recipe.get('preparation', ''),
            'cooking_time': recipe.get('cooking_time'),
            'meal_time': recipe.get('meal_time'),
            'recipe_type': recipe.get('recipe_type'),
            'portion_size': recipe.get('portion_size'),
            'nutritional_info': recipe.get('nutritional_info', {}),
            'suitable_for': recipe.get('suitable_for', []),
            'dietary_restrictions': self._identify_dietary_restrictions(recipe),
            'tags': self._generate_tags(recipe),
            'preparation_difficulty': self._assess_difficulty(recipe)
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
        
        # Vegetarian indicators
        if not any(meat in full_text for meat in ['pollo', 'carne', 'pescado', 'cerdo', 'jamón']):
            restrictions.append('vegetariano')
        
        # Vegan indicators
        if not any(dairy in full_text for dairy in ['leche', 'queso', 'yogur', 'huevo', 'manteca']):
            restrictions.append('vegano')
        
        # Gluten-free indicators
        if not any(gluten in full_text for gluten in ['harina', 'pan', 'trigo', 'avena', 'galleta']):
            restrictions.append('sin_gluten')
        
        # Lactose-free indicators  
        if not any(dairy in full_text for dairy in ['leche', 'queso', 'yogur', 'crema', 'manteca']):
            restrictions.append('sin_lactosa')
        
        # Sugar-free indicators
        if 'sin azúcar' in full_text or 'sugar free' in full_text:
            restrictions.append('sin_azucar')
        
        return restrictions
    
    def _generate_tags(self, recipe: Dict[str, Any]) -> List[str]:
        """Generate tags for recipe categorization."""
        tags = []
        
        # Add category tags
        if recipe.get('category'):
            tags.append(recipe['category'])
        
        if recipe.get('subcategory'):
            tags.append(recipe['subcategory'])
        
        # Add meal time tags
        suitable_for = recipe.get('suitable_for', [])
        tags.extend(suitable_for)
        
        # Add cooking time tags
        cooking_time = recipe.get('cooking_time')
        if cooking_time:
            if cooking_time <= 5:
                tags.append('instantaneo')
            elif cooking_time <= 15:
                tags.append('rapido')
            else:
                tags.append('elaborado')
        
        # Add preparation tags
        preparation = recipe.get('preparation', '').lower()
        if 'licuadora' in preparation or 'batir' in preparation:
            tags.append('licuado')
        if 'cocinar' in preparation or 'hornear' in preparation:
            tags.append('cocido')
        if not preparation or 'mezclar' in preparation:
            tags.append('crudo')
        
        return tags
    
    def _assess_difficulty(self, recipe: Dict[str, Any]) -> str:
        """Assess the difficulty of the recipe."""
        preparation = recipe.get('preparation', '').lower()
        ingredients_count = len(recipe.get('ingredients', []))
        cooking_time = recipe.get('cooking_time', 0)
        
        difficulty_score = 0
        
        # Score based on ingredients count
        if ingredients_count <= 3:
            difficulty_score += 1
        elif ingredients_count <= 6:
            difficulty_score += 2
        else:
            difficulty_score += 3
        
        # Score based on cooking time
        if cooking_time <= 5:
            difficulty_score += 1
        elif cooking_time <= 15:
            difficulty_score += 2
        else:
            difficulty_score += 3
        
        # Score based on preparation complexity
        complex_words = ['hornear', 'cocinar', 'batir', 'mezclar', 'calentar']
        if any(word in preparation for word in complex_words):
            difficulty_score += 1
        
        # Return difficulty level
        if difficulty_score <= 3:
            return 'facil'
        elif difficulty_score <= 5:
            return 'medio'
        else:
            return 'dificil'