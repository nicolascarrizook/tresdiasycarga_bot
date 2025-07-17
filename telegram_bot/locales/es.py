"""
Spanish localization messages for Sistema Mayra Telegram Bot.
"""

# Main messages
MESSAGES = {
    # Welcome and start
    "welcome": """¡Hola {name}! 👋

Soy el asistente de Mayra y te ayudo a crear tu plan nutricional personalizado usando el método <b>"Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva"</b>.

¿Qué necesitas hacer hoy?""",

    "welcome_back": """¡Hola de nuevo, {name}! 👋

¿En qué puedo ayudarte hoy?""",

    # Motor selection
    "motor_selection": """Selecciona el tipo de consulta que necesitas:

🆕 <b>Nuevo Paciente</b>
Crear un plan nutricional completo desde cero

🔄 <b>Control/Ajuste</b>
Modificar tu plan existente según tu progreso

🍽️ <b>Reemplazo de Comida</b>
Cambiar una comida específica manteniendo los macros

¿Cuál prefieres?""",

    # Data collection start
    "data_collection_start": """¡Perfecto! Voy a recopilar algunos datos para crear tu plan personalizado.

Este proceso tomará aproximadamente <b>5-10 minutos</b>. Puedes cancelar en cualquier momento escribiendo /cancel.

¿Empezamos? 🚀""",

    # Motor 1 messages
    "motor1_name": """Empecemos con tu información personal.

<b>¿Cuál es tu nombre completo?</b>

Por favor, ingresa tu nombre y apellido.""",

    "motor1_age": """¡Hola {name}! 👋

<b>¿Cuántos años tienes?</b>

Por favor, ingresa tu edad (debe ser mayor a 16 años).""",

    "motor1_sex": """<b>¿Cuál es tu sexo?</b>

Esta información es importante para calcular tus necesidades nutricionales.""",

    "motor1_height": """<b>¿Cuál es tu altura?</b>

Por favor, ingresa tu altura en centímetros (ej: 170).""",

    "motor1_weight": """<b>¿Cuál es tu peso actual?</b>

Por favor, ingresa tu peso en kilogramos (ej: 70.5).""",

    "motor1_objective": """<b>¿Cuál es tu objetivo nutricional?</b>

Selecciona la opción que mejor describe tu meta:""",

    "motor1_activity_type": """<b>¿Qué tipo de actividad física realizas?</b>

Selecciona la opción que mejor describe tu actividad principal:""",

    "motor1_activity_frequency": """<b>¿Con qué frecuencia realizas esta actividad?</b>

Selecciona la frecuencia que mejor describe tu rutina:""",

    "motor1_activity_duration": """<b>¿Cuánto tiempo dura cada sesión de actividad?</b>

Por favor, ingresa la duración promedio en minutos (ej: 60).""",

    "motor1_weight_type": """<b>¿Cómo prefieres que se expresen los pesos de los alimentos?</b>

Esta información determinará cómo se mostrarán las porciones en tu plan:""",

    "motor1_economic_level": """<b>¿Cuál es tu nivel económico para la compra de alimentos?</b>

Esto me ayudará a adaptar las recomendaciones a tu presupuesto:""",

    "motor1_supplements": """<b>¿Tomas algún suplemento actualmente?</b>

Puedes seleccionar varios o ninguno. Esta información es importante para evitar duplicaciones:""",

    "motor1_pathologies": """<b>¿Tienes alguna condición médica o patología?</b>

Puedes escribir varias separadas por comas, o seleccionar "Ninguna" si no tienes.

<i>Ejemplos: Diabetes, Hipertensión, Hipotiroidismo, etc.</i>""",

    "motor1_restrictions": """<b>¿Tienes alguna restricción alimentaria?</b>

Selecciona todas las que correspondan:""",

    "motor1_preferences": """<b>¿Tienes alguna preferencia alimentaria?</b>

Escribe los alimentos que prefieres o que te gustan más, separados por comas.

<i>Ejemplos: Pollo, Pescado, Verduras verdes, Frutas cítricas, etc.</i>""",

    "motor1_dislikes": """<b>¿Hay algún alimento que no te guste?</b>

Escribe los alimentos que no te gustan o que prefieres evitar, separados por comas.

<i>Ejemplos: Brócoli, Hígado, Pescado, Legumbres, etc.</i>""",

    "motor1_allergies": """<b>¿Tienes alguna alergia alimentaria?</b>

Es muy importante que menciones todas las alergias para evitar incluir estos alimentos en tu plan.

Escribe las alergias separadas por comas, o "Ninguna" si no tienes.

<i>Ejemplos: Frutos secos, Mariscos, Huevos, Gluten, etc.</i>""",

    "motor1_main_meals": """<b>¿Cuántas comidas principales prefieres al día?</b>

Selecciona el número de comidas principales (desayuno, almuerzo, cena):""",

    "motor1_collations": """<b>¿Cuántas colaciones prefieres al día?</b>

Las colaciones son pequeñas comidas entre las principales:""",

    "motor1_schedule": """<b>¿Tienes alguna preferencia de horarios para las comidas?</b>

Puedes escribir los horarios que prefieres o saltar este paso.

<i>Ejemplo: Desayuno 7:00, Almuerzo 13:00, Cena 20:00</i>""",

    "motor1_notes": """<b>¿Hay algo más que quieras contarme?</b>

Puedes agregar cualquier información adicional que consideres importante para tu plan nutricional.

<i>Ejemplos: Horarios de trabajo, deportes específicos, objetivos particulares, etc.</i>""",

    "motor1_review": """<b>Revisemos tu información:</b>

{patient_summary}

¿Es correcta toda la información? Si quieres cambiar algo, puedes editarlo antes de generar el plan.""",

    "motor1_generating": """<b>¡Perfecto! Generando tu plan nutricional...</b> ⏳

Esto puede tomar unos segundos. Estoy creando tu plan personalizado usando el método "Tres Días y Carga" basado en toda la información que me proporcionaste.

Por favor, espera...""",

    "motor1_plan_ready": """<b>¡Excelente! Tu plan nutricional está listo! 🎉</b>

Tu plan personalizado ha sido generado exitosamente usando el método <b>"Tres Días y Carga | Dieta Inteligente® & Nutrición Evolutiva"</b>.

📋 <b>El plan incluye:</b>
• 3 días de menú completo
• Porciones exactas en gramos ({weight_type})
• Instrucciones de preparación detalladas
• Equivalencias nutricionales
• Adaptado a tus objetivos y actividad

Te envío el PDF con todos los detalles 📄""",

    # Motor 2 messages
    "motor2_verify_patient": """¡Hola! Para hacer un control o ajuste, necesito verificar que ya tienes un plan anterior conmigo.

Buscando tu información...""",

    "motor2_patient_found": """¡Perfecto! Encontré tu información anterior:

<b>Último plan:</b> {last_plan_date}
<b>Objetivo anterior:</b> {objective}
<b>Peso anterior:</b> {weight} kg

¿Continuamos con el control?""",

    "motor2_patient_not_found": """No encontré un plan anterior para ti. 

Para hacer un control o ajuste, primero necesitas crear un plan inicial usando la opción "🆕 Nuevo Paciente".

¿Quieres crear tu primer plan ahora?""",

    "motor2_current_weight": """<b>¿Cuál es tu peso actual?</b>

Por favor, ingresa tu peso actual en kilogramos para ver tu progreso.""",

    "motor2_progress": """<b>¿Cómo ha sido tu progreso con el plan anterior?</b>

Cuéntame cómo te has sentido:

• ¿Has notado cambios en tu peso?
• ¿Cómo ha sido tu energía?
• ¿Has tenido alguna dificultad?""",

    "motor2_compliance": """<b>¿Has podido seguir el plan anterior?</b>

Del 1 al 10, ¿qué tan bien has podido cumplir con las indicaciones?

También puedes contarme qué partes fueron más fáciles o difíciles de seguir.""",

    "motor2_difficulties": """<b>¿Has tenido alguna dificultad específica?</b>

Cuéntame si hubo algo que te resultó difícil:

• Alimentos que no te gustaron
• Horarios complicados
• Porciones muy grandes o pequeñas
• Falta de variedad
• Otros problemas""",

    "motor2_objective_change": """<b>¿Quieres cambiar tu objetivo nutricional?</b>

Tu objetivo anterior era: <b>{current_objective}</b>

¿Quieres mantenerlo o cambiarlo?""",

    "motor2_activity_change": """<b>¿Ha cambiado tu actividad física?</b>

Tu actividad anterior era: <b>{current_activity}</b>

¿Quieres mantenerla o actualizarla?""",

    "motor2_preference_change": """<b>¿Quieres cambiar alguna preferencia alimentaria?</b>

¿Hay algún alimento nuevo que quieras incluir o excluir de tu plan?""",

    "motor2_instructions": """<b>¿Tienes alguna instrucción específica para el nuevo plan?</b>

Puedes pedirme que:
• AGREGUE alimentos específicos
• SAQUE alimentos que no te gustaron
• DEJE igual las cosas que funcionaron bien

<i>Ejemplo: "Agregar más pescado, sacar el brócoli, dejar igual los desayunos"</i>""",

    "motor2_review": """<b>Revisemos los cambios para tu nuevo plan:</b>

{changes_summary}

¿Está todo correcto? ¿Procedemos a generar tu plan ajustado?""",

    "motor2_generating": """<b>Generando tu plan ajustado...</b> ⏳

Estoy creando tu nuevo plan considerando:
• Tu progreso anterior
• Los cambios solicitados
• Tu peso actual
• Tus nuevas preferencias

Por favor, espera...""",

    "motor2_plan_ready": """<b>¡Tu plan ajustado está listo! 🎉</b>

He generado tu nuevo plan considerando:
• Tu progreso y peso actual
• Los cambios que solicitaste
• Tu experiencia con el plan anterior

📋 <b>El nuevo plan incluye:</b>
• Ajustes basados en tu progreso
• Mejoras según tus comentarios
• Misma estructura de 3 días
• Porciones actualizadas

Te envío el PDF actualizado 📄""",

    # Motor 3 messages
    "motor3_verify_patient": """¡Hola! Para hacer un reemplazo de comida, necesito verificar que tienes un plan activo.

Buscando tu plan actual...""",

    "motor3_patient_found": """¡Perfecto! Encontré tu plan actual:

<b>Plan generado:</b> {plan_date}
<b>Tipo:</b> {plan_type}

¿Continuamos con el reemplazo?""",

    "motor3_select_day": """<b>¿De qué día quieres reemplazar la comida?</b>

Tu plan actual tiene 3 días. Selecciona el día:""",

    "motor3_select_meal": """<b>¿Qué comida del Día {day} quieres reemplazar?</b>

Selecciona la comida que deseas cambiar:""",

    "motor3_select_option": """<b>¿Cuál de las opciones del {meal} quieres reemplazar?</b>

Tienes estas opciones disponibles:

{meal_options}

Selecciona la opción que quieres cambiar:""",

    "motor3_replacement_type": """<b>¿Qué tipo de reemplazo necesitas?</b>

Selecciona el motivo del reemplazo:""",

    "motor3_replacement_reason": """<b>¿Por qué quieres reemplazar esta comida?</b>

Cuéntame el motivo específico:

• ¿No te gusta algún ingrediente?
• ¿No conseguiste algún alimento?
• ¿Quieres más variedad?
• ¿Otro motivo?""",

    "motor3_specific_request": """<b>¿Tienes alguna comida específica en mente?</b>

Puedes pedirme:
• Un alimento específico (ej: "Pollo a la plancha")
• Un tipo de preparación (ej: "Algo al horno")
• Una categoría (ej: "Pescado")
• O déjame que te sugiera algo equivalente""",

    "motor3_special_conditions": """<b>¿Hay alguna condición especial para el reemplazo?</b>

Por ejemplo:
• Tiempo de preparación limitado
• Ingredientes que tienes disponibles
• Restricciones específicas
• Otro requerimiento

Si no tienes condiciones especiales, puedes saltar este paso.""",

    "motor3_review": """<b>Revisemos el reemplazo solicitado:</b>

<b>Comida original:</b>
{original_meal}

<b>Reemplazo solicitado:</b>
{replacement_details}

¿Está todo correcto? ¿Procedemos a generar el reemplazo?""",

    "motor3_generating": """<b>Generando tu reemplazo...</b> ⏳

Estoy creando una comida equivalente que:
• Mantenga las mismas calorías y macros
• Respete tus preferencias
• Cumpla con tus requerimientos

Por favor, espera...""",

    "motor3_replacement_ready": """<b>¡Tu reemplazo está listo! 🎉</b>

He generado una comida equivalente que mantiene:
• Las mismas calorías
• Los mismos macronutrientes
• El equilibrio de tu plan

<b>Comida reemplazada:</b>
{replacement_summary}

Te envío la actualización 📄""",

    # Common messages
    "processing": """⏳ <b>Procesando...</b>

Por favor, espera un momento.""",

    "success": """✅ <b>¡Completado exitosamente!</b>""",

    "plan_generated": """🎉 <b>¡Tu plan nutricional ha sido generado exitosamente!</b>

Te envío el PDF con todos los detalles.""",

    "error_general": """😔 <b>Ocurrió un error inesperado</b>

Por favor, intenta nuevamente o contacta al administrador si el problema persiste.

Puedes escribir /start para comenzar de nuevo.""",

    "error_api": """🔧 <b>Error de conexión</b>

Hay un problema temporal con el sistema. Por favor, intenta nuevamente en unos minutos.

Si el problema persiste, contacta al administrador.""",

    "error_timeout": """⏰ <b>La conversación ha expirado</b>

Tu sesión se ha cerrado por inactividad. 

Escribe /start para comenzar un nuevo proceso.""",

    "error_invalid_data": """❌ <b>Datos no válidos</b>

Los datos ingresados no son correctos. Por favor, revisa la información e intenta nuevamente.

{validation_details}""",

    "error_missing_data": """📝 <b>Falta información</b>

Necesito más información para continuar:

{missing_fields}""",

    "error_rate_limit": """🚦 <b>Demasiadas solicitudes</b>

Has realizado muchas solicitudes en poco tiempo. Por favor, espera un momento antes de continuar.""",

    "cancel_conversation": """❌ <b>Proceso cancelado</b>

La conversación ha sido cancelada. 

Escribe /start cuando quieras comenzar de nuevo.""",

    "help_message": """<b>📖 Sistema Mayra - Guía de Uso</b>

<b>🚀 Comandos disponibles:</b>
/start - Iniciar nueva consulta
/help - Mostrar esta ayuda
/cancel - Cancelar proceso actual
/mi_info - Ver mi información guardada
/historial - Ver historial de planes

<b>🔧 Tipos de consulta:</b>

🆕 <b>Nuevo Paciente:</b>
• Plan nutricional completo desde cero
• Recopilación de todos tus datos
• Plan personalizado de 3 días

🔄 <b>Control/Ajuste:</b>
• Modificar plan existente
• Basado en tu progreso
• Ajustes según tus necesidades

🍽️ <b>Reemplazo de Comida:</b>
• Cambiar una comida específica
• Mantiene macros equivalentes
• Respeta tus preferencias

<b>📊 Método "Tres Días y Carga":</b>
• Plan de 3 días iguales en calorías y macros
• Porciones exactas en gramos
• Adaptado a tu objetivo y actividad
• Incluye preparación detallada

<b>❓ ¿Necesitas ayuda?</b>
Escribe /start para comenzar o contacta al administrador.""",

    "maintenance_mode": """🔧 <b>Mantenimiento del Sistema</b>

El bot está temporalmente en mantenimiento para mejoras.

Tiempo estimado: {estimated_time}

Por favor, vuelve a intentar más tarde.""",

    "user_blocked": """🚫 <b>Acceso Restringido</b>

Tu acceso al bot ha sido temporalmente restringido.

Razón: {reason}

Para más información, contacta al administrador.""",

    "invalid_command": """❓ <b>Comando no reconocido</b>

No entiendo ese comando. 

Escribe /help para ver los comandos disponibles o /start para comenzar.""",

    "conversation_expired": """⏰ <b>Conversación expirada</b>

Tu conversación se ha cerrado por inactividad.

Escribe /start para comenzar una nueva consulta.""",

    "pdf_generating": """📄 <b>Generando PDF...</b>

Creando tu plan nutricional en formato PDF. Esto puede tomar unos segundos.

⏳ Por favor, espera...""",

    "pdf_ready": """📄 <b>PDF generado exitosamente</b>

Tu plan nutricional está listo. Te lo envío ahora.""",

    "pdf_error": """📄 <b>Error al generar PDF</b>

Hubo un problema al crear el documento. Por favor, intenta nuevamente.

Si el problema persiste, contacta al administrador.""",

    # User information
    "user_info": """<b>👤 Mi Información</b>

<b>Datos registrados:</b>
• Nombre: {name}
• Total de planes: {total_plans}
• Último plan: {last_plan}
• Miembro desde: {member_since}

<b>Configuración:</b>
• Idioma: {language}
• Notificaciones: {notifications}

¿Quieres actualizar algún dato?""",

    "user_history": """<b>📊 Historial de Planes</b>

<b>Tus planes generados:</b>

{plan_history}

<b>Estadísticas:</b>
• Total de planes: {total_plans}
• Reemplazos realizados: {total_replacements}
• Controles realizados: {total_controls}

¿Quieres ver algún plan específico?""",

    # Confirmation messages
    "confirm_generation": """<b>¿Confirmas la generación del plan?</b>

Estoy listo para generar tu plan nutricional personalizado con toda la información que me proporcionaste.

¿Procedemos?""",

    "confirm_replacement": """<b>¿Confirmas el reemplazo?</b>

Estoy listo para reemplazar la comida seleccionada manteniendo las mismas calorías y macronutrientes.

¿Procedemos?""",

    "confirm_cancel": """<b>¿Seguro que quieres cancelar?</b>

Se perderá toda la información ingresada hasta ahora.

¿Estás seguro?""",

    # Validation messages
    "validation_name": """❌ <b>Nombre inválido</b>

El nombre debe tener entre 2 y 50 caracteres y contener solo letras y espacios.

Por favor, ingresa un nombre válido.""",

    "validation_age": """❌ <b>Edad inválida</b>

La edad debe ser un número entre 16 y 80 años.

Por favor, ingresa una edad válida.""",

    "validation_weight": """❌ <b>Peso inválido</b>

El peso debe ser un número entre 40 y 200 kg.

Por favor, ingresa un peso válido (ej: 70.5).""",

    "validation_height": """❌ <b>Altura inválida</b>

La altura debe ser un número entre 140 y 220 cm.

Por favor, ingresa una altura válida (ej: 170).""",

    "validation_duration": """❌ <b>Duración inválida</b>

La duración debe ser un número entre 15 y 300 minutos.

Por favor, ingresa una duración válida.""",

    # Skip messages
    "skip_supplements": """⏭️ <b>Suplementos omitidos</b>

Continuamos sin información de suplementos.""",

    "skip_pathologies": """⏭️ <b>Patologías omitidas</b>

Continuamos sin información de patologías.""",

    "skip_preferences": """⏭️ <b>Preferencias omitidas</b>

Continuamos sin preferencias específicas.""",

    "skip_schedule": """⏭️ <b>Horarios omitidos</b>

Utilizaremos horarios estándar.""",

    "skip_notes": """⏭️ <b>Notas omitidas</b>

Continuamos sin notas adicionales.""",

    # Progress messages
    "progress_10": """📊 <b>Progreso: 10%</b>

Información personal recopilada.""",

    "progress_25": """📊 <b>Progreso: 25%</b>

Datos físicos completados.""",

    "progress_50": """📊 <b>Progreso: 50%</b>

Objetivos y actividad definidos.""",

    "progress_75": """📊 <b>Progreso: 75%</b>

Preferencias alimentarias configuradas.""",

    "progress_90": """📊 <b>Progreso: 90%</b>

Configuración de comidas completada.""",

    "progress_100": """📊 <b>Progreso: 100%</b>

Toda la información recopilada. ¡Listo para generar tu plan!""",

    # Admin messages
    "admin_menu": """<b>🔧 Panel de Administración</b>

Selecciona una opción:""",

    "admin_unauthorized": """🚫 <b>No autorizado</b>

No tienes permisos para acceder al panel de administración.""",

    "admin_stats": """<b>📊 Estadísticas del Sistema</b>

<b>Usuarios:</b>
• Total: {total_users}
• Activos: {active_users}
• Nuevos (mes): {new_users}

<b>Planes:</b>
• Total generados: {total_plans}
• Hoy: {plans_today}
• Promedio diario: {avg_daily_plans}

<b>Sistema:</b>
• Uptime: {uptime}
• Memoria: {memory_usage}
• Procesamiento: {cpu_usage}""",

    # Tips and suggestions
    "tip_hydration": """💧 <b>Consejo:</b> Recuerda beber al menos 2 litros de agua al día para optimizar tu metabolismo.""",

    "tip_meal_timing": """⏰ <b>Consejo:</b> Trata de mantener horarios regulares de comida para mejor digestión.""",

    "tip_preparation": """👨‍🍳 <b>Consejo:</b> Puedes preparar las comidas con anticipación para facilitar tu rutina.""",

    "suggestion_activity": """🏃 <b>Sugerencia:</b> Considera aumentar tu actividad física gradualmente para mejores resultados.""",

    "suggestion_variety": """🌈 <b>Sugerencia:</b> Varía los colores de tus vegetales para obtener más nutrientes.""",

    # Seasonal messages
    "seasonal_summer": """☀️ <b>Verano:</b> Incluye más frutas frescas y ensaladas para mantenerte hidratado.""",

    "seasonal_winter": """❄️ <b>Invierno:</b> Aprovecha las sopas y guisos para mantenerte satisfecho y caliente.""",

    # Success celebrations
    "celebration_first_plan": """🎉 <b>¡Felicitaciones!</b> Has generado tu primer plan nutricional personalizado.""",

    "celebration_consistency": """🏆 <b>¡Excelente consistencia!</b> Llevas {days} días siguiendo tu plan.""",

    # Educational content
    "education_macros": """📚 <b>¿Sabías que?</b>

Los macronutrientes son:
• Proteínas: 4 kcal/g
• Carbohidratos: 4 kcal/g  
• Grasas: 9 kcal/g""",

    "education_meal_timing": """📚 <b>¿Sabías que?</b>

Comer cada 3-4 horas ayuda a mantener estables los niveles de energía y glucosa.""",

    # Feedback messages
    "feedback_request": """📝 <b>¿Cómo fue tu experiencia?</b>

Tu opinión es muy valiosa para mejorar el servicio. ¿Podrías calificar del 1 al 5 tu experiencia?""",

    "feedback_thanks": """🙏 <b>¡Gracias por tu feedback!</b>

Tu opinión nos ayuda a mejorar continuamente.""",

    # Loading messages
    "loading_analyzing": """🔍 <b>Analizando tu información...</b>""",
    "loading_calculating": """🧮 <b>Calculando necesidades nutricionales...</b>""",
    "loading_selecting": """🎯 <b>Seleccionando recetas adecuadas...</b>""",
    "loading_generating": """📋 <b>Generando tu plan personalizado...</b>""",
    "loading_formatting": """📄 <b>Preparando documento final...</b>""",
}

