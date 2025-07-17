"""
Sistema Mayra - Unified System Prompts Configuration
Contains the unified prompt system for the three motors as specified in the updated requirements
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class MotorType(Enum):
    """Types of motors in the nutrition system."""
    NEW_PATIENT = "new_patient"
    CONTROL = "control"
    REPLACEMENT = "replacement"


class PlanType(Enum):
    """Types of nutrition plans."""
    MAINTENANCE = "mantenimiento"
    WEIGHT_LOSS_05 = "bajar_05kg"
    WEIGHT_LOSS_1 = "bajar_1kg"
    WEIGHT_GAIN = "subir_peso"
    MUSCLE_GAIN = "ganancia_muscular"


class ActivityType(Enum):
    """Types of physical activities."""
    SEDENTARY = "sedentario"
    LIGHT_WALKS = "caminatas_ligeras"
    MODERATE_WALKS = "caminatas_moderadas"
    WEIGHT_TRAINING = "pesas"
    CARDIO = "cardio"
    MIXED = "mixto"


@dataclass
class PromptTemplate:
    """Base class for prompt templates."""
    
    system_prompt: str
    user_prompt: str
    variables: Dict[str, Any]
    
    def format(self, **kwargs) -> str:
        """Format the prompt with provided variables."""
        all_variables = {**self.variables, **kwargs}
        return self.user_prompt.format(**all_variables)


class SystemPrompts:
    """Container for the unified system prompts used in the nutrition system."""
    
    # Base system prompt - Foundation for all motors
    BASE_SYSTEM_PROMPT = """Eres Mayra, nutricionista experta que genera planes alimentarios usando el método "Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva".

IDENTIDAD:
- Usás léxico argentino exclusivamente (palta, no aguacate)
- Sos precisa con cantidades y preparaciones
- Seguís las reglas del método sin excepciones

REGLAS FUNDAMENTALES DEL MÉTODO:
✓ Plan de 3 días iguales en calorías y macronutrientes
✓ Todas las comidas en gramos {tipo_peso}
✓ Papa, batata y choclo: SIEMPRE en gramos exactos
✓ Verduras no tipo C: libres (porción visual coherente)
✓ Frutas: SIEMPRE en gramos exactos
✓ Incluir preparación detallada de cada comida
✓ No usar suplementos si no están indicados
✓ Calcular desde: https://www.calculator.net/calorie-calculator.html

CONTEXTO DE RECETAS DISPONIBLES:
{rag_context}

ADAPTACIONES AUTOMÁTICAS:
- Nivel económico → Seleccionar ingredientes apropiados
- Patologías → Ajustar automáticamente sin mencionar
- Restricciones → Evitar completamente los alimentos indicados
- Preferencias → Priorizar alimentos que le gustan

FORMATO DE RESPUESTA:
- Título del plan con datos del paciente
- Plan organizado por días y comidas
- 3 opciones equivalentes por comida (±5% calorías)
- Preparación paso a paso para cada opción
- Total calórico y macros del día"""

    # Motor 1 - New Patient
    MOTOR_1_PROMPT = """MOTOR 1: PACIENTE NUEVO

Generá un plan alimentario de 3 días iguales siguiendo el método Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva.

DATOS DEL PACIENTE:
Nombre: {nombre}
Edad: {edad}
Sexo: {sexo}
Estatura: {estatura} cm
Peso: {peso} kg
Objetivo: {objetivo}
Actividad física: {actividad_fisica}
Frecuencia: {frecuencia_semanal}
Duración: {duracion_sesion} minutos
Tipo de entrenamiento: {tipo_entrenamiento}
Suplementación: {suplementacion}
Patologías/Medicación: {patologias}
NO consume: {restricciones}
Le gusta: {preferencias}
Horarios: {horarios}
Nivel económico: {nivel_economico}
Notas: {notas_personales}

CONFIGURACIÓN DEL PLAN:
Tipo de peso: {tipo_peso}
Comidas principales: {comidas_principales}
Colaciones: {tipo_colaciones}

ESPECIFICACIONES:
- {comidas_principales} comidas principales
- 3 opciones por cada comida (equivalentes ±5%)
- Colaciones: {tipo_colaciones}
- Preparación incluida para cada opción
- Usar ingredientes del contexto RAG proporcionado

ESTRUCTURA DE RESPUESTA:
# PLAN NUTRICIONAL - {nombre}
## Objetivo: {objetivo}

### DÍA 1, 2 y 3 (IGUALES)

**DESAYUNO** (XXX kcal)
Opción 1: [Receta detallada con gramos exactos]
Preparación: [Paso a paso]

Opción 2: [Receta equivalente]
Preparación: [Paso a paso]

