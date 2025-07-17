"""
Recipe seeder for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta

from database.models.recipe import Recipe, RecipeIngredient, RecipeCategoryEnum, RecipeEconomicLevelEnum, RecipeDifficultyEnum
from database.seeders.base import BaseSeeder


class RecipeSeeder(BaseSeeder):
    """Seeder for creating initial recipes."""
    
    def get_seeder_name(self) -> str:
        return "RecipeSeeder"
    
    async def seed(self) -> Dict[str, Any]:
        """Create initial recipes."""
        self.log_info("Starting recipe seeding...")
        
        # Create breakfast recipes
        breakfast_recipes = await self.create_breakfast_recipes()
        
        # Create lunch recipes
        lunch_recipes = await self.create_lunch_recipes()
        
        # Create dinner recipes
        dinner_recipes = await self.create_dinner_recipes()
        
        # Create snack recipes
        snack_recipes = await self.create_snack_recipes()
        
        return {
            "seeder": self.get_seeder_name(),
            "success": True,
            "created_count": len(self.created_records),
            "breakfast_count": len(breakfast_recipes),
            "lunch_count": len(lunch_recipes),
            "dinner_count": len(dinner_recipes),
            "snack_count": len(snack_recipes),
            "timestamp": datetime.utcnow()
        }
    
    async def create_breakfast_recipes(self) -> List[Recipe]:
        """Create breakfast recipes."""
        breakfast_recipes = []
        
        # Avena con frutas
        avena_frutas = Recipe(
            name="Avena con frutas y canela",
            description="Desayuno nutritivo con avena, frutas frescas y canela",
            category=RecipeCategoryEnum.BREAKFAST,
            subcategory="Cereales",
            economic_level=RecipeEconomicLevelEnum.BAJO,
            difficulty=RecipeDifficultyEnum.EASY,
            servings=1,
            cooking_time=10,
            calories=280,
            protein=8.5,
            carbs=45.0,
            fat=6.2,
            fiber=6.0,
            sugar=15.0,
            sodium=150,
            preparation="1. Cocinar la avena con agua o leche desnatada por 5 minutos.\n2. Agregar canela en polvo.\n3. Servir con frutas frescas cortadas.\n4. Endulzar con miel si se desea.",
            ingredients_text="- 1/2 taza de avena\n- 1 taza de leche desnatada\n- 1 manzana pequeña\n- 1 cucharadita de canela\n- 1 cucharada de miel",
            dietary_restrictions=["vegetarian"],
            allergens=["lactose", "gluten"],
            notes="Excelente fuente de fibra y proteína para comenzar el día",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="avena frutas canela desayuno cereales nutritivo fibra proteína"
        )
        breakfast_recipes.append(avena_frutas)
        
        # Huevos revueltos con verduras
        huevos_verduras = Recipe(
            name="Huevos revueltos con verduras",
            description="Huevos revueltos con espinaca, tomate y cebolla",
            category=RecipeCategoryEnum.BREAKFAST,
            subcategory="Huevos",
            economic_level=RecipeEconomicLevelEnum.MEDIO,
            difficulty=RecipeDifficultyEnum.EASY,
            servings=1,
            cooking_time=8,
            calories=180,
            protein=12.0,
            carbs=6.0,
            fat=12.0,
            fiber=2.0,
            sugar=4.0,
            sodium=200,
            preparation="1. Calentar aceite en sartén.\n2. Saltear cebolla y tomate 2 minutos.\n3. Agregar espinaca y cocinar 1 minuto.\n4. Batir huevos y agregar a la sartén.\n5. Revolver hasta cuajar.",
            ingredients_text="- 2 huevos\n- 1 cucharada de aceite de oliva\n- 1/4 cebolla\n- 1 tomate pequeño\n- 1 taza de espinaca\n- Sal y pimienta",
            dietary_restrictions=["vegetarian", "keto"],
            allergens=["eggs"],
            notes="Alto en proteína y vitaminas",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="huevos revueltos verduras espinaca tomate cebolla proteína"
        )
        breakfast_recipes.append(huevos_verduras)
        
        # Yogurt con granola
        yogurt_granola = Recipe(
            name="Yogurt griego con granola y berries",
            description="Yogurt griego natural con granola casera y frutos rojos",
            category=RecipeCategoryEnum.BREAKFAST,
            subcategory="Lácteos",
            economic_level=RecipeEconomicLevelEnum.ALTO,
            difficulty=RecipeDifficultyEnum.EASY,
            servings=1,
            cooking_time=3,
            calories=320,
            protein=20.0,
            carbs=35.0,
            fat=10.0,
            fiber=5.0,
            sugar=20.0,
            sodium=80,
            preparation="1. Servir el yogurt griego en un bowl.\n2. Agregar granola por encima.\n3. Decorar con frutos rojos frescos.\n4. Rociar con miel si se desea.",
            ingredients_text="- 1 taza de yogurt griego\n- 1/4 taza de granola\n- 1/2 taza de frutos rojos\n- 1 cucharada de miel",
            dietary_restrictions=["vegetarian"],
            allergens=["lactose", "nuts"],
            notes="Excelente fuente de probióticos y antioxidantes",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="yogurt griego granola berries frutos rojos probióticos"
        )
        breakfast_recipes.append(yogurt_granola)
        
        await self.commit_batch(breakfast_recipes, "breakfast recipes")
        return breakfast_recipes
    
    async def create_lunch_recipes(self) -> List[Recipe]:
        """Create lunch recipes."""
        lunch_recipes = []
        
        # Ensalada de pollo
        ensalada_pollo = Recipe(
            name="Ensalada de pollo con aguacate",
            description="Ensalada fresca con pollo grillado, aguacate y vegetales",
            category=RecipeCategoryEnum.LUNCH,
            subcategory="Ensaladas",
            economic_level=RecipeEconomicLevelEnum.MEDIO,
            difficulty=RecipeDifficultyEnum.MEDIUM,
            servings=2,
            cooking_time=20,
            calories=350,
            protein=25.0,
            carbs=15.0,
            fat=20.0,
            fiber=8.0,
            sugar=8.0,
            sodium=300,
            preparation="1. Marinar el pollo con especias y cocinar a la plancha.\n2. Cortar todas las verduras en juliana.\n3. Preparar vinagreta con aceite de oliva y limón.\n4. Mezclar todos los ingredientes y servir.",
            ingredients_text="- 200g pechuga de pollo\n- 1 aguacate\n- 2 tazas de lechugas mixtas\n- 1 tomate\n- 1 pepino\n- 1/2 cebolla morada\n- Aceite de oliva\n- Limón\n- Sal y pimienta",
            dietary_restrictions=["low_carb", "gluten_free"],
            allergens=[],
            notes="Comida completa y balanceada",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="ensalada pollo aguacate vegetales proteína saludable"
        )
        lunch_recipes.append(ensalada_pollo)
        
        # Salmón al horno
        salmon_horno = Recipe(
            name="Salmón al horno con verduras",
            description="Filete de salmón horneado con brócoli y zanahoria",
            category=RecipeCategoryEnum.LUNCH,
            subcategory="Pescados",
            economic_level=RecipeEconomicLevelEnum.ALTO,
            difficulty=RecipeDifficultyEnum.MEDIUM,
            servings=2,
            cooking_time=25,
            calories=420,
            protein=35.0,
            carbs=12.0,
            fat=25.0,
            fiber=4.0,
            sugar=6.0,
            sodium=250,
            preparation="1. Precalentar horno a 200°C.\n2. Marinar salmón con limón y hierbas.\n3. Cortar verduras y condimentar.\n4. Hornear todo junto por 20-25 minutos.",
            ingredients_text="- 2 filetes de salmón\n- 1 taza de brócoli\n- 2 zanahorias\n- Aceite de oliva\n- Limón\n- Tomillo\n- Sal y pimienta",
            dietary_restrictions=["keto", "low_carb", "gluten_free"],
            allergens=["fish"],
            notes="Rico en omega-3 y proteína de alta calidad",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="salmón horno verduras pescado omega3 proteína"
        )
        lunch_recipes.append(salmon_horno)
        
        # Quinoa con verduras
        quinoa_verduras = Recipe(
            name="Bowl de quinoa con verduras asadas",
            description="Quinoa cocida con verduras de temporada asadas",
            category=RecipeCategoryEnum.LUNCH,
            subcategory="Vegetarianos",
            economic_level=RecipeEconomicLevelEnum.MEDIO,
            difficulty=RecipeDifficultyEnum.MEDIUM,
            servings=2,
            cooking_time=30,
            calories=380,
            protein=15.0,
            carbs=55.0,
            fat=12.0,
            fiber=8.0,
            sugar=10.0,
            sodium=200,
            preparation="1. Cocinar quinoa en caldo de verduras.\n2. Cortar verduras y condimentar.\n3. Asar verduras en horno a 200°C por 20 minutos.\n4. Servir quinoa con verduras y aliñar.",
            ingredients_text="- 1 taza de quinoa\n- 1 calabacín\n- 1 pimiento rojo\n- 1 berenjena\n- 1 cebolla\n- Aceite de oliva\n- Caldo de verduras\n- Especias al gusto",
            dietary_restrictions=["vegetarian", "vegan", "gluten_free"],
            allergens=[],
            notes="Proteína completa de origen vegetal",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="quinoa verduras asadas vegetariano vegano proteína"
        )
        lunch_recipes.append(quinoa_verduras)
        
        await self.commit_batch(lunch_recipes, "lunch recipes")
        return lunch_recipes
    
    async def create_dinner_recipes(self) -> List[Recipe]:
        """Create dinner recipes."""
        dinner_recipes = []
        
        # Pechuga de pollo a la plancha
        pollo_plancha = Recipe(
            name="Pechuga de pollo a la plancha con puré de coliflor",
            description="Pechuga de pollo marinada con puré de coliflor cremoso",
            category=RecipeCategoryEnum.DINNER,
            subcategory="Carnes",
            economic_level=RecipeEconomicLevelEnum.MEDIO,
            difficulty=RecipeDifficultyEnum.MEDIUM,
            servings=2,
            cooking_time=30,
            calories=320,
            protein=40.0,
            carbs=10.0,
            fat=12.0,
            fiber=3.0,
            sugar=5.0,
            sodium=400,
            preparation="1. Marinar pollo con especias por 30 minutos.\n2. Cocinar coliflor hasta que esté tierna.\n3. Hacer puré con la coliflor y un poco de leche.\n4. Cocinar pollo a la plancha hasta dorar.\n5. Servir con el puré.",
            ingredients_text="- 2 pechugas de pollo\n- 1 coliflor mediana\n- 1/4 taza de leche desnatada\n- Especias (tomillo, orégano, paprika)\n- Aceite de oliva\n- Sal y pimienta",
            dietary_restrictions=["low_carb", "gluten_free"],
            allergens=["lactose"],
            notes="Cena ligera pero nutritiva",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="pollo plancha coliflor puré proteína cena ligera"
        )
        dinner_recipes.append(pollo_plancha)
        
        # Pescado al vapor
        pescado_vapor = Recipe(
            name="Pescado al vapor con vegetales",
            description="Filete de pescado blanco al vapor con verduras",
            category=RecipeCategoryEnum.DINNER,
            subcategory="Pescados",
            economic_level=RecipeEconomicLevelEnum.MEDIO,
            difficulty=RecipeDifficultyEnum.EASY,
            servings=2,
            cooking_time=20,
            calories=250,
            protein=30.0,
            carbs=8.0,
            fat=8.0,
            fiber=3.0,
            sugar=6.0,
            sodium=200,
            preparation="1. Preparar vaporera con agua hirviendo.\n2. Condimentar pescado con hierbas.\n3. Cortar verduras en juliana.\n4. Cocinar al vapor 15-20 minutos.\n5. Servir con limón.",
            ingredients_text="- 2 filetes de pescado blanco\n- 1 taza de brócoli\n- 1 zanahoria\n- 1 calabacín\n- Hierbas frescas\n- Limón\n- Sal y pimienta",
            dietary_restrictions=["low_calorie", "low_carb", "gluten_free"],
            allergens=["fish"],
            notes="Cocción saludable que preserva nutrientes",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="pescado vapor verduras saludable bajo calorías"
        )
        dinner_recipes.append(pescado_vapor)
        
        await self.commit_batch(dinner_recipes, "dinner recipes")
        return dinner_recipes
    
    async def create_snack_recipes(self) -> List[Recipe]:
        """Create snack recipes."""
        snack_recipes = []
        
        # Batido de proteínas
        batido_proteinas = Recipe(
            name="Batido de proteínas con banana",
            description="Batido nutritivo con proteína en polvo y banana",
            category=RecipeCategoryEnum.SNACK,
            subcategory="Bebidas",
            economic_level=RecipeEconomicLevelEnum.MEDIO,
            difficulty=RecipeDifficultyEnum.EASY,
            servings=1,
            cooking_time=5,
            calories=220,
            protein=25.0,
            carbs=20.0,
            fat=4.0,
            fiber=3.0,
            sugar=18.0,
            sodium=100,
            preparation="1. Pelar y cortar la banana.\n2. Agregar todos los ingredientes a la licuadora.\n3. Licuar hasta obtener consistencia cremosa.\n4. Servir inmediatamente.",
            ingredients_text="- 1 banana\n- 1 scoop de proteína en polvo\n- 1 taza de leche de almendras\n- 1 cucharada de mantequilla de almendras\n- Hielo",
            dietary_restrictions=["vegetarian", "post_workout"],
            allergens=["nuts"],
            notes="Ideal para después del entrenamiento",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="batido proteínas banana post entrenamiento"
        )
        snack_recipes.append(batido_proteinas)
        
        # Hummus con verduras
        hummus_verduras = Recipe(
            name="Hummus casero con bastones de verduras",
            description="Hummus de garbanzos con verduras crujientes",
            category=RecipeCategoryEnum.SNACK,
            subcategory="Vegetarianos",
            economic_level=RecipeEconomicLevelEnum.BAJO,
            difficulty=RecipeDifficultyEnum.EASY,
            servings=4,
            cooking_time=10,
            calories=150,
            protein=6.0,
            carbs=18.0,
            fat=6.0,
            fiber=5.0,
            sugar=4.0,
            sodium=200,
            preparation="1. Escurrir garbanzos y reservar líquido.\n2. Procesar garbanzos con tahini y limón.\n3. Agregar líquido hasta consistencia deseada.\n4. Cortar verduras en bastones.\n5. Servir con verduras.",
            ingredients_text="- 1 lata de garbanzos\n- 2 cucharadas de tahini\n- 1 limón\n- 1 diente de ajo\n- Zanahorias\n- Apio\n- Pepino\n- Aceite de oliva",
            dietary_restrictions=["vegetarian", "vegan", "gluten_free"],
            allergens=["sesame"],
            notes="Snack saludable rico en fibra",
            is_validated=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            search_vector="hummus garbanzos verduras snack vegetariano"
        )
        snack_recipes.append(hummus_verduras)
        
        await self.commit_batch(snack_recipes, "snack recipes")
        return snack_recipes