# Field labels for forms
FIELD_LABELS = {
    "name": "Nombre",
    "age": "Edad",
    "sex": "Sexo",
    "height": "Altura",
    "weight": "Peso",
    "objective": "Objetivo",
    "activity_type": "Tipo de Actividad",
    "frequency": "Frecuencia",
    "duration": "Duración",
    "peso_tipo": "Tipo de Peso",
    "economic_level": "Nivel Económico",
    "supplements": "Suplementos",
    "pathologies": "Patologías",
    "restrictions": "Restricciones",
    "preferences": "Preferencias",
    "dislikes": "No me gusta",
    "allergies": "Alergias",
    "main_meals": "Comidas Principales",
    "collations": "Colaciones",
    "schedule": "Horarios",
    "notes": "Notas"
}

# Option labels
OPTION_LABELS = {
    "objectives": {
        "mantenimiento": "Mantenimiento",
        "bajar_0.5kg": "Bajar 0.5kg",
        "bajar_1kg": "Bajar 1kg",
        "bajar_2kg": "Bajar 2kg",
        "subir_0.5kg": "Subir 0.5kg",
        "subir_1kg": "Subir 1kg"
    },
    "activities": {
        "sedentario": "Sedentario",
        "caminatas": "Caminatas",
        "pesas": "Pesas",
        "cardio": "Cardio",
        "mixto": "Mixto",
        "deportista": "Deportista"
    },
    "frequencies": {
        "nunca": "Nunca",
        "1_vez_semana": "1 vez por semana",
        "2_veces_semana": "2 veces por semana",
        "3_veces_semana": "3 veces por semana",
        "4_veces_semana": "4 veces por semana",
        "5_veces_semana": "5 veces por semana",
        "diario": "Diario"
    },
    "weight_types": {
        "crudo": "Crudo",
        "cocido": "Cocido"
    },
    "economic_levels": {
        "bajo": "Económico",
        "medio": "Intermedio",
        "alto": "Premium"
    },
    "sex": {
        "M": "Masculino",
        "F": "Femenino"
    }
}

# Time-related messages
TIME_MESSAGES = {
    "morning": "¡Buenos días! ☀️",
    "afternoon": "¡Buenas tardes! 🌤️",
    "evening": "¡Buenas noches! 🌙",
    "dawn": "¡Madrugada! 🌅"
}

# Seasonal greetings
SEASONAL_GREETINGS = {
    "spring": "¡Bienvenida la primavera! 🌸",
    "summer": "¡Que tengas un buen verano! ☀️",
    "autumn": "¡Disfruta el otoño! 🍂",
    "winter": "¡Que tengas un buen invierno! ❄️"
}

# Motivational messages
MOTIVATIONAL_MESSAGES = [
    "¡Cada paso cuenta hacia tu objetivo! 💪",
    "La constancia es la clave del éxito 🔑",
    "¡Estás en el camino correcto! 🎯",
    "Pequeños cambios, grandes resultados 🌟",
    "¡Tu salud es tu mejor inversión! 💎",
    "¡Sigue adelante, lo estás haciendo genial! 🚀",
    "El progreso no siempre es visible, pero siempre está ahí 📈"
]