Opción 3: [Receta equivalente]
Preparación: [Paso a paso]

[Repetir para cada comida]

**TOTALES DEL DÍA:**
- Calorías: XXX kcal
- Proteínas: XX g
- Carbohidratos: XX g  
- Grasas: XX g"""

    # Motor 2 - Control/Adjustments
    MOTOR_2_PROMPT = """MOTOR 2: CONTROL - AJUSTE COMPLETO

Reformulá completamente el plan de 3 días iguales para este paciente en seguimiento. Usá las indicaciones AGREGAR/SACAR/DEJAR como guía práctica, pero adaptá todo el plan a los nuevos requerimientos calóricos.

DATOS ACTUALIZADOS:
Nombre: {nombre}
Fecha del control: {fecha_control}
Peso actual: {peso_actual} kg
Objetivo actualizado: {objetivo_actualizado}
Actividad física actual: {actividad_actual}
Cambios en entrenamiento: {cambios_entrenamiento}
Suplementación: {suplementacion_actual}
Patologías/Medicación: {patologias_actuales}
NO consume: {restricciones_actuales}
Le gusta: {preferencias_actuales}
Horarios actualizados: {horarios_actuales}
Nivel económico: {nivel_economico_actual}
Notas: {notas_actuales}

INSTRUCCIONES DE LA FICHA:
AGREGAR: {agregar}
SACAR: {sacar}
DEJAR: {dejar}

CONFIGURACIÓN:
Tipo de peso: {tipo_peso}
Comidas principales: {comidas_principales}
Colaciones: {tipo_colaciones}

IMPORTANTE:
- Reformular TODO el plan con nueva base calórica
- Aplicar cambios AGREGAR/SACAR/DEJAR sobre la nueva base
- Mantener equivalencias ±5% entre opciones
- Usar contexto RAG para nuevas recetas"""

    # Motor 3 - Meal Replacement
    MOTOR_3_PROMPT = """MOTOR 3: REEMPLAZO PUNTUAL

Reemplazá una comida específica del plan por otra receta que respete los mismos macros y calorías. Seguí el estilo del método Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva.

DATOS:
Paciente: {nombre_paciente}
Día y comida a reemplazar: {dia_comida}
Nueva comida deseada: {nueva_comida}
Condiciones: {condiciones_especiales}
Tipo de peso: {tipo_peso}
Macros originales: {macros_originales}

INSTRUCCIONES:
- Mantener macros y calorías originales (±5%)
- Todos los ingredientes en gramos {tipo_peso}
- Verduras tipo C y frutas en gramos exactos
- Otras verduras libres
- Incluir preparación detallada
- Usar contexto RAG para ingredientes disponibles

FORMATO DE RESPUESTA:
**NUEVA {dia_comida.upper()}** (XXX kcal)
[Receta detallada con gramos exactos]

**Preparación:**
[Paso a paso detallado]

**Macros:**
- Calorías: XXX kcal
- Proteínas: XX g
- Carbohidratos: XX g
- Grasas: XX g"""

    # Validation prompts
    VALIDATION_PROMPT = """VALIDACIONES AUTOMÁTICAS:

1. COHERENCIA NUTRICIONAL:
   - Verificar que las 3 opciones sean equivalentes (±5%)
   - Comprobar que los totales coincidan con el objetivo

2. RESTRICCIONES:
   - Eliminar completamente alimentos de "NO consume"
   - Adaptar a patologías sin mencionarlas explícitamente
   - Respetar nivel económico en selección de ingredientes

3. FORMATO:
   - Gramos exactos para tipo C y frutas
   - "A gusto" solo para verduras libres
   - Preparaciones siempre incluidas
   - Léxico argentino verificado

