"""
Main Data Processor.
Orchestrates the complete data processing pipeline for DOCX files.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import traceback

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from data_processor.parsers.base_parser import BaseDocxParser
from data_processor.parsers.almuerzos_cenas_parser import AlmuerzosECenasParser
from data_processor.parsers.desayunos_meriendas_parser import DesayunosYMeriendasParser
from data_processor.parsers.equivalencias_parser import EquivalenciasParser
from data_processor.parsers.recetas_detalladas_parser import RecetasDetalladasParser

from data_processor.extractors.nutritional_extractor import NutritionalExtractor
from data_processor.extractors.ingredient_extractor import IngredientExtractor
from data_processor.extractors.preparation_extractor import PreparationExtractor
from data_processor.extractors.portion_extractor import PortionExtractor
from data_processor.extractors.category_classifier import CategoryClassifier

logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Enum for processing status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ProcessingResult:
    """Result of processing a single file."""
    file_path: str
    file_type: str
    status: ProcessingStatus
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    processing_time: float
    records_processed: int
    metadata: Dict[str, Any]


class DataProcessor:
    """
    Main data processor that orchestrates the complete pipeline.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data processor."""
        self.config = config or {}
        self.setup_logging()
        
        # Initialize extractors
        self.nutritional_extractor = NutritionalExtractor()
        self.ingredient_extractor = IngredientExtractor()
        self.preparation_extractor = PreparationExtractor()
        self.portion_extractor = PortionExtractor()
        self.category_classifier = CategoryClassifier()
        
        # Initialize parsers
        self.parsers = {
            'almuerzos_cenas': AlmuerzosECenasParser,
            'desayunos_meriendas': DesayunosYMeriendasParser,
            'equivalencias': EquivalenciasParser,
            'recetas_detalladas': RecetasDetalladasParser
        }
        
        # Processing stats
        self.processing_stats = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_recipes': 0,
            'total_equivalencies': 0,
            'start_time': None,
            'end_time': None,
            'processing_time': 0
        }
        
        # Results storage
        self.results = []
        self.processed_data = {
            'recipes': [],
            'equivalencies': [],
            'processed_files': [],
            'errors': []
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('log_level', 'INFO')
        log_format = self.config.get('log_format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('data_processor.log')
            ]
        )
    
    def process_directory(self, directory_path: str, 
                         file_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Process all DOCX files in a directory."""
        start_time = datetime.now()
        self.processing_stats['start_time'] = start_time
        
        logger.info(f"Starting processing of directory: {directory_path}")
        
        try:
            # Find DOCX files
            docx_files = self._find_docx_files(directory_path, file_patterns)
            self.processing_stats['total_files'] = len(docx_files)
            
            logger.info(f"Found {len(docx_files)} DOCX files to process")
            
            # Process each file
            for file_path in docx_files:
                result = self.process_file(file_path)
                self.results.append(result)
                
                if result.status == ProcessingStatus.COMPLETED:
                    self.processing_stats['successful_files'] += 1
                    if result.data:
                        self._integrate_result(result)
                else:
                    self.processing_stats['failed_files'] += 1
                    self.processed_data['errors'].append({
                        'file': file_path,
                        'error': result.error,
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Log progress
                progress = (len(self.results) / len(docx_files)) * 100
                logger.info(f"Progress: {progress:.1f}% ({len(self.results)}/{len(docx_files)})")
            
            # Finalize processing
            end_time = datetime.now()
            self.processing_stats['end_time'] = end_time
            self.processing_stats['processing_time'] = (end_time - start_time).total_seconds()
            
            logger.info(f"Processing completed in {self.processing_stats['processing_time']:.2f} seconds")
            
            return self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Error processing directory: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def process_file(self, file_path: str) -> ProcessingResult:
        """Process a single DOCX file."""
        start_time = datetime.now()
        
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Determine file type
            file_type = self._determine_file_type(file_path)
            
            if not file_type:
                return ProcessingResult(
                    file_path=file_path,
                    file_type='unknown',
                    status=ProcessingStatus.SKIPPED,
                    data=None,
                    error="Could not determine file type",
                    processing_time=0,
                    records_processed=0,
                    metadata={}
                )
            
            # Get appropriate parser
            parser_class = self.parsers.get(file_type)
            if not parser_class:
                return ProcessingResult(
                    file_path=file_path,
                    file_type=file_type,
                    status=ProcessingStatus.ERROR,
                    data=None,
                    error=f"No parser available for file type: {file_type}",
                    processing_time=0,
                    records_processed=0,
                    metadata={}
                )
            
            # Parse the file
            parser = parser_class(file_path)
            parsed_data = parser.parse()
            
            # Process the parsed data
            processed_data = self._process_parsed_data(parsed_data, file_type)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Count records
            records_processed = self._count_records(processed_data)
            
            logger.info(f"Successfully processed {file_path} ({records_processed} records)")
            
            return ProcessingResult(
                file_path=file_path,
                file_type=file_type,
                status=ProcessingStatus.COMPLETED,
                data=processed_data,
                error=None,
                processing_time=processing_time,
                records_processed=records_processed,
                metadata={
                    'parser_used': parser_class.__name__,
                    'file_size': os.path.getsize(file_path),
                    'processed_timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error processing {file_path}: {str(e)}"
            
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            return ProcessingResult(
                file_path=file_path,
                file_type=file_type if 'file_type' in locals() else 'unknown',
                status=ProcessingStatus.ERROR,
                data=None,
                error=error_msg,
                processing_time=processing_time,
                records_processed=0,
                metadata={}
            )
    
    def _find_docx_files(self, directory_path: str, 
                        file_patterns: Optional[List[str]] = None) -> List[str]:
        """Find all DOCX files in directory."""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Default patterns
        if not file_patterns:
            file_patterns = ['*.docx', '*.DOCX']
        
        docx_files = []
        for pattern in file_patterns:
            docx_files.extend(directory.glob(pattern))
        
        # Convert to strings and sort
        docx_files = sorted([str(f) for f in docx_files])
        
        return docx_files
    
    def _determine_file_type(self, file_path: str) -> Optional[str]:
        """Determine file type based on filename and content."""
        filename = Path(file_path).stem.lower()
        
        # Check filename patterns
        if any(keyword in filename for keyword in ['almuerzo', 'cena', 'lunch', 'dinner']):
            return 'almuerzos_cenas'
        elif any(keyword in filename for keyword in ['desayuno', 'merienda', 'breakfast', 'snack']):
            return 'desayunos_meriendas'
        elif any(keyword in filename for keyword in ['equivalencia', 'equivalent', 'intercambio']):
            return 'equivalencias'
        elif any(keyword in filename for keyword in ['receta', 'recipe', 'detallada']):
            return 'recetas_detalladas'
        
        # If filename doesn't match, try to analyze content
        try:
            parser = BaseDocxParser(file_path)
            parser.load_document()
            
            # Analyze tables and paragraphs
            tables_data = parser.extract_tables_data()
            paragraphs_data = parser.extract_paragraphs_data()
            
            # Combine text for analysis
            text_content = ""
            for table_data in tables_data:
                text_content += " ".join(table_data.get('headers', []))
            for paragraph_data in paragraphs_data:
                text_content += " " + paragraph_data.get('text', '')
            
            text_content = text_content.lower()
            
            # Check content patterns
            if any(keyword in text_content for keyword in ['pollo', 'carne', 'pescado', 'ensalada']):
                return 'almuerzos_cenas'
            elif any(keyword in text_content for keyword in ['dulce', 'salado', 'colacion']):
                return 'desayunos_meriendas'
            elif any(keyword in text_content for keyword in ['equivale', 'intercambio', 'porcion']):
                return 'equivalencias'
            elif any(keyword in text_content for keyword in ['ingrediente', 'preparacion', 'paso']):
                return 'recetas_detalladas'
            
        except Exception as e:
            logger.warning(f"Could not analyze content of {file_path}: {str(e)}")
        
        return None
    
    def _process_parsed_data(self, parsed_data: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Process parsed data through extractors and transformers."""
        processed_data = parsed_data.copy()
        
        # Extract and enrich data based on type
        if file_type in ['almuerzos_cenas', 'desayunos_meriendas', 'recetas_detalladas']:
            processed_data = self._process_recipes(processed_data)
        elif file_type == 'equivalencias':
            processed_data = self._process_equivalencies(processed_data)
        
        return processed_data
    
    def _process_recipes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process recipe data through extractors."""
        recipes = data.get('recipes', [])
        processed_recipes = []
        
        for recipe in recipes:
            try:
                processed_recipe = self._process_single_recipe(recipe)
                processed_recipes.append(processed_recipe)
            except Exception as e:
                logger.error(f"Error processing recipe {recipe.get('name', 'unknown')}: {str(e)}")
                continue
        
        data['recipes'] = processed_recipes
        return data
    
    def _process_single_recipe(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single recipe through all extractors."""
        processed_recipe = recipe.copy()
        
        # Extract ingredients if not already processed
        if 'ingredients' not in processed_recipe or not processed_recipe['ingredients']:
            ingredient_text = recipe.get('ingredients_text', '')
            if ingredient_text:
                ingredients = self.ingredient_extractor.extract_from_text(ingredient_text)
                processed_recipe['ingredients'] = self.ingredient_extractor.standardize_ingredients(ingredients)
        
        # Extract preparation steps if not already processed
        if 'preparation_steps' not in processed_recipe or not processed_recipe['preparation_steps']:
            preparation_text = recipe.get('preparation', '')
            if preparation_text:
                steps = self.preparation_extractor.extract_from_text(preparation_text)
                processed_recipe['preparation_steps'] = self.preparation_extractor.standardize_steps(steps)
        
        # Extract nutritional information
        nutrition_text = f"{recipe.get('name', '')} {recipe.get('description', '')}"
        nutritional_info = self.nutritional_extractor.extract_from_text(nutrition_text)
        
        # If no nutritional info from text, try to calculate from ingredients
        if not nutritional_info and processed_recipe.get('ingredients'):
            nutritional_info = self.nutritional_extractor.extract_from_ingredients(processed_recipe['ingredients'])
        
        if nutritional_info:
            processed_recipe['nutritional_info'] = self.nutritional_extractor.export_to_dict(nutritional_info)
        
        # Extract portion information
        portion_text = f"{recipe.get('portion_size', '')} {recipe.get('servings', '')}"
        portions = self.portion_extractor.extract_from_text(portion_text)
        if portions:
            processed_recipe['portions'] = self.portion_extractor.standardize_portions(portions)
        
        # Classify recipe
        classification = self.category_classifier.classify_recipe(processed_recipe)
        processed_recipe['classification'] = self.category_classifier.export_classification(classification)
        
        # Add processing metadata
        processed_recipe['processing_metadata'] = {
            'processed_at': datetime.now().isoformat(),
            'extractors_used': ['ingredient', 'preparation', 'nutritional', 'portion', 'classification'],
            'version': '1.0'
        }
        
        return processed_recipe
    
    def _process_equivalencies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process equivalency data."""
        equivalencies = data.get('equivalencies', [])
        processed_equivalencies = []
        
        for equivalency in equivalencies:
            try:
                processed_equivalency = self._process_single_equivalency(equivalency)
                processed_equivalencies.append(processed_equivalency)
            except Exception as e:
                logger.error(f"Error processing equivalency {equivalency.get('food_name', 'unknown')}: {str(e)}")
                continue
        
        data['equivalencies'] = processed_equivalencies
        return data
    
    def _process_single_equivalency(self, equivalency: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single equivalency."""
        processed_equivalency = equivalency.copy()
        
        # Extract portion information
        portion_text = f"{equivalency.get('portion', '')} {equivalency.get('weight_grams', '')}"
        portions = self.portion_extractor.extract_from_text(portion_text)
        if portions:
            processed_equivalency['portions'] = self.portion_extractor.standardize_portions(portions)
        
        # Classify equivalency
        classification = self.category_classifier.classify_ingredient(processed_equivalency)
        processed_equivalency['classification'] = self.category_classifier.export_classification(classification)
        
        # Add processing metadata
        processed_equivalency['processing_metadata'] = {
            'processed_at': datetime.now().isoformat(),
            'extractors_used': ['portion', 'classification'],
            'version': '1.0'
        }
        
        return processed_equivalency
    
    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count the number of records in processed data."""
        count = 0
        
        if 'recipes' in data:
            count += len(data['recipes'])
        
        if 'equivalencies' in data:
            count += len(data['equivalencies'])
        
        return count
    
    def _integrate_result(self, result: ProcessingResult):
        """Integrate processing result into main data structure."""
        if not result.data:
            return
        
        # Add recipes
        if 'recipes' in result.data:
            recipes = result.data['recipes']
            self.processed_data['recipes'].extend(recipes)
            self.processing_stats['total_recipes'] += len(recipes)
        
        # Add equivalencies
        if 'equivalencies' in result.data:
            equivalencies = result.data['equivalencies']
            self.processed_data['equivalencies'].extend(equivalencies)
            self.processing_stats['total_equivalencies'] += len(equivalencies)
        
        # Add file info
        self.processed_data['processed_files'].append({
            'file_path': result.file_path,
            'file_type': result.file_type,
            'records_processed': result.records_processed,
            'processing_time': result.processing_time,
            'metadata': result.metadata
        })
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final processing report."""
        report = {
            'summary': {
                'total_files_processed': self.processing_stats['total_files'],
                'successful_files': self.processing_stats['successful_files'],
                'failed_files': self.processing_stats['failed_files'],
                'total_recipes': self.processing_stats['total_recipes'],
                'total_equivalencies': self.processing_stats['total_equivalencies'],
                'processing_time': self.processing_stats['processing_time'],
                'success_rate': (self.processing_stats['successful_files'] / self.processing_stats['total_files']) * 100 if self.processing_stats['total_files'] > 0 else 0
            },
            'processing_details': {
                'start_time': self.processing_stats['start_time'].isoformat() if self.processing_stats['start_time'] else None,
                'end_time': self.processing_stats['end_time'].isoformat() if self.processing_stats['end_time'] else None,
                'processed_files': self.processed_data['processed_files'],
                'errors': self.processed_data['errors']
            },
            'data_summary': {
                'recipes_by_category': self._summarize_recipes_by_category(),
                'equivalencies_by_group': self._summarize_equivalencies_by_group(),
                'nutritional_coverage': self._calculate_nutritional_coverage(),
                'quality_metrics': self._calculate_quality_metrics()
            },
            'processed_data': self.processed_data
        }
        
        return report
    
    def _summarize_recipes_by_category(self) -> Dict[str, int]:
        """Summarize recipes by category."""
        categories = {}
        
        for recipe in self.processed_data['recipes']:
            category = recipe.get('classification', {}).get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        
        return categories
    
    def _summarize_equivalencies_by_group(self) -> Dict[str, int]:
        """Summarize equivalencies by food group."""
        groups = {}
        
        for equivalency in self.processed_data['equivalencies']:
            group = equivalency.get('food_group', 'unknown')
            groups[group] = groups.get(group, 0) + 1
        
        return groups
    
    def _calculate_nutritional_coverage(self) -> Dict[str, float]:
        """Calculate nutritional information coverage."""
        total_recipes = len(self.processed_data['recipes'])
        if total_recipes == 0:
            return {}
        
        coverage = {}
        nutrients = ['calories', 'protein', 'carbs', 'fat', 'fiber']
        
        for nutrient in nutrients:
            count = 0
            for recipe in self.processed_data['recipes']:
                nutritional_info = recipe.get('nutritional_info', {})
                if nutrient in nutritional_info and nutritional_info[nutrient].get('value'):
                    count += 1
            
            coverage[nutrient] = (count / total_recipes) * 100
        
        return coverage
    
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate data quality metrics."""
        metrics = {
            'avg_confidence': 0.0,
            'complete_recipes': 0.0,
            'recipes_with_ingredients': 0.0,
            'recipes_with_preparation': 0.0,
            'recipes_with_nutrition': 0.0
        }
        
        total_recipes = len(self.processed_data['recipes'])
        if total_recipes == 0:
            return metrics
        
        confidence_sum = 0
        complete_count = 0
        ingredients_count = 0
        preparation_count = 0
        nutrition_count = 0
        
        for recipe in self.processed_data['recipes']:
            # Confidence
            classification = recipe.get('classification', {})
            confidence = classification.get('confidence', 0)
            confidence_sum += confidence
            
            # Completeness
            has_ingredients = bool(recipe.get('ingredients'))
            has_preparation = bool(recipe.get('preparation_steps'))
            has_nutrition = bool(recipe.get('nutritional_info'))
            
            if has_ingredients:
                ingredients_count += 1
            if has_preparation:
                preparation_count += 1
            if has_nutrition:
                nutrition_count += 1
            
            if has_ingredients and has_preparation and has_nutrition:
                complete_count += 1
        
        metrics['avg_confidence'] = confidence_sum / total_recipes
        metrics['complete_recipes'] = (complete_count / total_recipes) * 100
        metrics['recipes_with_ingredients'] = (ingredients_count / total_recipes) * 100
        metrics['recipes_with_preparation'] = (preparation_count / total_recipes) * 100
        metrics['recipes_with_nutrition'] = (nutrition_count / total_recipes) * 100
        
        return metrics
    
    def export_results(self, output_dir: str, formats: List[str] = None) -> Dict[str, str]:
        """Export processing results to various formats."""
        if formats is None:
            formats = ['json']
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        exported_files = {}
        
        for format_type in formats:
            if format_type == 'json':
                file_path = output_path / 'processed_data.json'
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.processed_data, f, ensure_ascii=False, indent=2)
                exported_files['json'] = str(file_path)
            
            elif format_type == 'report':
                report = self._generate_final_report()
                file_path = output_path / 'processing_report.json'
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                exported_files['report'] = str(file_path)
        
        return exported_files
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return self.processing_stats.copy()
    
    def get_processed_data(self) -> Dict[str, Any]:
        """Get processed data."""
        return self.processed_data.copy()


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process DOCX files for nutrition data')
    parser.add_argument('input_dir', help='Directory containing DOCX files')
    parser.add_argument('--output-dir', default='./output', help='Output directory')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    parser.add_argument('--export-formats', nargs='+', default=['json', 'report'], 
                       help='Export formats')
    
    args = parser.parse_args()
    
    # Configure processor
    config = {
        'log_level': args.log_level
    }
    
    # Create processor and process directory
    processor = DataProcessor(config)
    
    try:
        logger.info(f"Starting processing of directory: {args.input_dir}")
        report = processor.process_directory(args.input_dir)
        
        # Export results
        exported_files = processor.export_results(args.output_dir, args.export_formats)
        
        # Print summary
        summary = report['summary']
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total files processed: {summary['total_files_processed']}")
        print(f"Successful files: {summary['successful_files']}")
        print(f"Failed files: {summary['failed_files']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total recipes: {summary['total_recipes']}")
        print(f"Total equivalencies: {summary['total_equivalencies']}")
        print(f"Processing time: {summary['processing_time']:.2f} seconds")
        print(f"\nExported files:")
        for format_type, file_path in exported_files.items():
            print(f"  {format_type}: {file_path}")
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()