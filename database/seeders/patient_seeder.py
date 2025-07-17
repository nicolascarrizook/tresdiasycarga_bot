"""
Patient seeder for Sistema Mayra database.
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal

from database.models.patient import Patient, PatientSexEnum, PatientObjectiveEnum, PatientActivityTypeEnum, PatientEconomicLevelEnum
from database.seeders.base import BaseSeeder


class PatientSeeder(BaseSeeder):
    """Seeder for creating initial patients."""
    
    def get_seeder_name(self) -> str:
        return "PatientSeeder"
    
    async def seed(self) -> Dict[str, Any]:
        """Create initial patients."""
        self.log_info("Starting patient seeding...")
        
        # Create test patients
        test_patients = await self.create_test_patients()
        
        return {
            "seeder": self.get_seeder_name(),
            "success": True,
            "created_count": len(self.created_records),
            "test_patients_count": len(test_patients),
            "timestamp": datetime.utcnow()
        }
    
    async def create_test_patients(self) -> List[Patient]:
        """Create test patients for development."""
        test_patients = []
        
        # Patient 1: Weight loss goal
        patient1 = Patient(
            name="María González",
            email="maria.gonzalez@email.com",
            age=28,
            sex=PatientSexEnum.FEMALE,
            height=Decimal("165.0"),
            weight=Decimal("70.0"),
            objective=PatientObjectiveEnum.WEIGHT_LOSS,
            activity_type=PatientActivityTypeEnum.MODERATE,
            economic_level=PatientEconomicLevelEnum.MEDIO,
            target_weight=Decimal("60.0"),
            telegram_user_id=123456789,
            telegram_username="maria_gonzalez",
            telegram_first_name="María",
            telegram_last_name="González",
            telegram_phone="+54911234567",
            telegram_language_code="es",
            initial_weight=Decimal("75.0"),
            weight_history=[
                {"date": "2024-01-01", "weight": 75.0, "notes": "Peso inicial"},
                {"date": "2024-02-01", "weight": 73.0, "notes": "Progreso mes 1"},
                {"date": "2024-03-01", "weight": 70.0, "notes": "Progreso mes 2"}
            ],
            pathologies=["hipertension"],
            supplements=["omega3", "multivitaminas"],
            restrictions=["lactosa"],
            preferences=["vegetales", "pescado"],
            notes="Paciente muy motivada, sigue bien las indicaciones",
            created_at=datetime.utcnow() - timedelta(days=60),
            updated_at=datetime.utcnow() - timedelta(days=1),
            last_conversation_date=datetime.utcnow() - timedelta(days=2),
            conversation_count=15,
            is_active_patient=True,
            search_vector="María González weight loss hipertension vegetales pescado"
        )
        test_patients.append(patient1)
        
        # Patient 2: Muscle gain goal
        patient2 = Patient(
            name="Carlos Rodríguez",
            email="carlos.rodriguez@email.com",
            age=35,
            sex=PatientSexEnum.MALE,
            height=Decimal("180.0"),
            weight=Decimal("75.0"),
            objective=PatientObjectiveEnum.MUSCLE_GAIN,
            activity_type=PatientActivityTypeEnum.INTENSE,
            economic_level=PatientEconomicLevelEnum.ALTO,
            target_weight=Decimal("85.0"),
            telegram_user_id=987654321,
            telegram_username="carlos_rodriguez",
            telegram_first_name="Carlos",
            telegram_last_name="Rodríguez",
            telegram_phone="+54911876543",
            telegram_language_code="es",
            initial_weight=Decimal("70.0"),
            weight_history=[
                {"date": "2024-01-01", "weight": 70.0, "notes": "Peso inicial"},
                {"date": "2024-02-01", "weight": 72.0, "notes": "Ganancia muscular"},
                {"date": "2024-03-01", "weight": 75.0, "notes": "Buen progreso"}
            ],
            pathologies=[],
            supplements=["proteina", "creatina", "bcaa"],
            restrictions=[],
            preferences=["carnes", "pollo", "arroz"],
            notes="Atleta dedicado, entrena 6 días a la semana",
            created_at=datetime.utcnow() - timedelta(days=90),
            updated_at=datetime.utcnow() - timedelta(hours=12),
            last_conversation_date=datetime.utcnow() - timedelta(days=1),
            conversation_count=25,
            is_active_patient=True,
            search_vector="Carlos Rodríguez muscle gain atleta carnes pollo proteina"
        )
        test_patients.append(patient2)
        
        # Patient 3: Maintenance goal
        patient3 = Patient(
            name="Ana Martínez",
            email="ana.martinez@email.com",
            age=42,
            sex=PatientSexEnum.FEMALE,
            height=Decimal("158.0"),
            weight=Decimal("55.0"),
            objective=PatientObjectiveEnum.MAINTENANCE,
            activity_type=PatientActivityTypeEnum.LIGHT,
            economic_level=PatientEconomicLevelEnum.BAJO,
            target_weight=Decimal("55.0"),
            telegram_user_id=456789123,
            telegram_username="ana_martinez",
            telegram_first_name="Ana",
            telegram_last_name="Martínez",
            telegram_phone="+54911345678",
            telegram_language_code="es",
            initial_weight=Decimal("58.0"),
            weight_history=[
                {"date": "2024-01-01", "weight": 58.0, "notes": "Peso inicial"},
                {"date": "2024-02-01", "weight": 56.0, "notes": "Pérdida gradual"},
                {"date": "2024-03-01", "weight": 55.0, "notes": "Peso objetivo alcanzado"}
            ],
            pathologies=["diabetes_tipo2"],
            supplements=["vitamina_d"],
            restrictions=["azucar", "harinas_refinadas"],
            preferences=["verduras", "legumbres"],
            notes="Paciente con diabetes tipo 2, requiere control estricto de carbohidratos",
            created_at=datetime.utcnow() - timedelta(days=120),
            updated_at=datetime.utcnow() - timedelta(days=3),
            last_conversation_date=datetime.utcnow() - timedelta(days=5),
            conversation_count=8,
            is_active_patient=True,
            search_vector="Ana Martínez maintenance diabetes verduras legumbres"
        )
        test_patients.append(patient3)
        
        # Patient 4: Inactive patient
        patient4 = Patient(
            name="Luis Fernández",
            email="luis.fernandez@email.com",
            age=29,
            sex=PatientSexEnum.MALE,
            height=Decimal("175.0"),
            weight=Decimal("80.0"),
            objective=PatientObjectiveEnum.WEIGHT_LOSS,
            activity_type=PatientActivityTypeEnum.SEDENTARY,
            economic_level=PatientEconomicLevelEnum.MEDIO,
            target_weight=Decimal("75.0"),
            telegram_user_id=789123456,
            telegram_username="luis_fernandez",
            telegram_first_name="Luis",
            telegram_last_name="Fernández",
            telegram_phone="+54911456789",
            telegram_language_code="es",
            initial_weight=Decimal("85.0"),
            weight_history=[
                {"date": "2024-01-01", "weight": 85.0, "notes": "Peso inicial"},
                {"date": "2024-01-15", "weight": 83.0, "notes": "Primer control"},
                {"date": "2024-02-01", "weight": 80.0, "notes": "Último registro"}
            ],
            pathologies=[],
            supplements=[],
            restrictions=["gluten"],
            preferences=["pasta", "pizza"],
            notes="Paciente que abandonó el seguimiento, trabajo sedentario",
            created_at=datetime.utcnow() - timedelta(days=150),
            updated_at=datetime.utcnow() - timedelta(days=45),
            last_conversation_date=datetime.utcnow() - timedelta(days=60),
            conversation_count=3,
            is_active_patient=False,
            search_vector="Luis Fernández weight loss sedentary gluten pasta"
        )
        test_patients.append(patient4)
        
        # Patient 5: Elderly patient
        patient5 = Patient(
            name="Elena Vargas",
            email="elena.vargas@email.com",
            age=68,
            sex=PatientSexEnum.FEMALE,
            height=Decimal("160.0"),
            weight=Decimal("65.0"),
            objective=PatientObjectiveEnum.HEALTH_IMPROVEMENT,
            activity_type=PatientActivityTypeEnum.LIGHT,
            economic_level=PatientEconomicLevelEnum.ALTO,
            target_weight=Decimal("63.0"),
            telegram_user_id=321654987,
            telegram_username="elena_vargas",
            telegram_first_name="Elena",
            telegram_last_name="Vargas",
            telegram_phone="+54911567890",
            telegram_language_code="es",
            initial_weight=Decimal("68.0"),
            weight_history=[
                {"date": "2024-01-01", "weight": 68.0, "notes": "Peso inicial"},
                {"date": "2024-02-01", "weight": 66.0, "notes": "Mejora gradual"},
                {"date": "2024-03-01", "weight": 65.0, "notes": "Progreso constante"}
            ],
            pathologies=["osteoporosis", "hipertension"],
            supplements=["calcio", "vitamina_d", "omega3"],
            restrictions=["sal", "grasas_saturadas"],
            preferences=["pescado", "verduras_cocidas", "frutas"],
            notes="Paciente mayor, necesita dieta rica en calcio y baja en sodio",
            created_at=datetime.utcnow() - timedelta(days=80),
            updated_at=datetime.utcnow() - timedelta(hours=6),
            last_conversation_date=datetime.utcnow() - timedelta(days=1),
            conversation_count=12,
            is_active_patient=True,
            search_vector="Elena Vargas health improvement osteoporosis pescado verduras"
        )
        test_patients.append(patient5)
        
        # Patient 6: Young athlete
        patient6 = Patient(
            name="Diego Morales",
            email="diego.morales@email.com",
            age=22,
            sex=PatientSexEnum.MALE,
            height=Decimal("185.0"),
            weight=Decimal("78.0"),
            objective=PatientObjectiveEnum.PERFORMANCE,
            activity_type=PatientActivityTypeEnum.INTENSE,
            economic_level=PatientEconomicLevelEnum.MEDIO,
            target_weight=Decimal("80.0"),
            telegram_user_id=654321789,
            telegram_username="diego_morales",
            telegram_first_name="Diego",
            telegram_last_name="Morales",
            telegram_phone="+54911678901",
            telegram_language_code="es",
            initial_weight=Decimal("76.0"),
            weight_history=[
                {"date": "2024-01-01", "weight": 76.0, "notes": "Peso inicial"},
                {"date": "2024-02-01", "weight": 77.0, "notes": "Ganancia muscular"},
                {"date": "2024-03-01", "weight": 78.0, "notes": "Composición corporal mejorada"}
            ],
            pathologies=[],
            supplements=["proteina", "creatina", "multivitaminas"],
            restrictions=[],
            preferences=["carnes_magras", "arroz", "avena", "frutas"],
            notes="Atleta de alto rendimiento, futbolista amateur",
            created_at=datetime.utcnow() - timedelta(days=45),
            updated_at=datetime.utcnow() - timedelta(hours=3),
            last_conversation_date=datetime.utcnow() - timedelta(hours=8),
            conversation_count=18,
            is_active_patient=True,
            search_vector="Diego Morales performance atleta futbol carnes arroz"
        )
        test_patients.append(patient6)
        
        await self.commit_batch(test_patients, "test patients")
        return test_patients