4. CONTEXTO RAG:
   - Usar únicamente recetas del contexto proporcionado
   - Adaptar cantidades manteniendo proporciones
   - Priorizar recetas que coincidan con preferencias"""

    # Variable definitions for each motor
    MOTOR_1_VARIABLES = {
        "nombre", "edad", "sexo", "estatura", "peso", "objetivo",
        "actividad_fisica", "frecuencia_semanal", "duracion_sesion",
        "tipo_entrenamiento", "suplementacion", "patologias",
        "restricciones", "preferencias", "horarios", "nivel_economico",
        "notas_personales", "tipo_peso", "comidas_principales",
        "tipo_colaciones", "rag_context"
    }

    MOTOR_2_VARIABLES = {
        "nombre", "fecha_control", "peso_actual", "objetivo_actualizado",
        "actividad_actual", "cambios_entrenamiento", "suplementacion_actual",
        "patologias_actuales", "restricciones_actuales", "preferencias_actuales",
        "horarios_actuales", "nivel_economico_actual", "notas_actuales",
        "agregar", "sacar", "dejar", "tipo_peso", "comidas_principales",
        "tipo_colaciones", "rag_context"
    }

    MOTOR_3_VARIABLES = {
        "nombre_paciente", "dia_comida", "nueva_comida", "condiciones_especiales",
        "tipo_peso", "macros_originales", "rag_context"
    }

    @classmethod
    def get_motor_prompt(cls, motor_type: MotorType) -> PromptTemplate:
        """Get the appropriate prompt template for a motor type."""
        
        if motor_type == MotorType.NEW_PATIENT:
            return PromptTemplate(
                system_prompt=cls.BASE_SYSTEM_PROMPT,
                user_prompt=cls.MOTOR_1_PROMPT,
                variables=cls.MOTOR_1_VARIABLES
            )
        elif motor_type == MotorType.CONTROL:
            return PromptTemplate(
                system_prompt=cls.BASE_SYSTEM_PROMPT,
                user_prompt=cls.MOTOR_2_PROMPT,
                variables=cls.MOTOR_2_VARIABLES
            )
        elif motor_type == MotorType.REPLACEMENT:
            return PromptTemplate(
                system_prompt=cls.BASE_SYSTEM_PROMPT,
                user_prompt=cls.MOTOR_3_PROMPT,
                variables=cls.MOTOR_3_VARIABLES
            )
        else:
            raise ValueError(f"Unknown motor type: {motor_type}")

    @classmethod
    def build_motor_1_prompt(cls, patient_data: Dict[str, Any], rag_context: str) -> Dict[str, str]:
        """Build a complete Motor 1 prompt with patient data."""
        template = cls.get_motor_prompt(MotorType.NEW_PATIENT)
        
        # Default values for missing data
        defaults = {
            'nombre': patient_data.get('name', 'Paciente'),
            'edad': patient_data.get('age', ''),
            'sexo': patient_data.get('sex', ''),
            'estatura': patient_data.get('height', ''),
            'peso': patient_data.get('weight', ''),
            'objetivo': patient_data.get('objective', ''),
            'actividad_fisica': patient_data.get('activity_type', ''),
            'frecuencia_semanal': patient_data.get('frequency', ''),
            'duracion_sesion': patient_data.get('duration', ''),
            'tipo_entrenamiento': patient_data.get('training_type', ''),
            'suplementacion': patient_data.get('supplements', 'Ninguna'),
            'patologias': patient_data.get('pathologies', 'Ninguna'),
            'restricciones': patient_data.get('restrictions', 'Ninguna'),
            'preferencias': patient_data.get('preferences', 'Ninguna'),
            'horarios': patient_data.get('schedule', 'Estándar'),
            'nivel_economico': patient_data.get('economic_level', 'medio'),
            'notas_personales': patient_data.get('notes', ''),
            'tipo_peso': patient_data.get('weight_type', 'crudo'),
            'comidas_principales': patient_data.get('main_meals', 4),
            'tipo_colaciones': patient_data.get('snacks_type', 'Sin colaciones'),
            'rag_context': rag_context
        }
        
        # Format system prompt with tipo_peso
        system_prompt_formatted = template.system_prompt.format(
            tipo_peso=defaults['tipo_peso'],
            rag_context=rag_context
        )
        
        # Format user prompt with all variables
        user_prompt_formatted = template.user_prompt.format(**defaults)
        
        return {
            'system': system_prompt_formatted,
            'user': user_prompt_formatted
        }

    @classmethod
    def build_motor_2_prompt(cls, patient_data: Dict[str, Any], control_data: Dict[str, Any], rag_context: str) -> Dict[str, str]:
        """Build a complete Motor 2 prompt with patient and control data."""
        template = cls.get_motor_prompt(MotorType.CONTROL)
        
        # Merge patient and control data
        all_data = {**patient_data, **control_data}
        
        defaults = {
            'nombre': all_data.get('name', 'Paciente'),
            'fecha_control': all_data.get('control_date', ''),
            'peso_actual': all_data.get('current_weight', ''),
            'objetivo_actualizado': all_data.get('updated_objective', ''),
            'actividad_actual': all_data.get('current_activity', ''),
            'cambios_entrenamiento': all_data.get('training_changes', 'Sin cambios'),
            'suplementacion_actual': all_data.get('current_supplements', 'Ninguna'),
            'patologias_actuales': all_data.get('current_pathologies', 'Ninguna'),
            'restricciones_actuales': all_data.get('current_restrictions', 'Ninguna'),
            'preferencias_actuales': all_data.get('current_preferences', 'Ninguna'),
            'horarios_actuales': all_data.get('current_schedule', 'Estándar'),
            'nivel_economico_actual': all_data.get('current_economic_level', 'medio'),
            'notas_actuales': all_data.get('current_notes', ''),
            'agregar': all_data.get('add_items', 'Nada'),
            'sacar': all_data.get('remove_items', 'Nada'),
            'dejar': all_data.get('keep_items', 'Todo el plan actual'),
            'tipo_peso': all_data.get('weight_type', 'crudo'),
            'comidas_principales': all_data.get('main_meals', 4),
            'tipo_colaciones': all_data.get('snacks_type', 'Sin colaciones'),
            'rag_context': rag_context
        }
        
        # Format system prompt with tipo_peso
        system_prompt_formatted = template.system_prompt.format(
            tipo_peso=defaults['tipo_peso'],
            rag_context=rag_context
        )
        
        # Format user prompt with all variables
        user_prompt_formatted = template.user_prompt.format(**defaults)
        
        return {
            'system': system_prompt_formatted,
            'user': user_prompt_formatted
        }

    @classmethod
    def build_motor_3_prompt(cls, patient_data: Dict[str, Any], replacement_data: Dict[str, Any], rag_context: str) -> Dict[str, str]:
        """Build a complete Motor 3 prompt with patient and replacement data."""
        template = cls.get_motor_prompt(MotorType.REPLACEMENT)
        
        # Merge patient and replacement data
        all_data = {**patient_data, **replacement_data}
        
        defaults = {
            'nombre_paciente': all_data.get('name', 'Paciente'),
            'dia_comida': all_data.get('meal_to_replace', ''),
            'nueva_comida': all_data.get('new_meal', ''),
            'condiciones_especiales': all_data.get('special_conditions', 'Ninguna'),
            'tipo_peso': all_data.get('weight_type', 'crudo'),
            'macros_originales': all_data.get('original_macros', ''),
            'rag_context': rag_context
        }
        
        # Format system prompt with tipo_peso
        system_prompt_formatted = template.system_prompt.format(
            tipo_peso=defaults['tipo_peso'],
            rag_context=rag_context
        )
        
        # Format user prompt with all variables
        user_prompt_formatted = template.user_prompt.format(**defaults)
        
        return {
            'system': system_prompt_formatted,
            'user': user_prompt_formatted
        }

    @classmethod
    def validate_prompt_variables(cls, motor_type: MotorType, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required variables are present for a motor type."""
        required_vars = {
            MotorType.NEW_PATIENT: ['nombre', 'edad', 'sexo', 'estatura', 'peso', 'objetivo'],
            MotorType.CONTROL: ['nombre', 'peso_actual', 'objetivo_actualizado'],
            MotorType.REPLACEMENT: ['nombre_paciente', 'dia_comida', 'nueva_comida']
        }
        
        missing_vars = []
        required = required_vars.get(motor_type, [])
        
        for var in required:
            if var not in variables or not variables[var]:
                missing_vars.append(var)
        
        return {
            'valid': len(missing_vars) == 0,
            'missing_variables': missing_vars,
            'required_variables': required
        }


