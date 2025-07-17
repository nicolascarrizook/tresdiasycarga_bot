"""
Preparation Steps Extractor.
Extracts and processes preparation steps from recipe content.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class StepType(Enum):
    """Enum for step types."""
    PREPARATION = "preparation"
    COOKING = "cooking"
    MIXING = "mixing"
    SEASONING = "seasoning"
    ASSEMBLY = "assembly"
    SERVING = "serving"
    CLEANUP = "cleanup"


class CookingMethod(Enum):
    """Enum for cooking methods."""
    BOILING = "boiling"
    FRYING = "frying"
    BAKING = "baking"
    GRILLING = "grilling"
    STEAMING = "steaming"
    ROASTING = "roasting"
    SAUTEING = "sauteing"
    BRAISING = "braising"
    STEWING = "stewing"
    BLANCHING = "blanching"
    POACHING = "poaching"
    MARINATING = "marinating"
    NONE = "none"


@dataclass
class PreparationStep:
    """Represents a preparation step with all its properties."""
    step_number: int
    instruction: str
    step_type: StepType
    cooking_method: CookingMethod
    estimated_time: Optional[int]
    temperature: Optional[int]
    equipment: List[str]
    techniques: List[str]
    ingredients_mentioned: List[str]
    safety_notes: List[str]
    tips: List[str]
    original_text: str
    confidence: float


class PreparationExtractor:
    """
    Extracts and processes preparation steps from recipe text.
    Handles various formats and provides structured step data.
    """
    
    def __init__(self):
        self.step_indicators = self._build_step_indicators()
        self.cooking_methods = self._build_cooking_methods()
        self.equipment_terms = self._build_equipment_terms()
        self.technique_terms = self._build_technique_terms()
        self.time_patterns = self._build_time_patterns()
        self.temperature_patterns = self._build_temperature_patterns()
        self.safety_keywords = self._build_safety_keywords()
        self.tip_indicators = self._build_tip_indicators()
        
    def _build_step_indicators(self) -> List[str]:
        """Build step indicator patterns."""
        return [
            r'^\d+\.?\s*',               # 1., 2., 3.
            r'^paso\s*\d+[\s:]*',        # Paso 1:, Paso 2:
            r'^step\s*\d+[\s:]*',        # Step 1:, Step 2:
            r'^primero[\s:]*',           # Primero:
            r'^segundo[\s:]*',           # Segundo:
            r'^tercero[\s:]*',           # Tercero:
            r'^luego[\s:]*',             # Luego:
            r'^después[\s:]*',           # Después:
            r'^finalmente[\s:]*',        # Finalmente:
            r'^para\s*terminar[\s:]*',   # Para terminar:
            r'^a\s*continuación[\s:]*',  # A continuación:
            r'^mientras\s*tanto[\s:]*'   # Mientras tanto:
        ]
    
    def _build_cooking_methods(self) -> Dict[str, CookingMethod]:
        """Build cooking method keywords."""
        return {
            'hervir': CookingMethod.BOILING,
            'boil': CookingMethod.BOILING,
            'cocinar': CookingMethod.COOKING,
            'freír': CookingMethod.FRYING,
            'fry': CookingMethod.FRYING,
            'hornear': CookingMethod.BAKING,
            'bake': CookingMethod.BAKING,
            'asar': CookingMethod.GRILLING,
            'grill': CookingMethod.GRILLING,
            'vapor': CookingMethod.STEAMING,
            'steam': CookingMethod.STEAMING,
            'rostizar': CookingMethod.ROASTING,
            'roast': CookingMethod.ROASTING,
            'saltear': CookingMethod.SAUTEING,
            'sauté': CookingMethod.SAUTEING,
            'brasear': CookingMethod.BRAISING,
            'braise': CookingMethod.BRAISING,
            'guisar': CookingMethod.STEWING,
            'stew': CookingMethod.STEWING,
            'blanquear': CookingMethod.BLANCHING,
            'blanch': CookingMethod.BLANCHING,
            'pochear': CookingMethod.POACHING,
            'poach': CookingMethod.POACHING,
            'marinar': CookingMethod.MARINATING,
            'marinate': CookingMethod.MARINATING
        }
    
    def _build_equipment_terms(self) -> List[str]:
        """Build equipment terminology."""
        return [
            'sartén', 'pan', 'olla', 'pot', 'cacerola', 'saucepan',
            'horno', 'oven', 'microondas', 'microwave', 'parrilla', 'grill',
            'batidora', 'mixer', 'licuadora', 'blender', 'procesadora', 'processor',
            'cuchillo', 'knife', 'tabla', 'board', 'bowl', 'tazón',
            'colador', 'strainer', 'escurridor', 'colander', 'espátula', 'spatula',
            'cuchara', 'spoon', 'tenedor', 'fork', 'batidor', 'whisk',
            'molde', 'mold', 'bandeja', 'tray', 'fuente', 'dish',
            'vaporera', 'steamer', 'freidora', 'fryer', 'plancha', 'griddle',
            'wok', 'cazuela', 'casserole', 'refractario', 'baking dish',
            'manga', 'piping bag', 'tamiz', 'sieve', 'rallador', 'grater',
            'mortero', 'mortar', 'prensa', 'press', 'tijeras', 'scissors',
            'pinzas', 'tongs', 'espumadera', 'slotted spoon', 'pelador', 'peeler'
        ]
    
    def _build_technique_terms(self) -> List[str]:
        """Build cooking technique terminology."""
        return [
            'picar', 'chop', 'cortar', 'cut', 'rebanar', 'slice',
            'rallar', 'grate', 'pelar', 'peel', 'lavar', 'wash',
            'secar', 'dry', 'escurrir', 'drain', 'colar', 'strain',
            'mezclar', 'mix', 'batir', 'beat', 'revolver', 'stir',
            'amasar', 'knead', 'licuar', 'blend', 'procesar', 'process',
            'moler', 'grind', 'machacar', 'crush', 'triturar', 'mash',
            'condimentar', 'season', 'sazonar', 'flavor', 'salar', 'salt',
            'endulzar', 'sweeten', 'acidular', 'acidify', 'marinar', 'marinate',
            'calentar', 'heat', 'enfriar', 'cool', 'congelar', 'freeze',
            'descongelar', 'thaw', 'templar', 'temper', 'reposar', 'rest',
            'fermentar', 'ferment', 'leudar', 'rise', 'cuajar', 'set',
            'reducir', 'reduce', 'espesar', 'thicken', 'diluir', 'dilute',
            'emulsionar', 'emulsify', 'montar', 'whip', 'incorporar', 'fold',
            'glasear', 'glaze', 'dorar', 'brown', 'caramelizar', 'caramelize',
            'desmoldar', 'unmold', 'decorar', 'decorate', 'servir', 'serve'
        ]
    
    def _build_time_patterns(self) -> List[str]:
        """Build time extraction patterns."""
        return [
            r'(\d+)\s*minutos?',
            r'(\d+)\s*mins?',
            r'(\d+)\s*horas?',
            r'(\d+)\s*hrs?',
            r'(\d+)\s*segundos?',
            r'(\d+)\s*secs?',
            r'media\s*hora',
            r'half\s*hour',
            r'un\s*cuarto\s*de\s*hora',
            r'quarter\s*hour',
            r'hasta\s*que\s*esté\s*listo',
            r'until\s*ready',
            r'hasta\s*que\s*dore',
            r'until\s*golden'
        ]
    
    def _build_temperature_patterns(self) -> List[str]:
        """Build temperature extraction patterns."""
        return [
            r'(\d+)\s*°?c',
            r'(\d+)\s*°?f',
            r'(\d+)\s*celsius',
            r'(\d+)\s*fahrenheit',
            r'(\d+)\s*grados',
            r'(\d+)\s*degrees',
            r'horno\s*fuerte',
            r'horno\s*medio',
            r'horno\s*suave',
            r'fuego\s*alto',
            r'fuego\s*medio',
            r'fuego\s*bajo',
            r'high\s*heat',
            r'medium\s*heat',
            r'low\s*heat'
        ]
    
    def _build_safety_keywords(self) -> List[str]:
        """Build safety-related keywords."""
        return [
            'cuidado', 'careful', 'precaución', 'caution',
            'peligro', 'danger', 'caliente', 'hot',
            'no tocar', 'don\\'t touch', 'usar guantes', 'use gloves',
            'ventilación', 'ventilation', 'extractor', 'exhaust',
            'no dejar solo', 'don\\'t leave alone', 'supervisar', 'supervise',
            'alejar niños', 'keep children away', 'fuego', 'fire',
            'quemadura', 'burn', 'corte', 'cut', 'resbaloso', 'slippery'
        ]
    
    def _build_tip_indicators(self) -> List[str]:
        """Build tip indicator patterns."""
        return [
            r'consejo[\s:]*',
            r'tip[\s:]*',
            r'sugerencia[\s:]*',
            r'nota[\s:]*',
            r'importante[\s:]*',
            r'recuerda[\s:]*',
            r'truco[\s:]*',
            r'secreto[\s:]*'
        ]
    
    def extract_from_text(self, text: str) -> List[PreparationStep]:
        """Extract preparation steps from text."""
        if not text:
            return []
        
        # Clean and prepare text
        text = self._clean_text(text)
        
        # Split into steps
        steps = self._split_into_steps(text)
        
        # Process each step
        preparation_steps = []
        for i, step_text in enumerate(steps, 1):
            step = self._extract_step_from_text(step_text, i)
            if step:
                preparation_steps.append(step)
        
        return preparation_steps
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove common headers
        text = re.sub(r'^(preparación|preparacion|instructions|instrucciones|método|method|pasos|steps)[\s:]*', 
                     '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _split_into_steps(self, text: str) -> List[str]:
        """Split text into individual steps."""
        steps = []
        
        # Try different splitting strategies
        
        # Strategy 1: Split by numbered steps
        numbered_steps = re.split(r'(?=\d+\.?\s)', text)
        if len(numbered_steps) > 1:
            steps = [step.strip() for step in numbered_steps if step.strip()]
        
        # Strategy 2: Split by step indicators
        if not steps:
            for pattern in self.step_indicators:
                parts = re.split(pattern, text, flags=re.IGNORECASE)
                if len(parts) > 1:
                    steps = [part.strip() for part in parts if part.strip()]
                    break
        
        # Strategy 3: Split by sentences if no clear steps
        if not steps:
            sentences = re.split(r'[.!?]+', text)
            steps = [sentence.strip() for sentence in sentences if sentence.strip() and len(sentence.strip()) > 10]
        
        # Strategy 4: Split by paragraph if still no steps
        if not steps:
            paragraphs = text.split('\n')
            steps = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
        
        return steps
    
    def _extract_step_from_text(self, text: str, step_number: int) -> Optional[PreparationStep]:
        """Extract a preparation step from text."""
        if not text or len(text.strip()) < 5:
            return None
        
        # Clean step text
        instruction = self._clean_step_text(text)
        
        # Extract step properties
        step_type = self._determine_step_type(instruction)
        cooking_method = self._determine_cooking_method(instruction)
        estimated_time = self._extract_time(instruction)
        temperature = self._extract_temperature(instruction)
        equipment = self._extract_equipment(instruction)
        techniques = self._extract_techniques(instruction)
        ingredients_mentioned = self._extract_ingredients_mentioned(instruction)
        safety_notes = self._extract_safety_notes(instruction)
        tips = self._extract_tips(instruction)
        
        # Calculate confidence
        confidence = self._calculate_confidence(text, step_type, cooking_method, equipment, techniques)
        
        return PreparationStep(
            step_number=step_number,
            instruction=instruction,
            step_type=step_type,
            cooking_method=cooking_method,
            estimated_time=estimated_time,
            temperature=temperature,
            equipment=equipment,
            techniques=techniques,
            ingredients_mentioned=ingredients_mentioned,
            safety_notes=safety_notes,
            tips=tips,
            original_text=text,
            confidence=confidence
        )
    
    def _clean_step_text(self, text: str) -> str:
        """Clean step text from indicators and numbering."""
        # Remove step indicators
        for pattern in self.step_indicators:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    def _determine_step_type(self, instruction: str) -> StepType:
        """Determine the type of step based on instruction content."""
        instruction_lower = instruction.lower()
        
        # Check for step type indicators
        type_indicators = {
            StepType.PREPARATION: ['picar', 'cortar', 'pelar', 'lavar', 'preparar', 'chop', 'cut', 'peel', 'wash', 'prep'],
            StepType.COOKING: ['hervir', 'freír', 'hornear', 'cocinar', 'boil', 'fry', 'bake', 'cook'],
            StepType.MIXING: ['mezclar', 'batir', 'revolver', 'incorporar', 'mix', 'beat', 'stir', 'fold'],
            StepType.SEASONING: ['condimentar', 'sazonar', 'salar', 'season', 'salt', 'pepper', 'spice'],
            StepType.ASSEMBLY: ['montar', 'armar', 'ensamblar', 'colocar', 'assemble', 'place', 'arrange'],
            StepType.SERVING: ['servir', 'presentar', 'decorar', 'serve', 'present', 'garnish', 'decorate']
        }
        
        for step_type, keywords in type_indicators.items():
            if any(keyword in instruction_lower for keyword in keywords):
                return step_type
        
        return StepType.PREPARATION
    
    def _determine_cooking_method(self, instruction: str) -> CookingMethod:
        """Determine cooking method from instruction."""
        instruction_lower = instruction.lower()
        
        for keyword, method in self.cooking_methods.items():
            if keyword in instruction_lower:
                return method
        
        return CookingMethod.NONE
    
    def _extract_time(self, instruction: str) -> Optional[int]:
        """Extract time information from instruction."""
        instruction_lower = instruction.lower()
        
        for pattern in self.time_patterns:
            match = re.search(pattern, instruction_lower)
            if match:
                if 'minuto' in pattern or 'min' in pattern:
                    try:
                        return int(match.group(1))
                    except (ValueError, IndexError):
                        continue
                elif 'hora' in pattern or 'hr' in pattern:
                    try:
                        return int(match.group(1)) * 60
                    except (ValueError, IndexError):
                        continue
                elif 'segundo' in pattern or 'sec' in pattern:
                    try:
                        return max(1, int(match.group(1)) // 60)
                    except (ValueError, IndexError):
                        continue
                elif 'media hora' in pattern or 'half hour' in pattern:
                    return 30
                elif 'cuarto de hora' in pattern or 'quarter hour' in pattern:
                    return 15
        
        return None
    
    def _extract_temperature(self, instruction: str) -> Optional[int]:
        """Extract temperature information from instruction."""
        instruction_lower = instruction.lower()
        
        for pattern in self.temperature_patterns:
            match = re.search(pattern, instruction_lower)
            if match:
                if '°c' in pattern or 'celsius' in pattern:
                    try:
                        return int(match.group(1))
                    except (ValueError, IndexError):
                        continue
                elif '°f' in pattern or 'fahrenheit' in pattern:
                    try:
                        # Convert Fahrenheit to Celsius
                        f_temp = int(match.group(1))
                        return int((f_temp - 32) * 5/9)
                    except (ValueError, IndexError):
                        continue
                elif 'grados' in pattern or 'degrees' in pattern:
                    try:
                        return int(match.group(1))
                    except (ValueError, IndexError):
                        continue
        
        # Handle descriptive temperatures
        if 'horno fuerte' in instruction_lower or 'high heat' in instruction_lower:
            return 220
        elif 'horno medio' in instruction_lower or 'medium heat' in instruction_lower:
            return 180
        elif 'horno suave' in instruction_lower or 'low heat' in instruction_lower:
            return 150
        elif 'fuego alto' in instruction_lower:
            return 200
        elif 'fuego medio' in instruction_lower:
            return 150
        elif 'fuego bajo' in instruction_lower:
            return 100
        
        return None
    
    def _extract_equipment(self, instruction: str) -> List[str]:
        """Extract equipment mentioned in instruction."""
        instruction_lower = instruction.lower()
        equipment = []
        
        for term in self.equipment_terms:
            if term in instruction_lower:
                equipment.append(term)
        
        return equipment
    
    def _extract_techniques(self, instruction: str) -> List[str]:
        """Extract cooking techniques mentioned in instruction."""
        instruction_lower = instruction.lower()
        techniques = []
        
        for technique in self.technique_terms:
            if technique in instruction_lower:
                techniques.append(technique)
        
        return techniques
    
    def _extract_ingredients_mentioned(self, instruction: str) -> List[str]:
        """Extract ingredients mentioned in the instruction."""
        # This is a simplified version - in practice, you'd want to use
        # the ingredient extractor or maintain a database of ingredients
        common_ingredients = [
            'cebolla', 'ajo', 'tomate', 'sal', 'pimienta', 'aceite',
            'agua', 'harina', 'azúcar', 'leche', 'huevo', 'queso',
            'pollo', 'carne', 'pescado', 'arroz', 'pasta', 'pan',
            'limón', 'perejil', 'oregano', 'albahaca', 'manteca'
        ]
        
        instruction_lower = instruction.lower()
        ingredients = []
        
        for ingredient in common_ingredients:
            if ingredient in instruction_lower:
                ingredients.append(ingredient)
        
        return ingredients
    
    def _extract_safety_notes(self, instruction: str) -> List[str]:
        """Extract safety-related notes from instruction."""
        instruction_lower = instruction.lower()
        safety_notes = []
        
        for keyword in self.safety_keywords:
            if keyword in instruction_lower:
                safety_notes.append(f"Safety note: {keyword}")
        
        return safety_notes
    
    def _extract_tips(self, instruction: str) -> List[str]:
        """Extract tips from instruction."""
        tips = []
        
        for pattern in self.tip_indicators:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                # Extract text after tip indicator
                tip_text = instruction[match.end():].strip()
                if tip_text:
                    tips.append(tip_text)
        
        return tips
    
    def _calculate_confidence(self, text: str, step_type: StepType, cooking_method: CookingMethod,
                            equipment: List[str], techniques: List[str]) -> float:
        """Calculate confidence score for step extraction."""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for longer, more detailed instructions
        if len(text) > 50:
            confidence += 0.1
        
        # Higher confidence if we identified specific step type
        if step_type != StepType.PREPARATION:
            confidence += 0.1
        
        # Higher confidence if we identified cooking method
        if cooking_method != CookingMethod.NONE:
            confidence += 0.1
        
        # Higher confidence if we found equipment
        if equipment:
            confidence += 0.1
        
        # Higher confidence if we found techniques
        if techniques:
            confidence += 0.1
        
        # Higher confidence if text is well-structured
        if any(indicator in text.lower() for indicator in ['primero', 'luego', 'después', 'finalmente']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def extract_from_list(self, steps_list: List[str]) -> List[PreparationStep]:
        """Extract preparation steps from a list of step texts."""
        preparation_steps = []
        
        for i, step_text in enumerate(steps_list, 1):
            step = self._extract_step_from_text(step_text, i)
            if step:
                preparation_steps.append(step)
        
        return preparation_steps
    
    def extract_from_table(self, table_data: Dict[str, Any]) -> List[PreparationStep]:
        """Extract preparation steps from table data."""
        steps = []
        
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])
        
        if not headers or not rows:
            return steps
        
        # Identify column structure
        column_mapping = self._identify_table_columns(headers)
        
        for i, row in enumerate(rows, 1):
            if len(row) >= len(headers):
                step = self._extract_step_from_row(row, column_mapping, i)
                if step:
                    steps.append(step)
        
        return steps
    
    def _identify_table_columns(self, headers: List[str]) -> Dict[str, int]:
        """Identify column types in preparation table."""
        column_mapping = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            if any(keyword in header_lower for keyword in ['paso', 'step', 'número', 'number']):
                column_mapping['step_number'] = i
            elif any(keyword in header_lower for keyword in ['instrucción', 'instruction', 'descripción']):
                column_mapping['instruction'] = i
            elif any(keyword in header_lower for keyword in ['tiempo', 'time', 'duración']):
                column_mapping['time'] = i
            elif any(keyword in header_lower for keyword in ['temperatura', 'temperature']):
                column_mapping['temperature'] = i
            elif any(keyword in header_lower for keyword in ['equipo', 'equipment', 'herramienta']):
                column_mapping['equipment'] = i
            elif any(keyword in header_lower for keyword in ['técnica', 'technique', 'método']):
                column_mapping['technique'] = i
        
        return column_mapping
    
    def _extract_step_from_row(self, row: List[str], column_mapping: Dict[str, int], 
                              step_number: int) -> Optional[PreparationStep]:
        """Extract preparation step from table row."""
        if not row:
            return None
        
        # Extract instruction
        instruction_col = column_mapping.get('instruction', 0)
        instruction = row[instruction_col].strip() if instruction_col < len(row) else ''
        
        if not instruction:
            return None
        
        # Extract step number if available
        step_num_col = column_mapping.get('step_number')
        if step_num_col is not None and step_num_col < len(row):
            try:
                step_number = int(row[step_num_col])
            except ValueError:
                pass
        
        # Extract time if available
        time_col = column_mapping.get('time')
        estimated_time = None
        if time_col is not None and time_col < len(row):
            time_text = row[time_col].strip()
            estimated_time = self._extract_time(time_text)
        
        # Extract temperature if available
        temp_col = column_mapping.get('temperature')
        temperature = None
        if temp_col is not None and temp_col < len(row):
            temp_text = row[temp_col].strip()
            temperature = self._extract_temperature(temp_text)
        
        # Extract equipment if available
        equipment_col = column_mapping.get('equipment')
        equipment = []
        if equipment_col is not None and equipment_col < len(row):
            equipment_text = row[equipment_col].strip()
            if equipment_text:
                equipment = [eq.strip() for eq in equipment_text.split(',')]
        
        # Extract techniques if available
        technique_col = column_mapping.get('technique')
        techniques = []
        if technique_col is not None and technique_col < len(row):
            technique_text = row[technique_col].strip()
            if technique_text:
                techniques = [tech.strip() for tech in technique_text.split(',')]
        
        # Determine other properties
        step_type = self._determine_step_type(instruction)
        cooking_method = self._determine_cooking_method(instruction)
        ingredients_mentioned = self._extract_ingredients_mentioned(instruction)
        safety_notes = self._extract_safety_notes(instruction)
        tips = self._extract_tips(instruction)
        
        # If not extracted from table, extract from instruction
        if not estimated_time:
            estimated_time = self._extract_time(instruction)
        if not temperature:
            temperature = self._extract_temperature(instruction)
        if not equipment:
            equipment = self._extract_equipment(instruction)
        if not techniques:
            techniques = self._extract_techniques(instruction)
        
        return PreparationStep(
            step_number=step_number,
            instruction=instruction,
            step_type=step_type,
            cooking_method=cooking_method,
            estimated_time=estimated_time,
            temperature=temperature,
            equipment=equipment,
            techniques=techniques,
            ingredients_mentioned=ingredients_mentioned,
            safety_notes=safety_notes,
            tips=tips,
            original_text=' '.join(row),
            confidence=0.8  # Higher confidence for table data
        )
    
    def standardize_steps(self, steps: List[PreparationStep]) -> List[Dict[str, Any]]:
        """Standardize preparation steps to common format."""
        standardized = []
        
        for step in steps:
            standardized_step = {
                'step_number': step.step_number,
                'instruction': step.instruction,
                'step_type': step.step_type.value,
                'cooking_method': step.cooking_method.value,
                'estimated_time': step.estimated_time,
                'temperature': step.temperature,
                'equipment': step.equipment,
                'techniques': step.techniques,
                'ingredients_mentioned': step.ingredients_mentioned,
                'safety_notes': step.safety_notes,
                'tips': step.tips,
                'confidence': step.confidence,
                'original_text': step.original_text
            }
            standardized.append(standardized_step)
        
        return standardized
    
    def calculate_total_time(self, steps: List[PreparationStep]) -> Optional[int]:
        """Calculate total estimated time for all steps."""
        total_time = 0
        has_time = False
        
        for step in steps:
            if step.estimated_time:
                total_time += step.estimated_time
                has_time = True
        
        return total_time if has_time else None
    
    def group_by_type(self, steps: List[PreparationStep]) -> Dict[str, List[PreparationStep]]:
        """Group steps by type."""
        grouped = {}
        
        for step in steps:
            step_type = step.step_type.value
            if step_type not in grouped:
                grouped[step_type] = []
            grouped[step_type].append(step)
        
        return grouped
    
    def validate_steps(self, steps: List[PreparationStep]) -> Dict[str, Any]:
        """Validate preparation steps."""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        if not steps:
            validation_results['errors'].append("No preparation steps found")
            validation_results['is_valid'] = False
            return validation_results
        
        # Check for step numbering issues
        step_numbers = [step.step_number for step in steps]
        if len(set(step_numbers)) != len(step_numbers):
            validation_results['warnings'].append("Duplicate step numbers found")
        
        # Check for missing instructions
        empty_instructions = [step for step in steps if not step.instruction.strip()]
        if empty_instructions:
            validation_results['warnings'].append(f"{len(empty_instructions)} steps with empty instructions")
        
        # Check for very low confidence steps
        low_confidence = [step for step in steps if step.confidence < 0.3]
        if low_confidence:
            validation_results['warnings'].append(f"{len(low_confidence)} steps with low confidence")
        
        # Check for safety concerns
        unsafe_steps = [step for step in steps if step.safety_notes]
        if unsafe_steps:
            validation_results['warnings'].append(f"{len(unsafe_steps)} steps with safety notes")
        
        return validation_results
    
    def export_to_dict(self, steps: List[PreparationStep]) -> List[Dict[str, Any]]:
        """Export preparation steps to dictionary format."""
        return [
            {
                'step_number': step.step_number,
                'instruction': step.instruction,
                'step_type': step.step_type.value,
                'cooking_method': step.cooking_method.value,
                'estimated_time': step.estimated_time,
                'temperature': step.temperature,
                'equipment': step.equipment,
                'techniques': step.techniques,
                'ingredients_mentioned': step.ingredients_mentioned,
                'safety_notes': step.safety_notes,
                'tips': step.tips,
                'confidence': step.confidence,
                'original_text': step.original_text
            }
            for step in steps
        ]