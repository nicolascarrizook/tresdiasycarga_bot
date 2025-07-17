# Database Seeders

This directory contains database seeders for the Sistema Mayra project. Seeders are used to populate the database with initial data for development, testing, and production environments.

## Available Seeders

### 1. UserSeeder
Creates initial users including:
- Admin user (admin@sistemamayra.com)
- API service user for system integration
- Test users for different roles (nutritionist, viewer, inactive)

### 2. RecipeSeeder
Creates initial recipes including:
- Breakfast recipes (avena, huevos, yogurt)
- Lunch recipes (ensaladas, salmón, quinoa)
- Dinner recipes (pollo, pescado)
- Snack recipes (batidos, hummus)

### 3. PatientSeeder
Creates test patients with different profiles:
- Weight loss patients
- Muscle gain patients
- Maintenance patients
- Elderly patients
- Young athletes
- Inactive patients

### 4. PlanSeeder
Creates sample nutrition plans:
- Active weight loss plans
- Muscle gain plans
- Completed plans
- Plans with different statuses and adherence levels

### 5. ConversationSeeder
Creates sample bot conversations:
- Completed new patient onboarding
- Active control conversations
- Meal replacement conversations
- Failed conversations

### 6. EmbeddingSeeder
Creates vector embeddings for RAG (Retrieval-Augmented Generation):
- Recipe embeddings for semantic search
- Nutrition knowledge embeddings
- FAQ embeddings for common questions

## Usage

### Run All Seeders
```bash
python -m database.seeders.main_seeder
```

### Run Basic Seeders Only (Users and Recipes)
```bash
python -m database.seeders.main_seeder basic
```

### Run Test Data Seeders Only
```bash
python -m database.seeders.main_seeder test
```

## Programmatic Usage

```python
from database.seeders import run_all_seeders, run_basic_seeders, run_test_data_seeders

# Run all seeders
result = await run_all_seeders()

# Run basic seeders only
result = await run_basic_seeders()

# Run test data seeders only
result = await run_test_data_seeders()
```

## Individual Seeder Usage

```python
from database.seeders import UserSeeder, RecipeSeeder
from database.utils.connection import get_database_connection

# Get database connection
db_connection = get_database_connection()

# Create and run individual seeder
user_seeder = UserSeeder(db_connection.get_async_session())
result = await user_seeder.seed()
```

## Data Created

### Users
- 1 Admin user
- 1 API service user
- 3 Test users (nutritionist, viewer, inactive)

### Recipes
- 3 Breakfast recipes
- 3 Lunch recipes
- 2 Dinner recipes
- 2 Snack recipes

### Patients
- 6 Test patients with different profiles and goals

### Plans
- 3 Test plans with different statuses and meal configurations

### Conversations
- 5 Test conversations showing different conversation flows

### Embeddings
- 3 Recipe embeddings
- 3 Nutrition knowledge embeddings
- 3 FAQ embeddings

## Important Notes

1. **Database State**: Seeders assume a clean database with tables already created by migrations.

2. **Dependencies**: Some seeders depend on data from other seeders:
   - PlanSeeder depends on PatientSeeder
   - ConversationSeeder depends on PatientSeeder
   - EmbeddingSeeder references RecipeSeeder data

3. **Production Usage**: Be careful when running seeders in production. They are primarily designed for development and testing.

4. **Data Consistency**: All seeded data includes proper timestamps, relationships, and realistic values.

5. **Error Handling**: Seeders include proper error handling and logging. Check the output for any failed operations.

## Testing

Each seeder includes comprehensive test data that covers:
- Different user scenarios
- Various recipe types and nutritional profiles
- Diverse patient demographics and goals
- Multiple conversation flows
- Rich embedding content for RAG functionality

The seeded data is designed to be representative of real-world usage patterns and provides a solid foundation for development and testing activities.