# Utility functions for prompt management
def get_system_prompt_for_motor(motor_type: MotorType) -> str:
    """Get the system prompt for a specific motor type."""
    template = SystemPrompts.get_motor_prompt(motor_type)
    return template.system_prompt


def build_complete_prompt(motor_type: MotorType, patient_data: Dict[str, Any], 
                         additional_data: Optional[Dict[str, Any]] = None, 
                         rag_context: str = "") -> Dict[str, str]:
    """Build a complete prompt with system and user parts."""
    
    if motor_type == MotorType.NEW_PATIENT:
        return SystemPrompts.build_motor_1_prompt(patient_data, rag_context)
    elif motor_type == MotorType.CONTROL:
        return SystemPrompts.build_motor_2_prompt(patient_data, additional_data or {}, rag_context)
    elif motor_type == MotorType.REPLACEMENT:
        return SystemPrompts.build_motor_3_prompt(patient_data, additional_data or {}, rag_context)
    else:
        raise ValueError(f"Unknown motor type: {motor_type}")


def format_rag_context(recipes: List[Dict[str, Any]]) -> str:
    """Format RAG recipe results into a context string for prompts."""
    if not recipes:
        return "No se encontraron recetas relevantes en la base de datos."
    
    context_parts = []
    for recipe in recipes:
        recipe_text = f"- {recipe.get('name', 'Sin nombre')}"
        if recipe.get('category'):
            recipe_text += f" [{recipe['category']}]"
        if recipe.get('description'):
            recipe_text += f": {recipe['description']}"
        context_parts.append(recipe_text)
    
    return "\n".join(context_parts)