"""
Recipe Validator.
Validates recipe data for completeness and consistency.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of validation check."""
    level: ValidationLevel
    field: str
    message: str
    suggested_fix: Optional[str] = None


class RecipeValidator:
    """
    Validates recipe data for completeness and consistency.
    """
    
    def __init__(self):
        self.required_fields = ['name', 'category']
        self.recommended_fields = ['ingredients', 'preparation_steps', 'nutritional_info']
        self.numeric_fields = ['cooking_time', 'prep_time', 'servings']
        
    def validate_recipe(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate a single recipe."""
        results = []
        
        # Check required fields
        results.extend(self._validate_required_fields(recipe))
        
        # Check recommended fields
        results.extend(self._validate_recommended_fields(recipe))
        
        # Check data types
        results.extend(self._validate_data_types(recipe))
        
        # Check content quality
        results.extend(self._validate_content_quality(recipe))
        
        # Check nutritional data
        results.extend(self._validate_nutritional_data(recipe))
        
        # Check ingredients
        results.extend(self._validate_ingredients(recipe))
        
        # Check preparation steps
        results.extend(self._validate_preparation_steps(recipe))
        
        return results
    
    def _validate_required_fields(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate required fields."""
        results = []
        
        for field in self.required_fields:
            if field not in recipe or not recipe[field]:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=field,
                    message=f"Required field '{field}' is missing or empty",
                    suggested_fix=f"Add {field} to recipe"
                ))
        
        return results
    
    def _validate_recommended_fields(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate recommended fields."""
        results = []
        
        for field in self.recommended_fields:
            if field not in recipe or not recipe[field]:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=field,
                    message=f"Recommended field '{field}' is missing or empty",
                    suggested_fix=f"Consider adding {field} to recipe"
                ))
        
        return results
    
    def _validate_data_types(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate data types."""
        results = []
        
        for field in self.numeric_fields:
            if field in recipe and recipe[field] is not None:
                try:
                    value = float(recipe[field])
                    if value < 0:
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            field=field,
                            message=f"Field '{field}' cannot be negative",
                            suggested_fix=f"Use positive value for {field}"
                        ))
                except (ValueError, TypeError):
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        field=field,
                        message=f"Field '{field}' must be numeric",
                        suggested_fix=f"Convert {field} to number"
                    ))
        
        return results
    
    def _validate_content_quality(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate content quality."""
        results = []
        
        # Check recipe name
        name = recipe.get('name', '')
        if name:
            if len(name) < 3:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field='name',
                    message="Recipe name is too short",
                    suggested_fix="Use more descriptive name"
                ))
            elif len(name) > 100:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field='name',
                    message="Recipe name is too long",
                    suggested_fix="Shorten recipe name"
                ))
        
        # Check description
        description = recipe.get('description', '')
        if description and len(description) < 10:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                field='description',
                message="Description is very short",
                suggested_fix="Add more detailed description"
            ))
        
        return results
    
    def _validate_nutritional_data(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate nutritional data."""
        results = []
        
        nutritional_info = recipe.get('nutritional_info', {})
        if not nutritional_info:
            return results
        
        # Check for reasonable calorie values
        if 'calories' in nutritional_info:
            calorie_data = nutritional_info['calories']
            if isinstance(calorie_data, dict) and 'value' in calorie_data:
                calories = calorie_data['value']
                if calories < 0:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        field='nutritional_info.calories',
                        message="Calories cannot be negative",
                        suggested_fix="Check calorie calculation"
                    ))
                elif calories > 2000:  # per 100g
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        field='nutritional_info.calories',
                        message="Calories seem very high",
                        suggested_fix="Verify calorie calculation"
                    ))
        
        # Check macronutrient balance
        macros = ['protein', 'carbs', 'fat']
        macro_values = {}
        
        for macro in macros:
            if macro in nutritional_info:
                macro_data = nutritional_info[macro]
                if isinstance(macro_data, dict) and 'value' in macro_data:
                    macro_values[macro] = macro_data['value']
        
        if len(macro_values) == 3:
            # Check if macros add up reasonably
            total_macro_calories = (
                macro_values['protein'] * 4 +
                macro_values['carbs'] * 4 +
                macro_values['fat'] * 9
            )
            
            if 'calories' in nutritional_info:
                stated_calories = nutritional_info['calories'].get('value', 0)
                if abs(total_macro_calories - stated_calories) > stated_calories * 0.3:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        field='nutritional_info',
                        message="Macronutrient calories don't match total calories",
                        suggested_fix="Verify nutritional calculations"
                    ))
        
        return results
    
    def _validate_ingredients(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate ingredients."""
        results = []
        
        ingredients = recipe.get('ingredients', [])
        if not ingredients:
            return results
        
        for i, ingredient in enumerate(ingredients):
            if not isinstance(ingredient, dict):
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=f'ingredients[{i}]',
                    message="Ingredient must be an object",
                    suggested_fix="Format ingredient as object with name, quantity, unit"
                ))
                continue
            
            # Check ingredient name
            if 'name' not in ingredient or not ingredient['name']:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=f'ingredients[{i}].name',
                    message="Ingredient name is missing",
                    suggested_fix="Add ingredient name"
                ))
            
            # Check quantity and unit consistency
            quantity = ingredient.get('quantity')
            unit = ingredient.get('unit')
            
            if quantity is not None and unit is None:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=f'ingredients[{i}].unit',
                    message="Ingredient has quantity but no unit",
                    suggested_fix="Add unit for quantity"
                ))
            elif quantity is None and unit is not None:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field=f'ingredients[{i}].quantity',
                    message="Ingredient has unit but no quantity",
                    suggested_fix="Add quantity for unit"
                ))
            
            # Check for negative quantities
            if quantity is not None and quantity < 0:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=f'ingredients[{i}].quantity',
                    message="Ingredient quantity cannot be negative",
                    suggested_fix="Use positive quantity"
                ))
        
        return results
    
    def _validate_preparation_steps(self, recipe: Dict[str, Any]) -> List[ValidationResult]:
        """Validate preparation steps."""
        results = []
        
        preparation_steps = recipe.get('preparation_steps', [])
        if not preparation_steps:
            return results
        
        for i, step in enumerate(preparation_steps):
            if not isinstance(step, dict):
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=f'preparation_steps[{i}]',
                    message="Preparation step must be an object",
                    suggested_fix="Format step as object with instruction"
                ))
                continue
            
            # Check instruction
            if 'instruction' not in step or not step['instruction']:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=f'preparation_steps[{i}].instruction',
                    message="Step instruction is missing",
                    suggested_fix="Add instruction text"
                ))
            else:
                instruction = step['instruction']
                if len(instruction) < 5:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        field=f'preparation_steps[{i}].instruction',
                        message="Step instruction is too short",
                        suggested_fix="Add more detailed instruction"
                    ))
            
            # Check step numbering
            if 'step_number' in step:
                step_number = step['step_number']
                if step_number != i + 1:
                    results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        field=f'preparation_steps[{i}].step_number',
                        message="Step number doesn't match position",
                        suggested_fix="Fix step numbering"
                    ))
        
        return results
    
    def validate_batch(self, recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of recipes."""
        all_results = []
        summary = {
            'total_recipes': len(recipes),
            'valid_recipes': 0,
            'recipes_with_errors': 0,
            'recipes_with_warnings': 0,
            'total_errors': 0,
            'total_warnings': 0,
            'total_info': 0
        }
        
        for i, recipe in enumerate(recipes):
            recipe_results = self.validate_recipe(recipe)
            
            # Count validation results
            errors = [r for r in recipe_results if r.level == ValidationLevel.ERROR]
            warnings = [r for r in recipe_results if r.level == ValidationLevel.WARNING]
            info = [r for r in recipe_results if r.level == ValidationLevel.INFO]
            
            summary['total_errors'] += len(errors)
            summary['total_warnings'] += len(warnings)
            summary['total_info'] += len(info)
            
            if errors:
                summary['recipes_with_errors'] += 1
            elif warnings:
                summary['recipes_with_warnings'] += 1
            else:
                summary['valid_recipes'] += 1
            
            # Add to results with recipe index
            for result in recipe_results:
                all_results.append({
                    'recipe_index': i,
                    'recipe_name': recipe.get('name', 'Unknown'),
                    'level': result.level.value,
                    'field': result.field,
                    'message': result.message,
                    'suggested_fix': result.suggested_fix
                })
        
        return {
            'summary': summary,
            'results': all_results
        }
    
    def get_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report."""
        summary = validation_results['summary']
        results = validation_results['results']
        
        report = []
        report.append("RECIPE VALIDATION REPORT")
        report.append("=" * 50)
        report.append(f"Total recipes: {summary['total_recipes']}")
        report.append(f"Valid recipes: {summary['valid_recipes']}")
        report.append(f"Recipes with errors: {summary['recipes_with_errors']}")
        report.append(f"Recipes with warnings: {summary['recipes_with_warnings']}")
        report.append(f"Total errors: {summary['total_errors']}")
        report.append(f"Total warnings: {summary['total_warnings']}")
        report.append(f"Total info: {summary['total_info']}")
        report.append("")
        
        # Group results by level
        errors = [r for r in results if r['level'] == 'error']
        warnings = [r for r in results if r['level'] == 'warning']
        
        if errors:
            report.append("ERRORS:")
            report.append("-" * 20)
            for error in errors:
                report.append(f"Recipe: {error['recipe_name']}")
                report.append(f"Field: {error['field']}")
                report.append(f"Message: {error['message']}")
                if error['suggested_fix']:
                    report.append(f"Fix: {error['suggested_fix']}")
                report.append("")
        
        if warnings:
            report.append("WARNINGS:")
            report.append("-" * 20)
            for warning in warnings:
                report.append(f"Recipe: {warning['recipe_name']}")
                report.append(f"Field: {warning['field']}")
                report.append(f"Message: {warning['message']}")
                if warning['suggested_fix']:
                    report.append(f"Fix: {warning['suggested_fix']}")
                report.append("")
        
        return "\n".join(report)