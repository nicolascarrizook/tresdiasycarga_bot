"""
Parser for Recetas detalladas DOCX files.
Handles extraction of detailed recipes with step-by-step preparations.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import re

from .base_parser import BaseDocxParser

logger = logging.getLogger(__name__)


class RecetasDetalladasParser(BaseDocxParser):
    """
    Parser for detailed recipes with step-by-step instructions.
    Extracts complete recipe information including ingredients, steps, and tips.
    """
    
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.recipes = []
        self.current_recipe = None
        
    def parse(self) -> Dict[str, Any]:
        """Parse the document and extract detailed recipes."""
        self.load_document()
        
        if not self.validate_structure():
            raise ValueError("Document structure does not match expected format")
        
        # Extract recipes using a combination of tables and paragraphs
        recipes = self._extract_detailed_recipes()
        
        # Process and standardize recipes
        processed_recipes = self._process_recipes(recipes)
        
        return {
            'type': 'recetas_detalladas',
            'total_recipes': len(processed_recipes),
            'recipes': processed_recipes,
            'metadata': {
                'file_path': str(self.file_path),
                'table_count': len(self.tables),
                'paragraph_count': len(self.paragraphs)
            }
        }
    
    def validate_structure(self) -> bool:
        """Validate that the document has the expected structure."""
        if not self.tables and not self.paragraphs:
            logger.error("No tables or paragraphs found in document")
            return False
        
        # Check for recipe indicators
        paragraphs_data = self.extract_paragraphs_data()
        recipe_indicators = [
            'ingredientes', 'ingredients', 'preparación', 'preparacion',
            'instrucciones', 'instructions', 'receta', 'recipe'
        ]
        
        found_indicators = False
        for paragraph_data in paragraphs_data:
            text = paragraph_data.get('text', '').lower()
            if any(indicator in text for indicator in recipe_indicators):
                found_indicators = True
                break
        
        return found_indicators
    
    def _extract_detailed_recipes(self) -> List[Dict[str, Any]]:
        """Extract detailed recipes from the document."""
        recipes = []
        
        # Try different extraction methods
        recipes_from_tables = self._extract_recipes_from_tables()
        recipes_from_paragraphs = self._extract_recipes_from_paragraphs()
        recipes_from_mixed = self._extract_recipes_from_mixed_content()
        
        # Combine all recipes
        all_recipes = recipes_from_tables + recipes_from_paragraphs + recipes_from_mixed
        
        # Deduplicate and clean
        recipes = self._deduplicate_recipes(all_recipes)
        
        return recipes
    
    def _extract_recipes_from_tables(self) -> List[Dict[str, Any]]:
        """Extract recipes from table structures."""
        recipes = []
        tables_data = self.extract_tables_data()
        
        for table_data in tables_data:
            recipe = self._extract_recipe_from_table(table_data)
            if recipe:
                recipes.append(recipe)
        
        return recipes
    
    def _extract_recipe_from_table(self, table_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract a single recipe from a table."""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers or not rows:
            return None
        
        recipe = {
            'id': f"recipe_{table_data.get('table_index', 0)}",
            'name': '',
            'description': '',
            'ingredients': [],
            'preparation_steps': [],
            'cooking_time': None,
            'prep_time': None,
            'servings': None,
            'difficulty': None,
            'category': None,
            'tags': [],
            'nutritional_info': {},
            'tips': [],
            'variations': [],
            'source': 'table'
        }
        
        # Identify column structure
        column_mapping = self._identify_table_columns(headers)
        
        # Extract recipe data
        for row in rows:
            self._extract_data_from_row(row, column_mapping, recipe)
        
        # Post-process recipe
        self._post_process_recipe(recipe)
        
        return recipe if recipe['name'] else None
    
    def _identify_table_columns(self, headers: List[str]) -> Dict[str, int]:
        """Identify column types in recipe table."""
        column_mapping = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            if any(keyword in header_lower for keyword in ['nombre', 'receta', 'título', 'title']):
                column_mapping['name'] = i
            elif any(keyword in header_lower for keyword in ['descripción', 'descripcion', 'description']):
                column_mapping['description'] = i
            elif any(keyword in header_lower for keyword in ['ingrediente', 'ingredientes', 'ingredients']):
                column_mapping['ingredients'] = i
            elif any(keyword in header_lower for keyword in ['preparación', 'preparacion', 'instrucciones', 'pasos']):
                column_mapping['preparation'] = i
            elif any(keyword in header_lower for keyword in ['tiempo', 'duración', 'duracion']):
                column_mapping['time'] = i
            elif any(keyword in header_lower for keyword in ['porciones', 'servings', 'rinde']):
                column_mapping['servings'] = i
            elif any(keyword in header_lower for keyword in ['dificultad', 'difficulty']):
                column_mapping['difficulty'] = i
            elif any(keyword in header_lower for keyword in ['categoría', 'categoria', 'category']):
                column_mapping['category'] = i
            elif any(keyword in header_lower for keyword in ['consejos', 'tips']):
                column_mapping['tips'] = i
            elif any(keyword in header_lower for keyword in ['variaciones', 'variations']):
                column_mapping['variations'] = i
        
        return column_mapping
    
    def _extract_data_from_row(self, row: List[str], column_mapping: Dict[str, int], recipe: Dict[str, Any]) -> None:
        """Extract data from a table row into the recipe."""
        for field, col_index in column_mapping.items():
            if col_index < len(row):
                value = row[col_index]
                
                if field == 'name' and not recipe['name']:
                    recipe['name'] = self._clean_text(value)
                elif field == 'description':
                    recipe['description'] = self._clean_text(value)
                elif field == 'ingredients':
                    ingredients = self._parse_ingredients(value)
                    recipe['ingredients'].extend(ingredients)
                elif field == 'preparation':
                    steps = self._parse_preparation_steps(value)
                    recipe['preparation_steps'].extend(steps)
                elif field == 'time':
                    times = self._parse_cooking_times(value)
                    recipe.update(times)
                elif field == 'servings':
                    recipe['servings'] = self._parse_servings(value)
                elif field == 'difficulty':
                    recipe['difficulty'] = self._parse_difficulty(value)
                elif field == 'category':
                    recipe['category'] = self._clean_text(value)
                elif field == 'tips':
                    tips = self._parse_tips(value)
                    recipe['tips'].extend(tips)
                elif field == 'variations':
                    variations = self._parse_variations(value)
                    recipe['variations'].extend(variations)
    
    def _extract_recipes_from_paragraphs(self) -> List[Dict[str, Any]]:
        """Extract recipes from paragraph structures."""
        recipes = []
        paragraphs_data = self.extract_paragraphs_data()
        
        current_recipe = None
        recipe_start_indicators = ['receta', 'recipe', 'preparación de', 'cómo hacer']
        
        for paragraph_data in paragraphs_data:
            text = paragraph_data.get('text', '')
            text_lower = text.lower()
            
            # Check if this starts a new recipe
            if any(indicator in text_lower for indicator in recipe_start_indicators):
                if current_recipe:
                    recipes.append(current_recipe)
                current_recipe = self._initialize_recipe(text)
                continue
            
            # Process paragraph content if we have a current recipe
            if current_recipe:
                self._process_paragraph_content(paragraph_data, current_recipe)
        
        # Add the last recipe
        if current_recipe:
            recipes.append(current_recipe)
        
        return recipes
    
    def _initialize_recipe(self, title_text: str) -> Dict[str, Any]:
        """Initialize a new recipe structure."""
        return {
            'id': f"recipe_{len(self.recipes)}",
            'name': self._extract_recipe_name(title_text),
            'description': '',
            'ingredients': [],
            'preparation_steps': [],
            'cooking_time': None,
            'prep_time': None,
            'servings': None,
            'difficulty': None,
            'category': None,
            'tags': [],
            'nutritional_info': {},
            'tips': [],
            'variations': [],
            'source': 'paragraph'
        }
    
    def _extract_recipe_name(self, text: str) -> str:
        """Extract recipe name from title text."""
        # Remove common prefixes
        text = re.sub(r'^(receta|recipe|cómo hacer|preparación de)[\s:]+', '', text, flags=re.IGNORECASE)
        
        # Clean and return
        return self._clean_text(text)
    
    def _process_paragraph_content(self, paragraph_data: Dict[str, Any], recipe: Dict[str, Any]) -> None:
        """Process paragraph content and add to recipe."""
        text = paragraph_data.get('text', '')
        text_lower = text.lower()
        
        # Determine content type and process accordingly
        if any(keyword in text_lower for keyword in ['ingredientes', 'ingredients']):
            self._process_ingredients_paragraph(text, recipe)
        elif any(keyword in text_lower for keyword in ['preparación', 'preparacion', 'instrucciones', 'pasos']):
            self._process_preparation_paragraph(text, recipe)
        elif any(keyword in text_lower for keyword in ['tiempo', 'duración', 'duracion']):
            self._process_time_paragraph(text, recipe)
        elif any(keyword in text_lower for keyword in ['consejos', 'tips']):
            self._process_tips_paragraph(text, recipe)
        elif any(keyword in text_lower for keyword in ['variaciones', 'variations']):
            self._process_variations_paragraph(text, recipe)
        else:
            # General content - might be description or additional info
            self._process_general_paragraph(text, recipe)
    
    def _process_ingredients_paragraph(self, text: str, recipe: Dict[str, Any]) -> None:
        """Process ingredients paragraph."""
        # Remove the header
        text = re.sub(r'^(ingredientes|ingredients)[\s:]*', '', text, flags=re.IGNORECASE)
        
        ingredients = self._parse_ingredients(text)
        recipe['ingredients'].extend(ingredients)
    
    def _process_preparation_paragraph(self, text: str, recipe: Dict[str, Any]) -> None:
        """Process preparation paragraph."""
        # Remove the header
        text = re.sub(r'^(preparación|preparacion|instrucciones|pasos)[\s:]*', '', text, flags=re.IGNORECASE)
        
        steps = self._parse_preparation_steps(text)
        recipe['preparation_steps'].extend(steps)
    
    def _process_time_paragraph(self, text: str, recipe: Dict[str, Any]) -> None:
        """Process time information paragraph."""
        times = self._parse_cooking_times(text)
        recipe.update(times)
    
    def _process_tips_paragraph(self, text: str, recipe: Dict[str, Any]) -> None:
        """Process tips paragraph."""
        # Remove the header
        text = re.sub(r'^(consejos|tips)[\s:]*', '', text, flags=re.IGNORECASE)
        
        tips = self._parse_tips(text)
        recipe['tips'].extend(tips)
    
    def _process_variations_paragraph(self, text: str, recipe: Dict[str, Any]) -> None:
        """Process variations paragraph."""
        # Remove the header
        text = re.sub(r'^(variaciones|variations)[\s:]*', '', text, flags=re.IGNORECASE)
        
        variations = self._parse_variations(text)
        recipe['variations'].extend(variations)
    
    def _process_general_paragraph(self, text: str, recipe: Dict[str, Any]) -> None:
        """Process general paragraph content."""
        # If recipe doesn't have description, use this as description
        if not recipe['description'] and len(text) > 20:
            recipe['description'] = self._clean_text(text)
    
    def _extract_recipes_from_mixed_content(self) -> List[Dict[str, Any]]:
        """Extract recipes from mixed table and paragraph content."""
        recipes = []
        
        # This method combines information from nearby tables and paragraphs
        paragraphs_data = self.extract_paragraphs_data()
        tables_data = self.extract_tables_data()
        
        # Find recipe titles in paragraphs and associate with nearby tables
        for i, paragraph_data in enumerate(paragraphs_data):
            if self._is_recipe_title(paragraph_data):
                recipe = self._initialize_recipe(paragraph_data['text'])
                
                # Look for related content in nearby paragraphs and tables
                self._gather_related_content(i, paragraphs_data, tables_data, recipe)
                
                if recipe['name']:
                    recipes.append(recipe)
        
        return recipes
    
    def _is_recipe_title(self, paragraph_data: Dict[str, Any]) -> bool:
        """Check if paragraph is a recipe title."""
        text = paragraph_data.get('text', '').lower()
        is_heading = paragraph_data.get('is_heading', False)
        
        # Check for heading style or title indicators
        if is_heading:
            return True
        
        # Check for recipe title patterns
        title_patterns = [
            r'^receta\s+de\s+',
            r'^cómo\s+hacer\s+',
            r'^preparación\s+de\s+',
            r'^\w+\s+casero',
            r'^\w+\s+fácil',
            r'^\w+\s+rápido'
        ]
        
        return any(re.search(pattern, text) for pattern in title_patterns)
    
    def _gather_related_content(self, title_index: int, paragraphs_data: List[Dict[str, Any]], 
                               tables_data: List[Dict[str, Any]], recipe: Dict[str, Any]) -> None:
        """Gather content related to a recipe title."""
        # Look in following paragraphs (up to 10 paragraphs ahead)
        for i in range(title_index + 1, min(title_index + 11, len(paragraphs_data))):
            paragraph_data = paragraphs_data[i]
            
            # Stop if we find another recipe title
            if self._is_recipe_title(paragraph_data):
                break
            
            self._process_paragraph_content(paragraph_data, recipe)
        
        # Look for nearby tables (within 2 positions)
        for table_data in tables_data:
            table_index = table_data.get('table_index', 0)
            if abs(table_index - title_index) <= 2:
                self._extract_data_from_table_for_recipe(table_data, recipe)
    
    def _extract_data_from_table_for_recipe(self, table_data: Dict[str, Any], recipe: Dict[str, Any]) -> None:
        """Extract data from a table for a specific recipe."""
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        # Try to identify what this table contains
        header_text = ' '.join(headers).lower()
        
        if any(keyword in header_text for keyword in ['ingrediente', 'ingredients']):
            # This is an ingredients table
            for row in rows:
                ingredient = self._parse_ingredient_row(row)
                if ingredient:
                    recipe['ingredients'].append(ingredient)
        elif any(keyword in header_text for keyword in ['nutritional', 'nutricional']):
            # This is a nutritional information table
            nutritional_info = self._parse_nutritional_table(table_data)
            recipe['nutritional_info'].update(nutritional_info)
    
    def _parse_ingredients(self, text: str) -> List[Dict[str, Any]]:
        """Parse ingredients from text."""
        ingredients = []
        
        # Split by lines or bullet points
        lines = re.split(r'\n|•|–|-', text)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            ingredient = self._parse_single_ingredient(line)
            if ingredient:
                ingredients.append(ingredient)
        
        return ingredients
    
    def _parse_single_ingredient(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a single ingredient line."""
        if not text:
            return None
        
        # Remove common prefixes
        text = re.sub(r'^\d+\.?\s*', '', text)
        text = re.sub(r'^[-•*]\s*', '', text)
        
        # Extract quantity and unit
        portions = self.extract_portions(text)
        
        if portions:
            portion = portions[0]
            # Remove the quantity from the ingredient name
            ingredient_name = re.sub(r'^\d+(?:\.\d+)?\s*\w+\s*', '', text).strip()
            
            return {
                'name': ingredient_name,
                'quantity': portion['amount'],
                'unit': portion['unit'],
                'original_text': text,
                'notes': self._extract_ingredient_notes(text)
            }
        else:
            return {
                'name': text,
                'quantity': None,
                'unit': None,
                'original_text': text,
                'notes': self._extract_ingredient_notes(text)
            }
    
    def _extract_ingredient_notes(self, text: str) -> List[str]:
        """Extract notes from ingredient text."""
        notes = []
        
        # Look for parenthetical notes
        parenthetical = re.findall(r'\(([^)]+)\)', text)
        notes.extend(parenthetical)
        
        # Look for common qualifiers
        qualifiers = [
            'opcional', 'optional', 'al gusto', 'a gusto', 'fresco', 'fresh',
            'picado', 'rallado', 'cortado', 'pelado', 'sin semillas'
        ]
        
        for qualifier in qualifiers:
            if qualifier in text.lower():
                notes.append(qualifier)
        
        return notes
    
    def _parse_preparation_steps(self, text: str) -> List[Dict[str, Any]]:
        """Parse preparation steps from text."""
        steps = []
        
        # Split by numbered steps or paragraphs
        step_patterns = [
            r'\d+\.?\s*',  # Numbered steps
            r'Paso\s+\d+',  # "Paso 1", "Paso 2"
            r'Step\s+\d+',  # "Step 1", "Step 2"
        ]
        
        # Try to split by numbered steps first
        for pattern in step_patterns:
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 1:
                for i, part in enumerate(parts[1:], 1):  # Skip first empty part
                    step = self._parse_single_step(part.strip(), i)
                    if step:
                        steps.append(step)
                return steps
        
        # If no numbered steps found, treat as single step or split by sentences
        sentences = re.split(r'[.!?]+', text)
        for i, sentence in enumerate(sentences, 1):
            sentence = sentence.strip()
            if sentence:
                step = self._parse_single_step(sentence, i)
                if step:
                    steps.append(step)
        
        return steps
    
    def _parse_single_step(self, text: str, step_number: int) -> Optional[Dict[str, Any]]:
        """Parse a single preparation step."""
        if not text or len(text.strip()) < 5:
            return None
        
        return {
            'step_number': step_number,
            'instruction': self._clean_text(text),
            'estimated_time': self._extract_step_time(text),
            'equipment': self._extract_step_equipment(text),
            'techniques': self._extract_step_techniques(text)
        }
    
    def _extract_step_time(self, text: str) -> Optional[int]:
        """Extract time information from step text."""
        time_patterns = [
            r'(\d+)\s*min',
            r'(\d+)\s*minutos',
            r'(\d+)\s*segundos',
            r'(\d+)\s*horas?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                time_value = int(match.group(1))
                if 'hora' in pattern:
                    time_value *= 60
                elif 'segundo' in pattern:
                    time_value = max(1, time_value // 60)
                return time_value
        
        return None
    
    def _extract_step_equipment(self, text: str) -> List[str]:
        """Extract equipment mentioned in step."""
        equipment = []
        
        equipment_terms = [
            'sartén', 'olla', 'cacerola', 'horno', 'microondas', 'batidora',
            'licuadora', 'procesadora', 'cuchillo', 'tabla', 'bowl',
            'molde', 'bandeja', 'colador', 'espátula', 'cuchara'
        ]
        
        text_lower = text.lower()
        for term in equipment_terms:
            if term in text_lower:
                equipment.append(term)
        
        return equipment
    
    def _extract_step_techniques(self, text: str) -> List[str]:
        """Extract cooking techniques mentioned in step."""
        techniques = []
        
        technique_terms = [
            'freír', 'hornear', 'hervir', 'cocinar', 'mezclar', 'batir',
            'licuar', 'picar', 'cortar', 'pelar', 'rallar', 'marinar',
            'sazonar', 'condimentar', 'calentar', 'enfriar'
        ]
        
        text_lower = text.lower()
        for term in technique_terms:
            if term in text_lower:
                techniques.append(term)
        
        return techniques
    
    def _parse_cooking_times(self, text: str) -> Dict[str, Optional[int]]:
        """Parse cooking times from text."""
        times = {
            'cooking_time': None,
            'prep_time': None,
            'total_time': None
        }
        
        # Look for specific time types
        if 'preparación' in text.lower() or 'prep' in text.lower():
            times['prep_time'] = self._extract_time_value(text)
        elif 'cocción' in text.lower() or 'cooking' in text.lower():
            times['cooking_time'] = self._extract_time_value(text)
        elif 'total' in text.lower():
            times['total_time'] = self._extract_time_value(text)
        else:
            # General time - assume cooking time
            times['cooking_time'] = self._extract_time_value(text)
        
        return times
    
    def _extract_time_value(self, text: str) -> Optional[int]:
        """Extract time value in minutes."""
        time_patterns = [
            r'(\d+)\s*h(?:oras?)?',
            r'(\d+)\s*min(?:utos?)?',
            r'(\d+)\s*hrs?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                time_value = int(match.group(1))
                if 'h' in pattern:
                    time_value *= 60
                return time_value
        
        return None
    
    def _parse_servings(self, text: str) -> Optional[int]:
        """Parse servings from text."""
        servings_patterns = [
            r'(\d+)\s*porcion',
            r'(\d+)\s*serving',
            r'(\d+)\s*personas',
            r'rinde\s+(\d+)',
            r'para\s+(\d+)'
        ]
        
        for pattern in servings_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def _parse_difficulty(self, text: str) -> Optional[str]:
        """Parse difficulty level."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['fácil', 'facil', 'easy', 'simple']):
            return 'facil'
        elif any(word in text_lower for word in ['medio', 'intermedio', 'medium', 'moderado']):
            return 'medio'
        elif any(word in text_lower for word in ['difícil', 'dificil', 'hard', 'avanzado']):
            return 'dificil'
        
        return None
    
    def _parse_tips(self, text: str) -> List[str]:
        """Parse tips from text."""
        tips = []
        
        # Split by bullet points or numbers
        parts = re.split(r'[•\-\*]|\d+\.', text)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 10:
                tips.append(self._clean_text(part))
        
        return tips
    
    def _parse_variations(self, text: str) -> List[Dict[str, Any]]:
        """Parse variations from text."""
        variations = []
        
        # Split by bullet points or numbers
        parts = re.split(r'[•\-\*]|\d+\.', text)
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 10:
                variations.append({
                    'description': self._clean_text(part),
                    'type': self._classify_variation(part)
                })
        
        return variations
    
    def _classify_variation(self, text: str) -> str:
        """Classify the type of variation."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['vegetariano', 'vegano']):
            return 'dietary'
        elif any(word in text_lower for word in ['dulce', 'salado']):
            return 'flavor'
        elif any(word in text_lower for word in ['fácil', 'rápido']):
            return 'preparation'
        else:
            return 'general'
    
    def _parse_ingredient_row(self, row: List[str]) -> Optional[Dict[str, Any]]:
        """Parse an ingredient from a table row."""
        if not row or not any(row):
            return None
        
        # Assume first column is ingredient name, second is quantity
        ingredient_name = row[0].strip() if row else ''
        quantity_text = row[1].strip() if len(row) > 1 else ''
        
        if not ingredient_name:
            return None
        
        # Parse quantity
        portions = self.extract_portions(quantity_text)
        
        return {
            'name': ingredient_name,
            'quantity': portions[0]['amount'] if portions else None,
            'unit': portions[0]['unit'] if portions else None,
            'original_text': f"{ingredient_name} {quantity_text}".strip(),
            'notes': []
        }
    
    def _parse_nutritional_table(self, table_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse nutritional information from a table."""
        nutritional_info = {}
        
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        # Map headers to nutritional values
        nutrient_mapping = {
            'calorías': 'calories',
            'proteína': 'protein',
            'carbohidratos': 'carbs',
            'grasa': 'fat',
            'fibra': 'fiber'
        }
        
        for row in rows:
            if len(row) >= 2:
                nutrient_name = row[0].lower()
                value_text = row[1]
                
                for spanish_name, english_name in nutrient_mapping.items():
                    if spanish_name in nutrient_name:
                        value = self._parse_nutritional_value(value_text)
                        if value is not None:
                            nutritional_info[english_name] = value
        
        return nutritional_info
    
    def _parse_nutritional_value(self, text: str) -> Optional[float]:
        """Parse nutritional value from text."""
        if not text:
            return None
        
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        
        return None
    
    def _deduplicate_recipes(self, recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate recipes based on name similarity."""
        unique_recipes = []
        seen_names = set()
        
        for recipe in recipes:
            name = recipe.get('name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_recipes.append(recipe)
        
        return unique_recipes
    
    def _post_process_recipe(self, recipe: Dict[str, Any]) -> None:
        """Post-process recipe to clean and enhance data."""
        # Remove empty lists
        for key in ['ingredients', 'preparation_steps', 'tips', 'variations']:
            if not recipe.get(key):
                recipe[key] = []
        
        # Generate tags
        recipe['tags'] = self._generate_recipe_tags(recipe)
        
        # Estimate difficulty if not provided
        if not recipe.get('difficulty'):
            recipe['difficulty'] = self._estimate_difficulty(recipe)
    
    def _generate_recipe_tags(self, recipe: Dict[str, Any]) -> List[str]:
        """Generate tags for the recipe."""
        tags = []
        
        # Add category tag
        if recipe.get('category'):
            tags.append(recipe['category'])
        
        # Add difficulty tag
        if recipe.get('difficulty'):
            tags.append(f"dificultad_{recipe['difficulty']}")
        
        # Add time-based tags
        cooking_time = recipe.get('cooking_time', 0) or 0
        if cooking_time <= 15:
            tags.append('rapido')
        elif cooking_time <= 30:
            tags.append('medio_tiempo')
        elif cooking_time > 60:
            tags.append('tiempo_largo')
        
        # Add ingredient-based tags
        ingredients_text = ' '.join([ing.get('name', '') for ing in recipe.get('ingredients', [])])
        if 'vegetariano' in ingredients_text.lower():
            tags.append('vegetariano')
        
        return tags
    
    def _estimate_difficulty(self, recipe: Dict[str, Any]) -> str:
        """Estimate difficulty based on recipe complexity."""
        score = 0
        
        # Score based on number of ingredients
        ingredient_count = len(recipe.get('ingredients', []))
        if ingredient_count > 10:
            score += 2
        elif ingredient_count > 5:
            score += 1
        
        # Score based on number of steps
        step_count = len(recipe.get('preparation_steps', []))
        if step_count > 8:
            score += 2
        elif step_count > 4:
            score += 1
        
        # Score based on cooking time
        cooking_time = recipe.get('cooking_time', 0) or 0
        if cooking_time > 60:
            score += 2
        elif cooking_time > 30:
            score += 1
        
        # Score based on techniques used
        techniques = []
        for step in recipe.get('preparation_steps', []):
            techniques.extend(step.get('techniques', []))
        
        if len(set(techniques)) > 5:
            score += 2
        elif len(set(techniques)) > 3:
            score += 1
        
        # Return difficulty level
        if score <= 2:
            return 'facil'
        elif score <= 4:
            return 'medio'
        else:
            return 'dificil'
    
    def _process_recipes(self, recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and standardize all recipes."""
        processed_recipes = []
        
        for recipe in recipes:
            processed_recipe = self._standardize_recipe(recipe)
            if processed_recipe:
                processed_recipes.append(processed_recipe)
        
        return processed_recipes
    
    def _standardize_recipe(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize recipe format."""
        return {
            'id': recipe.get('id'),
            'name': recipe.get('name', '').strip(),
            'description': recipe.get('description', ''),
            'category': 'recetas_detalladas',
            'subcategory': recipe.get('category'),
            'ingredients': recipe.get('ingredients', []),
            'preparation_steps': recipe.get('preparation_steps', []),
            'cooking_time': recipe.get('cooking_time'),
            'prep_time': recipe.get('prep_time'),
            'total_time': recipe.get('total_time'),
            'servings': recipe.get('servings'),
            'difficulty': recipe.get('difficulty'),
            'nutritional_info': recipe.get('nutritional_info', {}),
            'tags': recipe.get('tags', []),
            'tips': recipe.get('tips', []),
            'variations': recipe.get('variations', []),
            'source': recipe.get('source'),
            'equipment_needed': self._extract_equipment_needed(recipe),
            'techniques_used': self._extract_techniques_used(recipe)
        }
    
    def _extract_equipment_needed(self, recipe: Dict[str, Any]) -> List[str]:
        """Extract all equipment needed for the recipe."""
        equipment = set()
        
        for step in recipe.get('preparation_steps', []):
            equipment.update(step.get('equipment', []))
        
        return list(equipment)
    
    def _extract_techniques_used(self, recipe: Dict[str, Any]) -> List[str]:
        """Extract all techniques used in the recipe."""
        techniques = set()
        
        for step in recipe.get('preparation_steps', []):
            techniques.update(step.get('techniques', []))
        
        return list(techniques)