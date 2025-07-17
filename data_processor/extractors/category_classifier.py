"""
Category Classifier.
Classifies recipes and ingredients into appropriate categories.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class RecipeCategory(Enum):
    """Enum for recipe categories."""
    ALMUERZOS_CENAS = "almuerzos_cenas"
    DESAYUNOS_MERIENDAS = "desayunos_meriendas"
    EQUIVALENCIAS = "equivalencias"
    RECETAS_DETALLADAS = "recetas_detalladas"


class MealType(Enum):
    """Enum for meal types."""
    DESAYUNO = "desayuno"
    MEDIA_MANANA = "media_manana"
    ALMUERZO = "almuerzo"
    MERIENDA = "merienda"
    MEDIA_TARDE = "media_tarde"
    CENA = "cena"
    COLACION = "colacion"


class FoodCategory(Enum):
    """Enum for food categories."""
    POLLO = "pollo"
    CARNE = "carne"
    CERDO = "cerdo"
    PESCADO = "pescado"
    MARISCOS = "mariscos"
    VEGETARIANOS = "vegetarianos"
    ENSALADAS = "ensaladas"
    DULCES = "dulces"
    SALADOS = "salados"
    COLACIONES = "colaciones"


@dataclass
class Classification:
    """Represents a classification result."""
    category: str
    subcategory: Optional[str]
    confidence: float
    reasoning: List[str]
    tags: List[str]


class CategoryClassifier:
    """
    Classifies recipes and ingredients into appropriate categories.
    """
    
    def __init__(self):
        self.category_keywords = self._build_category_keywords()
        self.meal_type_keywords = self._build_meal_type_keywords()
        self.food_category_keywords = self._build_food_category_keywords()
        self.dietary_keywords = self._build_dietary_keywords()
        self.cooking_method_keywords = self._build_cooking_method_keywords()
        
    def _build_category_keywords(self) -> Dict[str, List[str]]:
        """Build keywords for main recipe categories."""
        return {
            'almuerzos_cenas': [
                'almuerzo', 'lunch', 'cena', 'dinner', 'comida', 'meal',
                'plato principal', 'main course', 'segundo plato'
            ],
            'desayunos_meriendas': [
                'desayuno', 'breakfast', 'merienda', 'snack', 'colación',
                'media mañana', 'media tarde', 'once'
            ],
            'equivalencias': [
                'equivalencia', 'equivalent', 'intercambio', 'exchange',
                'sustituto', 'substitute', 'reemplazo', 'replacement'
            ],
            'recetas_detalladas': [
                'receta', 'recipe', 'preparación', 'preparation',
                'instrucciones', 'instructions', 'paso a paso'
            ]
        }
    
    def _build_meal_type_keywords(self) -> Dict[str, List[str]]:
        """Build keywords for meal types."""
        return {
            'desayuno': [
                'desayuno', 'breakfast', 'mañana', 'morning', 'café',
                'tostada', 'cereal', 'avena', 'yogur', 'frutas'
            ],
            'media_manana': [
                'media mañana', 'mid morning', 'colación mañana',
                'snack mañana', 'entre desayuno y almuerzo'
            ],
            'almuerzo': [
                'almuerzo', 'lunch', 'comida', 'mediodía', 'noon',
                'plato principal', 'segundo plato'
            ],
            'merienda': [
                'merienda', 'afternoon snack', 'once', 'té',
                'tarde', 'afternoon'
            ],
            'media_tarde': [
                'media tarde', 'mid afternoon', 'colación tarde',
                'snack tarde', 'entre merienda y cena'
            ],
            'cena': [
                'cena', 'dinner', 'noche', 'evening', 'night',
                'último plato', 'comida nocturna'
            ],
            'colacion': [
                'colación', 'snack', 'picoteo', 'aperitivo',
                'bocadillo', 'tentempié'
            ]
        }
    
    def _build_food_category_keywords(self) -> Dict[str, List[str]]:
        """Build keywords for food categories."""
        return {
            'pollo': [
                'pollo', 'chicken', 'pechuga', 'breast', 'muslo', 'thigh',
                'ala', 'wing', 'pollo entero', 'whole chicken'
            ],
            'carne': [
                'carne', 'beef', 'res', 'vaca', 'ternera', 'veal',
                'bife', 'steak', 'asado', 'roast', 'cordero', 'lamb'
            ],
            'cerdo': [
                'cerdo', 'pork', 'chancho', 'pig', 'jamón', 'ham',
                'tocino', 'bacon', 'costilla', 'ribs'
            ],
            'pescado': [
                'pescado', 'fish', 'salmón', 'salmon', 'atún', 'tuna',
                'merluza', 'hake', 'bacalao', 'cod', 'trucha', 'trout'
            ],
            'mariscos': [
                'mariscos', 'seafood', 'camarones', 'shrimp', 'langosta', 'lobster',
                'cangrejo', 'crab', 'mejillones', 'mussels', 'almejas', 'clams'
            ],
            'vegetarianos': [
                'vegetariano', 'vegetarian', 'vegano', 'vegan', 'sin carne',
                'verduras', 'vegetables', 'legumbres', 'legumes'
            ],
            'ensaladas': [
                'ensalada', 'salad', 'verde', 'green', 'mixta', 'mixed',
                'lechuga', 'lettuce', 'rúcula', 'arugula', 'espinaca', 'spinach'
            ],
            'dulces': [
                'dulce', 'sweet', 'azúcar', 'sugar', 'miel', 'honey',
                'chocolate', 'postre', 'dessert', 'torta', 'cake'
            ],
            'salados': [
                'salado', 'salty', 'sal', 'salt', 'queso', 'cheese',
                'jamón', 'ham', 'aceitunas', 'olives'
            ],
            'colaciones': [
                'colación', 'snack', 'frutos secos', 'nuts', 'barras',
                'galletas', 'crackers', 'yogur', 'frutas'
            ]
        }
    
    def _build_dietary_keywords(self) -> Dict[str, List[str]]:
        """Build keywords for dietary restrictions."""
        return {
            'vegetariano': [
                'vegetariano', 'vegetarian', 'sin carne', 'meat-free',
                'plant-based', 'basado en plantas'
            ],
            'vegano': [
                'vegano', 'vegan', 'sin lácteos', 'dairy-free',
                'sin huevo', 'egg-free', 'sin productos animales'
            ],
            'sin_gluten': [
                'sin gluten', 'gluten-free', 'celíaco', 'celiac',
                'sin trigo', 'wheat-free', 'sin harina'
            ],
            'sin_lactosa': [
                'sin lactosa', 'lactose-free', 'intolerante lactosa',
                'sin lácteos', 'dairy-free'
            ],
            'bajo_sodio': [
                'bajo sodio', 'low sodium', 'sin sal', 'salt-free',
                'hipertensión', 'hypertension'
            ],
            'diabetico': [
                'diabético', 'diabetic', 'sin azúcar', 'sugar-free',
                'bajo carbohidratos', 'low carb'
            ],
            'light': [
                'light', 'bajo en calorías', 'low calorie',
                'reducido en grasa', 'low fat', 'diet'
            ]
        }
    
    def _build_cooking_method_keywords(self) -> Dict[str, List[str]]:
        """Build keywords for cooking methods."""
        return {
            'crudo': ['crudo', 'raw', 'fresco', 'fresh', 'sin cocción'],
            'hervido': ['hervido', 'boiled', 'cocido', 'cooked'],
            'frito': ['frito', 'fried', 'freído', 'sartén'],
            'asado': ['asado', 'roasted', 'grilled', 'parrilla'],
            'horneado': ['horneado', 'baked', 'horno', 'oven'],
            'vapor': ['vapor', 'steamed', 'al vapor', 'vaporera'],
            'guisado': ['guisado', 'stewed', 'estofado', 'cazuela'],
            'salteado': ['salteado', 'sautéed', 'saltear', 'sauté']
        }
    
    def classify_recipe(self, recipe_data: Dict[str, Any]) -> Classification:
        """Classify a recipe into appropriate category."""
        name = recipe_data.get('name', '').lower()
        description = recipe_data.get('description', '').lower()
        ingredients = recipe_data.get('ingredients', [])
        
        # Combine text for analysis
        text_content = f"{name} {description}"
        if ingredients:
            ingredients_text = ' '.join([ing.get('name', '') for ing in ingredients])
            text_content += f" {ingredients_text}"
        
        text_content = text_content.lower()
        
        # Classify main category
        main_category = self._classify_main_category(text_content)
        
        # Classify subcategory
        subcategory = self._classify_subcategory(text_content, main_category)
        
        # Generate tags
        tags = self._generate_tags(text_content, recipe_data)
        
        # Calculate confidence and reasoning
        confidence, reasoning = self._calculate_confidence_and_reasoning(
            text_content, main_category, subcategory, tags
        )
        
        return Classification(
            category=main_category,
            subcategory=subcategory,
            confidence=confidence,
            reasoning=reasoning,
            tags=tags
        )
    
    def _classify_main_category(self, text: str) -> str:
        """Classify main recipe category."""
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # Return category with highest score
        if scores:
            return max(scores, key=scores.get)
        
        return 'recetas_detalladas'  # Default category
    
    def _classify_subcategory(self, text: str, main_category: str) -> Optional[str]:
        """Classify subcategory based on main category."""
        if main_category == 'almuerzos_cenas':
            return self._classify_food_category(text)
        elif main_category == 'desayunos_meriendas':
            return self._classify_breakfast_category(text)
        elif main_category == 'equivalencias':
            return self._classify_equivalency_category(text)
        else:
            return None
    
    def _classify_food_category(self, text: str) -> Optional[str]:
        """Classify food category for lunch/dinner."""
        scores = {}
        
        for category, keywords in self.food_category_keywords.items():
            if category in ['pollo', 'carne', 'cerdo', 'pescado', 'mariscos', 'vegetarianos', 'ensaladas']:
                score = sum(1 for keyword in keywords if keyword in text)
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _classify_breakfast_category(self, text: str) -> Optional[str]:
        """Classify breakfast/snack category."""
        scores = {}
        
        for category, keywords in self.food_category_keywords.items():
            if category in ['dulces', 'salados', 'colaciones']:
                score = sum(1 for keyword in keywords if keyword in text)
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _classify_equivalency_category(self, text: str) -> Optional[str]:
        """Classify equivalency category."""
        # This could be expanded to classify different types of equivalencies
        equivalency_types = {
            'proteinas': ['proteína', 'protein', 'carne', 'pollo', 'pescado'],
            'carbohidratos': ['carbohidratos', 'carbs', 'arroz', 'pasta', 'pan'],
            'lacteos': ['lácteo', 'dairy', 'leche', 'queso', 'yogur'],
            'grasas': ['grasa', 'fat', 'aceite', 'oil', 'manteca']
        }
        
        scores = {}
        for category, keywords in equivalency_types.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _generate_tags(self, text: str, recipe_data: Dict[str, Any]) -> List[str]:
        """Generate tags for the recipe."""
        tags = []
        
        # Add dietary restriction tags
        for restriction, keywords in self.dietary_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(restriction)
        
        # Add cooking method tags
        for method, keywords in self.cooking_method_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(method)
        
        # Add meal type tags
        for meal_type, keywords in self.meal_type_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(meal_type)
        
        # Add difficulty tags
        difficulty = recipe_data.get('difficulty')
        if difficulty:
            tags.append(f"dificultad_{difficulty}")
        
        # Add time-based tags
        cooking_time = recipe_data.get('cooking_time', 0)
        if cooking_time:
            if cooking_time <= 15:
                tags.append('rapido')
            elif cooking_time <= 30:
                tags.append('medio_tiempo')
            else:
                tags.append('tiempo_largo')
        
        # Add economic level tags
        economic_level = recipe_data.get('economic_level')
        if economic_level:
            tags.append(f"economico_{economic_level}")
        
        return tags
    
    def _calculate_confidence_and_reasoning(self, text: str, main_category: str, 
                                         subcategory: Optional[str], tags: List[str]) -> Tuple[float, List[str]]:
        """Calculate confidence score and reasoning for classification."""
        confidence = 0.5  # Base confidence
        reasoning = []
        
        # Higher confidence for clear category matches
        category_keywords = self.category_keywords.get(main_category, [])
        matches = [keyword for keyword in category_keywords if keyword in text]
        if matches:
            confidence += 0.2
            reasoning.append(f"Found category keywords: {', '.join(matches)}")
        
        # Higher confidence for subcategory matches
        if subcategory:
            subcategory_keywords = self.food_category_keywords.get(subcategory, [])
            submatches = [keyword for keyword in subcategory_keywords if keyword in text]
            if submatches:
                confidence += 0.2
                reasoning.append(f"Found subcategory keywords: {', '.join(submatches)}")
        
        # Higher confidence for multiple tags
        if len(tags) > 2:
            confidence += 0.1
            reasoning.append(f"Multiple relevant tags found: {len(tags)}")
        
        # Lower confidence for ambiguous cases
        if not matches and not subcategory:
            confidence -= 0.2
            reasoning.append("Limited keyword matches found")
        
        return min(confidence, 1.0), reasoning
    
    def classify_ingredient(self, ingredient_data: Dict[str, Any]) -> Classification:
        """Classify an ingredient."""
        name = ingredient_data.get('name', '').lower()
        ingredient_type = ingredient_data.get('ingredient_type', '')
        
        # Determine main category
        main_category = self._classify_ingredient_category(name, ingredient_type)
        
        # Generate tags
        tags = self._generate_ingredient_tags(name, ingredient_data)
        
        # Calculate confidence
        confidence = 0.8 if ingredient_type else 0.6
        reasoning = [f"Ingredient type: {ingredient_type}" if ingredient_type else "No specific type identified"]
        
        return Classification(
            category=main_category,
            subcategory=ingredient_type,
            confidence=confidence,
            reasoning=reasoning,
            tags=tags
        )
    
    def _classify_ingredient_category(self, name: str, ingredient_type: str) -> str:
        """Classify ingredient into main category."""
        # Map ingredient types to categories
        type_mapping = {
            'protein': 'proteinas',
            'carbohydrate': 'carbohidratos',
            'vegetable': 'verduras',
            'fruit': 'frutas',
            'dairy': 'lacteos',
            'fat': 'grasas',
            'grain': 'cereales',
            'legume': 'legumbres',
            'spice': 'condimentos',
            'condiment': 'condimentos'
        }
        
        return type_mapping.get(ingredient_type, 'otros')
    
    def _generate_ingredient_tags(self, name: str, ingredient_data: Dict[str, Any]) -> List[str]:
        """Generate tags for an ingredient."""
        tags = []
        
        # Add dietary restriction tags
        for restriction, keywords in self.dietary_keywords.items():
            if any(keyword in name for keyword in keywords):
                tags.append(restriction)
        
        # Add preparation method tags
        preparation_method = ingredient_data.get('preparation_method')
        if preparation_method:
            tags.append(f"preparacion_{preparation_method}")
        
        # Add optional tag
        if ingredient_data.get('is_optional'):
            tags.append('opcional')
        
        return tags
    
    def classify_meal_plan(self, meal_plan_data: Dict[str, Any]) -> Classification:
        """Classify a meal plan."""
        plan_type = meal_plan_data.get('plan_type', '')
        objective = meal_plan_data.get('objective', '')
        
        # Determine main category
        main_category = 'plan_nutricional'
        
        # Determine subcategory based on objective
        subcategory = self._classify_plan_objective(objective)
        
        # Generate tags
        tags = self._generate_plan_tags(meal_plan_data)
        
        return Classification(
            category=main_category,
            subcategory=subcategory,
            confidence=0.9,
            reasoning=[f"Plan type: {plan_type}", f"Objective: {objective}"],
            tags=tags
        )
    
    def _classify_plan_objective(self, objective: str) -> str:
        """Classify plan objective."""
        objective_lower = objective.lower()
        
        if any(word in objective_lower for word in ['bajar', 'perder', 'lose', 'weight loss']):
            return 'perdida_peso'
        elif any(word in objective_lower for word in ['subir', 'ganar', 'gain', 'weight gain']):
            return 'ganancia_peso'
        elif any(word in objective_lower for word in ['mantener', 'maintain', 'maintenance']):
            return 'mantenimiento'
        elif any(word in objective_lower for word in ['definir', 'definition', 'tonificar']):
            return 'definicion'
        elif any(word in objective_lower for word in ['volumen', 'bulk', 'masa']):
            return 'volumen'
        else:
            return 'general'
    
    def _generate_plan_tags(self, meal_plan_data: Dict[str, Any]) -> List[str]:
        """Generate tags for a meal plan."""
        tags = []
        
        # Add plan type
        plan_type = meal_plan_data.get('plan_type')
        if plan_type:
            tags.append(f"tipo_{plan_type}")
        
        # Add activity level
        activity_level = meal_plan_data.get('activity_level')
        if activity_level:
            tags.append(f"actividad_{activity_level}")
        
        # Add dietary restrictions
        restrictions = meal_plan_data.get('dietary_restrictions', [])
        tags.extend(restrictions)
        
        # Add economic level
        economic_level = meal_plan_data.get('economic_level')
        if economic_level:
            tags.append(f"economico_{economic_level}")
        
        return tags
    
    def batch_classify(self, items: List[Dict[str, Any]], item_type: str) -> List[Classification]:
        """Classify multiple items at once."""
        classifications = []
        
        for item in items:
            if item_type == 'recipe':
                classification = self.classify_recipe(item)
            elif item_type == 'ingredient':
                classification = self.classify_ingredient(item)
            elif item_type == 'meal_plan':
                classification = self.classify_meal_plan(item)
            else:
                classification = Classification(
                    category='unknown',
                    subcategory=None,
                    confidence=0.0,
                    reasoning=['Unknown item type'],
                    tags=[]
                )
            
            classifications.append(classification)
        
        return classifications
    
    def export_classification(self, classification: Classification) -> Dict[str, Any]:
        """Export classification to dictionary format."""
        return {
            'category': classification.category,
            'subcategory': classification.subcategory,
            'confidence': classification.confidence,
            'reasoning': classification.reasoning,
            'tags': classification.tags
        }