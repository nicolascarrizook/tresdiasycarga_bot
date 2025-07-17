"""
Ingredient List Extractor.
Extracts and processes ingredient information from recipe content.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IngredientType(Enum):
    """Enum for ingredient types."""
    PROTEIN = "protein"
    CARBOHYDRATE = "carbohydrate"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    DAIRY = "dairy"
    FAT = "fat"
    SPICE = "spice"
    CONDIMENT = "condiment"
    GRAIN = "grain"
    LEGUME = "legume"
    LIQUID = "liquid"
    OTHER = "other"


@dataclass
class Ingredient:
    """Represents an ingredient with all its properties."""
    name: str
    quantity: Optional[float]
    unit: Optional[str]
    original_text: str
    ingredient_type: IngredientType
    preparation_method: Optional[str]
    notes: List[str]
    confidence: float
    alternatives: List[str]
    nutritional_category: Optional[str]
    is_optional: bool


class IngredientExtractor:
    """
    Extracts and processes ingredient information from recipe text.
    Handles various formats and provides standardized ingredient data.
    """
    
    def __init__(self):
        self.quantity_patterns = self._build_quantity_patterns()
        self.unit_patterns = self._build_unit_patterns()
        self.ingredient_types = self._build_ingredient_types()
        self.preparation_methods = self._build_preparation_methods()
        self.alternative_indicators = self._build_alternative_indicators()
        
    def _build_quantity_patterns(self) -> List[str]:
        """Build regex patterns for quantity extraction."""
        return [
            r'(\d+(?:\.\d+)?)\s*½',  # 1½, 2½
            r'(\d+(?:\.\d+)?)\s*¼',  # 1¼, 2¼
            r'(\d+(?:\.\d+)?)\s*¾',  # 1¾, 2¾
            r'(\d+(?:\.\d+)?)\s*/',  # 1/2, 3/4
            r'(\d+(?:\.\d+)?)',      # Regular numbers
            r'½',                    # Half
            r'¼',                    # Quarter
            r'¾',                    # Three quarters
            r'una?\s+',              # "una" or "un"
            r'dos\s+',               # "dos"
            r'tres\s+',              # "tres"
            r'cuatro\s+',            # "cuatro"
            r'cinco\s+',             # "cinco"
            r'media\s+',             # "media"
            r'medio\s+',             # "medio"
            r'un\s+poco\s+de',       # "un poco de"
            r'una\s+pizca\s+de',     # "una pizca de"
            r'al\s+gusto',           # "al gusto"
            r'a\s+gusto'             # "a gusto"
        ]
    
    def _build_unit_patterns(self) -> Dict[str, List[str]]:
        """Build unit patterns by category."""
        return {
            'weight': [
                r'kg|kilogramos?|kilo',
                r'g|gr|gramos?',
                r'mg|miligramos?',
                r'libra|libras|lb|lbs',
                r'onza|onzas|oz'
            ],
            'volume': [
                r'l|lt|litros?',
                r'ml|cc|mililitros?',
                r'taza|tazas|cup|cups',
                r'cucharada|cucharadas|cda|cdas|tbsp|cucharadita|cucharaditas|cdita|cditas|tsp',
                r'vaso|vasos|copa|copas',
                r'pinta|pintas'
            ],
            'unit': [
                r'unidad|unidades|u|ud',
                r'pieza|piezas|pza',
                r'diente|dientes',
                r'rodaja|rodajas|slice|slices',
                r'hoja|hojas',
                r'rama|ramas',
                r'cabeza|cabezas',
                r'manojo|manojos',
                r'racimo|racimos'
            ],
            'container': [
                r'lata|latas|can|cans',
                r'paquete|paquetes|pack|packs',
                r'sobre|sobres|sachet|sachets',
                r'frasco|frascos|jar|jars',
                r'botella|botellas|bottle|bottles'
            ]
        }
    
    def _build_ingredient_types(self) -> Dict[str, List[str]]:
        """Build ingredient type classifications."""
        return {
            IngredientType.PROTEIN.value: [
                'pollo', 'chicken', 'carne', 'beef', 'res', 'cerdo', 'pork', 'cordero', 'lamb',
                'pescado', 'fish', 'salmón', 'salmon', 'atún', 'atun', 'tuna', 'merluza',
                'huevo', 'huevos', 'egg', 'eggs', 'clara', 'claras', 'yema', 'yemas',
                'jamón', 'jamon', 'ham', 'salchicha', 'salchichas', 'sausage'
            ],
            IngredientType.CARBOHYDRATE.value: [
                'arroz', 'rice', 'pasta', 'fideos', 'noodles', 'pan', 'bread', 'harina', 'flour',
                'papa', 'papas', 'potato', 'potatoes', 'batata', 'sweet potato', 'avena', 'oats',
                'quinoa', 'kinoa', 'bulgur', 'cebada', 'barley', 'polenta', 'maíz', 'corn',
                'cereales', 'cereals', 'galletas', 'crackers', 'tostadas', 'toast'
            ],
            IngredientType.VEGETABLE.value: [
                'tomate', 'tomato', 'cebolla', 'onion', 'ajo', 'garlic', 'zanahoria', 'carrot',
                'apio', 'celery', 'pimiento', 'pepper', 'brócoli', 'broccoli', 'coliflor', 'cauliflower',
                'espinaca', 'spinach', 'lechuga', 'lettuce', 'pepino', 'cucumber', 'rúcula', 'arugula',
                'puerro', 'leek', 'berenjena', 'eggplant', 'calabaza', 'pumpkin', 'zucchini',
                'choclo', 'corn', 'arvejas', 'peas', 'chauchas', 'green beans'
            ],
            IngredientType.FRUIT.value: [
                'manzana', 'apple', 'banana', 'plátano', 'naranja', 'orange', 'limón', 'lemon',
                'lima', 'lime', 'frutilla', 'strawberry', 'uva', 'grape', 'pera', 'pear',
                'durazno', 'peach', 'damasco', 'apricot', 'ciruela', 'plum', 'kiwi',
                'mango', 'palta', 'avocado', 'ananá', 'pineapple', 'melón', 'melon',
                'sandía', 'watermelon', 'arándano', 'blueberry', 'frambuesa', 'raspberry'
            ],
            IngredientType.DAIRY.value: [
                'leche', 'milk', 'yogur', 'yogurt', 'queso', 'cheese', 'crema', 'cream',
                'manteca', 'butter', 'ricota', 'ricotta', 'mozzarella', 'parmesano', 'parmesan',
                'cheddar', 'roquefort', 'camembert', 'brie', 'suero', 'whey',
                'dulce de leche', 'crema de leche', 'leche condensada'
            ],
            IngredientType.FAT.value: [
                'aceite', 'oil', 'oliva', 'olive', 'girasol', 'sunflower', 'maíz', 'corn',
                'manteca', 'butter', 'margarina', 'margarine', 'palta', 'avocado',
                'nuez', 'nuts', 'almendra', 'almond', 'maní', 'peanut', 'sésamo', 'sesame',
                'chía', 'chia', 'lino', 'flax', 'coco', 'coconut'
            ],
            IngredientType.SPICE.value: [
                'sal', 'salt', 'pimienta', 'pepper', 'orégano', 'oregano', 'albahaca', 'basil',
                'perejil', 'parsley', 'cilantro', 'coriander', 'tomillo', 'thyme', 'romero', 'rosemary',
                'laurel', 'bay', 'comino', 'cumin', 'pimentón', 'paprika', 'curry', 'canela', 'cinnamon',
                'nuez moscada', 'nutmeg', 'jengibre', 'ginger', 'ajo en polvo', 'garlic powder',
                'cebolla en polvo', 'onion powder', 'chile', 'chili', 'ají', 'hot pepper'
            ],
            IngredientType.CONDIMENT.value: [
                'vinagre', 'vinegar', 'mostaza', 'mustard', 'ketchup', 'mayonesa', 'mayonnaise',
                'salsa', 'sauce', 'soja', 'soy', 'worcestershire', 'tabasco', 'sriracha',
                'miel', 'honey', 'azúcar', 'sugar', 'edulcorante', 'sweetener', 'stevia',
                'vainilla', 'vanilla', 'esencia', 'essence', 'extracto', 'extract'
            ],
            IngredientType.GRAIN.value: [
                'arroz', 'rice', 'trigo', 'wheat', 'avena', 'oats', 'cebada', 'barley',
                'centeno', 'rye', 'quinoa', 'kinoa', 'amaranto', 'amaranth', 'mijo', 'millet',
                'bulgur', 'sémola', 'semolina', 'polenta', 'harina', 'flour'
            ],
            IngredientType.LEGUME.value: [
                'lenteja', 'lentil', 'garbanzo', 'chickpea', 'poroto', 'bean', 'arveja', 'pea',
                'soja', 'soy', 'maní', 'peanut', 'habas', 'fava', 'judías', 'kidney'
            ],
            IngredientType.LIQUID.value: [
                'agua', 'water', 'caldo', 'broth', 'stock', 'jugo', 'juice', 'vino', 'wine',
                'cerveza', 'beer', 'leche', 'milk', 'crema', 'cream', 'café', 'coffee',
                'té', 'tea', 'infusión', 'infusion'
            ]
        }
    
    def _build_preparation_methods(self) -> List[str]:
        """Build preparation method patterns."""
        return [
            'picado', 'picada', 'chopped', 'cortado', 'cortada', 'cut',
            'rallado', 'rallada', 'grated', 'pelado', 'pelada', 'peeled',
            'rebanado', 'rebanada', 'sliced', 'cubeteado', 'cubeteada', 'diced',
            'molido', 'molida', 'ground', 'triturado', 'triturada', 'crushed',
            'machacado', 'machacada', 'mashed', 'licuado', 'licuada', 'blended',
            'batido', 'batida', 'beaten', 'mezclado', 'mezclada', 'mixed',
            'cocido', 'cocida', 'cooked', 'crudo', 'cruda', 'raw',
            'asado', 'asada', 'roasted', 'hervido', 'hervida', 'boiled',
            'frito', 'frita', 'fried', 'al vapor', 'steamed', 'marinado', 'marinada', 'marinated',
            'desmenuzado', 'desmenuzada', 'shredded', 'en juliana', 'julienned',
            'en daditos', 'diced', 'en trozos', 'chunked', 'en rodajas', 'sliced',
            'sin semillas', 'seedless', 'sin piel', 'skinless', 'sin hueso', 'boneless',
            'fresco', 'fresca', 'fresh', 'seco', 'seca', 'dry', 'dried',
            'congelado', 'congelada', 'frozen', 'enlatado', 'enlatada', 'canned',
            'embotellado', 'embotellada', 'bottled', 'en conserva', 'preserved'
        ]
    
    def _build_alternative_indicators(self) -> List[str]:
        """Build alternative ingredient indicators."""
        return [
            'o', 'or', 'u', 'también', 'tambien', 'alternativamente',
            'en su defecto', 'en lugar de', 'instead of', 'substitute',
            'reemplazar por', 'replace with', 'si no tienes', 'if you don\\'t have'
        ]
    
    def extract_from_text(self, text: str) -> List[Ingredient]:
        """Extract ingredients from text."""
        if not text:
            return []
        
        # Clean and prepare text
        text = self._clean_text(text)
        
        # Split into lines
        lines = self._split_into_lines(text)
        
        # Extract ingredients from each line
        ingredients = []
        for line in lines:
            ingredient = self._extract_ingredient_from_line(line)
            if ingredient:
                ingredients.append(ingredient)
        
        return ingredients
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove common headers
        text = re.sub(r'^(ingredientes|ingredients)[\s:]*', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra punctuation
        text = re.sub(r'[•\-\*]+\s*', '', text)
        
        return text.strip()
    
    def _split_into_lines(self, text: str) -> List[str]:
        """Split text into ingredient lines."""
        # Split by common delimiters
        lines = re.split(r'[,\n]|(?=\d+\.)', text)
        
        # Clean each line
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                # Remove numbering
                line = re.sub(r'^\d+\.?\s*', '', line)
                # Remove bullet points
                line = re.sub(r'^[•\-\*]\s*', '', line)
                cleaned_lines.append(line)
        
        return cleaned_lines
    
    def _extract_ingredient_from_line(self, line: str) -> Optional[Ingredient]:
        """Extract ingredient information from a single line."""
        if not line:
            return None
        
        # Extract quantity and unit
        quantity, unit, remaining_text = self._extract_quantity_and_unit(line)
        
        # Extract ingredient name
        ingredient_name = self._extract_ingredient_name(remaining_text)
        
        if not ingredient_name:
            return None
        
        # Extract preparation method
        preparation_method = self._extract_preparation_method(remaining_text)
        
        # Extract notes
        notes = self._extract_notes(remaining_text)
        
        # Check if optional
        is_optional = self._is_optional(remaining_text)
        
        # Extract alternatives
        alternatives = self._extract_alternatives(remaining_text)
        
        # Classify ingredient type
        ingredient_type = self._classify_ingredient_type(ingredient_name)
        
        # Determine nutritional category
        nutritional_category = self._determine_nutritional_category(ingredient_type)
        
        # Calculate confidence
        confidence = self._calculate_confidence(line, quantity, unit, ingredient_name)
        
        return Ingredient(
            name=ingredient_name,
            quantity=quantity,
            unit=unit,
            original_text=line,
            ingredient_type=ingredient_type,
            preparation_method=preparation_method,
            notes=notes,
            confidence=confidence,
            alternatives=alternatives,
            nutritional_category=nutritional_category,
            is_optional=is_optional
        )
    
    def _extract_quantity_and_unit(self, text: str) -> Tuple[Optional[float], Optional[str], str]:
        """Extract quantity and unit from text."""
        # Try to find quantity patterns
        for pattern in self.quantity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quantity_text = match.group(0)
                quantity = self._parse_quantity(quantity_text)
                
                # Remove quantity from text
                remaining_text = text.replace(quantity_text, '', 1).strip()
                
                # Look for unit after quantity
                unit = self._extract_unit(remaining_text)
                
                # Remove unit from remaining text
                if unit:
                    remaining_text = re.sub(rf'^{re.escape(unit)}\s*', '', remaining_text, flags=re.IGNORECASE)
                
                return quantity, unit, remaining_text
        
        # No quantity found
        return None, None, text
    
    def _parse_quantity(self, quantity_text: str) -> Optional[float]:
        """Parse quantity from text."""
        quantity_text = quantity_text.lower().strip()
        
        # Handle fractions
        if '½' in quantity_text:
            base = re.sub(r'½', '', quantity_text)
            base_val = float(base) if base and base.isdigit() else 0
            return base_val + 0.5
        elif '¼' in quantity_text:
            base = re.sub(r'¼', '', quantity_text)
            base_val = float(base) if base and base.isdigit() else 0
            return base_val + 0.25
        elif '¾' in quantity_text:
            base = re.sub(r'¾', '', quantity_text)
            base_val = float(base) if base and base.isdigit() else 0
            return base_val + 0.75
        elif '/' in quantity_text:
            # Handle fractions like 1/2, 3/4
            parts = quantity_text.split('/')
            if len(parts) == 2:
                try:
                    numerator = float(parts[0])
                    denominator = float(parts[1])
                    return numerator / denominator
                except ValueError:
                    pass
        
        # Handle word quantities
        word_quantities = {
            'una': 1, 'un': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,
            'media': 0.5, 'medio': 0.5, 'un poco': 0.1, 'una pizca': 0.05,
            'al gusto': None, 'a gusto': None
        }
        
        for word, value in word_quantities.items():
            if word in quantity_text:
                return value
        
        # Try to extract numeric value
        match = re.search(r'(\d+(?:\.\d+)?)', quantity_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _extract_unit(self, text: str) -> Optional[str]:
        """Extract unit from text."""
        text_lower = text.lower()
        
        # Check all unit categories
        for category, patterns in self.unit_patterns.items():
            for pattern in patterns:
                match = re.search(rf'^({pattern})\b', text_lower)
                if match:
                    return match.group(1)
        
        return None
    
    def _extract_ingredient_name(self, text: str) -> str:
        """Extract ingredient name from text."""
        # Remove preparation methods and notes
        text = re.sub(r'\([^)]*\)', '', text)  # Remove parentheses
        
        # Remove preparation method words
        for prep_method in self.preparation_methods:
            text = re.sub(rf'\b{prep_method}\b', '', text, flags=re.IGNORECASE)
        
        # Remove alternative indicators
        for indicator in self.alternative_indicators:
            text = re.sub(rf'\b{indicator}\b.*$', '', text, flags=re.IGNORECASE)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove leading/trailing commas and periods
        text = text.strip('.,')
        
        return text
    
    def _extract_preparation_method(self, text: str) -> Optional[str]:
        """Extract preparation method from text."""
        text_lower = text.lower()
        
        for method in self.preparation_methods:
            if method in text_lower:
                return method
        
        return None
    
    def _extract_notes(self, text: str) -> List[str]:
        """Extract notes from text."""
        notes = []
        
        # Extract parenthetical notes
        parenthetical = re.findall(r'\(([^)]+)\)', text)
        notes.extend(parenthetical)
        
        # Extract common qualifiers
        qualifiers = [
            'fresco', 'fresh', 'seco', 'dry', 'congelado', 'frozen',
            'enlatado', 'canned', 'orgánico', 'organic', 'natural',
            'sin azúcar', 'sugar-free', 'light', 'descremado', 'low-fat',
            'integral', 'whole', 'refinado', 'refined', 'crudo', 'raw',
            'cocido', 'cooked', 'maduro', 'ripe', 'tierno', 'tender',
            'salado', 'salty', 'dulce', 'sweet', 'amargo', 'bitter',
            'picante', 'spicy', 'suave', 'mild', 'fuerte', 'strong'
        ]
        
        text_lower = text.lower()
        for qualifier in qualifiers:
            if qualifier in text_lower:
                notes.append(qualifier)
        
        return notes
    
    def _is_optional(self, text: str) -> bool:
        """Check if ingredient is optional."""
        optional_indicators = [
            'opcional', 'optional', 'al gusto', 'a gusto', 'si se desea',
            'if desired', 'si tienes', 'if you have', 'puede omitirse',
            'can be omitted', 'no es necesario', 'not necessary'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in optional_indicators)
    
    def _extract_alternatives(self, text: str) -> List[str]:
        """Extract alternative ingredients."""
        alternatives = []
        
        # Look for alternative indicators
        for indicator in self.alternative_indicators:
            if indicator in text.lower():
                # Extract text after indicator
                parts = re.split(rf'\b{indicator}\b', text, flags=re.IGNORECASE)
                if len(parts) > 1:
                    alt_text = parts[1].strip()
                    # Clean and add as alternative
                    alt_text = self._clean_alternative_text(alt_text)
                    if alt_text:
                        alternatives.append(alt_text)
        
        return alternatives
    
    def _clean_alternative_text(self, text: str) -> str:
        """Clean alternative ingredient text."""
        # Remove common separators
        text = re.split(r'[,;]', text)[0].strip()
        
        # Remove preparation methods
        for method in self.preparation_methods:
            text = re.sub(rf'\b{method}\b', '', text, flags=re.IGNORECASE)
        
        # Clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _classify_ingredient_type(self, ingredient_name: str) -> IngredientType:
        """Classify ingredient type."""
        ingredient_lower = ingredient_name.lower()
        
        # Check each ingredient type
        for ingredient_type, keywords in self.ingredient_types.items():
            if any(keyword in ingredient_lower for keyword in keywords):
                return IngredientType(ingredient_type)
        
        return IngredientType.OTHER
    
    def _determine_nutritional_category(self, ingredient_type: IngredientType) -> Optional[str]:
        """Determine nutritional category."""
        category_mapping = {
            IngredientType.PROTEIN: 'proteina',
            IngredientType.CARBOHYDRATE: 'carbohidrato',
            IngredientType.VEGETABLE: 'verdura',
            IngredientType.FRUIT: 'fruta',
            IngredientType.DAIRY: 'lacteo',
            IngredientType.FAT: 'grasa',
            IngredientType.GRAIN: 'cereal',
            IngredientType.LEGUME: 'legumbre'
        }
        
        return category_mapping.get(ingredient_type)
    
    def _calculate_confidence(self, line: str, quantity: Optional[float], 
                            unit: Optional[str], ingredient_name: str) -> float:
        """Calculate confidence score for extraction."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if we found quantity
        if quantity is not None:
            confidence += 0.2
        
        # Higher confidence if we found unit
        if unit:
            confidence += 0.2
        
        # Higher confidence if ingredient name is not too short
        if len(ingredient_name) > 3:
            confidence += 0.1
        
        # Higher confidence if line is well-structured
        if ',' in line or '(' in line:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def extract_from_table(self, table_data: Dict[str, Any]) -> List[Ingredient]:
        """Extract ingredients from table data."""
        ingredients = []
        
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers or not rows:
            return ingredients
        
        # Identify column structure
        column_mapping = self._identify_table_columns(headers)
        
        for row in rows:
            if len(row) >= len(headers):
                ingredient = self._extract_ingredient_from_row(row, column_mapping)
                if ingredient:
                    ingredients.append(ingredient)
        
        return ingredients
    
    def _identify_table_columns(self, headers: List[str]) -> Dict[str, int]:
        """Identify column types in ingredient table."""
        column_mapping = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            if any(keyword in header_lower for keyword in ['ingrediente', 'ingredient', 'nombre']):
                column_mapping['name'] = i
            elif any(keyword in header_lower for keyword in ['cantidad', 'quantity', 'porción']):
                column_mapping['quantity'] = i
            elif any(keyword in header_lower for keyword in ['unidad', 'unit', 'medida']):
                column_mapping['unit'] = i
            elif any(keyword in header_lower for keyword in ['preparación', 'preparation', 'método']):
                column_mapping['preparation'] = i
            elif any(keyword in header_lower for keyword in ['notas', 'notes', 'observaciones']):
                column_mapping['notes'] = i
        
        return column_mapping
    
    def _extract_ingredient_from_row(self, row: List[str], column_mapping: Dict[str, int]) -> Optional[Ingredient]:
        """Extract ingredient from table row."""
        if not row:
            return None
        
        # Extract name
        name_col = column_mapping.get('name', 0)
        ingredient_name = row[name_col].strip() if name_col < len(row) else ''
        
        if not ingredient_name:
            return None
        
        # Extract quantity
        quantity = None
        quantity_col = column_mapping.get('quantity')
        if quantity_col is not None and quantity_col < len(row):
            quantity_text = row[quantity_col].strip()
            quantity = self._parse_quantity(quantity_text)
        
        # Extract unit
        unit = None
        unit_col = column_mapping.get('unit')
        if unit_col is not None and unit_col < len(row):
            unit = row[unit_col].strip() or None
        
        # Extract preparation method
        preparation_method = None
        prep_col = column_mapping.get('preparation')
        if prep_col is not None and prep_col < len(row):
            preparation_method = row[prep_col].strip() or None
        
        # Extract notes
        notes = []
        notes_col = column_mapping.get('notes')
        if notes_col is not None and notes_col < len(row):
            notes_text = row[notes_col].strip()
            if notes_text:
                notes = [notes_text]
        
        # Classify ingredient type
        ingredient_type = self._classify_ingredient_type(ingredient_name)
        
        # Determine nutritional category
        nutritional_category = self._determine_nutritional_category(ingredient_type)
        
        # Create full text for confidence calculation
        full_text = ' '.join(row)
        
        return Ingredient(
            name=ingredient_name,
            quantity=quantity,
            unit=unit,
            original_text=full_text,
            ingredient_type=ingredient_type,
            preparation_method=preparation_method,
            notes=notes,
            confidence=0.8,  # Higher confidence for table data
            alternatives=[],
            nutritional_category=nutritional_category,
            is_optional=False
        )
    
    def standardize_ingredients(self, ingredients: List[Ingredient]) -> List[Dict[str, Any]]:
        """Standardize ingredients to common format."""
        standardized = []
        
        for ingredient in ingredients:
            standardized_ingredient = {
                'name': ingredient.name,
                'quantity': ingredient.quantity,
                'unit': ingredient.unit,
                'ingredient_type': ingredient.ingredient_type.value,
                'preparation_method': ingredient.preparation_method,
                'notes': ingredient.notes,
                'alternatives': ingredient.alternatives,
                'nutritional_category': ingredient.nutritional_category,
                'is_optional': ingredient.is_optional,
                'confidence': ingredient.confidence,
                'original_text': ingredient.original_text
            }
            standardized.append(standardized_ingredient)
        
        return standardized
    
    def group_by_type(self, ingredients: List[Ingredient]) -> Dict[str, List[Ingredient]]:
        """Group ingredients by type."""
        grouped = {}
        
        for ingredient in ingredients:
            ingredient_type = ingredient.ingredient_type.value
            if ingredient_type not in grouped:
                grouped[ingredient_type] = []
            grouped[ingredient_type].append(ingredient)
        
        return grouped
    
    def validate_ingredients(self, ingredients: List[Ingredient]) -> Dict[str, Any]:
        """Validate ingredient list."""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        if not ingredients:
            validation_results['errors'].append("No ingredients found")
            validation_results['is_valid'] = False
            return validation_results
        
        # Check for ingredients without names
        unnamed_count = sum(1 for ing in ingredients if not ing.name.strip())
        if unnamed_count > 0:
            validation_results['warnings'].append(f"{unnamed_count} ingredients without names")
        
        # Check for very low confidence ingredients
        low_confidence = [ing for ing in ingredients if ing.confidence < 0.3]
        if low_confidence:
            validation_results['warnings'].append(f"{len(low_confidence)} ingredients with low confidence")
        
        # Check for duplicate ingredients
        names = [ing.name.lower() for ing in ingredients]
        duplicates = set([name for name in names if names.count(name) > 1])
        if duplicates:
            validation_results['warnings'].append(f"Duplicate ingredients: {', '.join(duplicates)}")
        
        return validation_results
    
    def export_to_dict(self, ingredients: List[Ingredient]) -> List[Dict[str, Any]]:
        """Export ingredients to dictionary format."""
        return [
            {
                'name': ing.name,
                'quantity': ing.quantity,
                'unit': ing.unit,
                'ingredient_type': ing.ingredient_type.value,
                'preparation_method': ing.preparation_method,
                'notes': ing.notes,
                'alternatives': ing.alternatives,
                'nutritional_category': ing.nutritional_category,
                'is_optional': ing.is_optional,
                'confidence': ing.confidence,
                'original_text': ing.original_text
            }
            for ing in ingredients
        ]