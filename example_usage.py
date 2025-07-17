"""
Example usage of the Data Processor.
Demonstrates how to process DOCX files and generate embeddings.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from data_processor.main import DataProcessor
from data_processor.embeddings.recipe_embeddings import RecipeEmbeddingsGenerator
from data_processor.validators.recipe_validator import RecipeValidator


def main():
    """Example usage of the data processor."""
    
    # Configuration
    config = {
        'log_level': 'INFO'
    }
    
    print("=== Data Processor Example ===")
    print("This example demonstrates how to use the data processor.")
    print("Make sure you have DOCX files in the 'data/raw' directory.")
    print()
    
    # Initialize the data processor
    processor = DataProcessor(config)
    
    # Define input directory (you can change this to your actual data directory)
    input_dir = "./data/raw"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        print("Please create the directory and add your DOCX files.")
        return
    
    try:
        # Process all DOCX files in the directory
        print(f"Processing DOCX files in: {input_dir}")
        report = processor.process_directory(input_dir)
        
        # Print processing summary
        summary = report['summary']
        print(f"\n=== Processing Summary ===")
        print(f"Total files processed: {summary['total_files_processed']}")
        print(f"Successful files: {summary['successful_files']}")
        print(f"Failed files: {summary['failed_files']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Total recipes: {summary['total_recipes']}")
        print(f"Total equivalencies: {summary['total_equivalencies']}")
        print(f"Processing time: {summary['processing_time']:.2f} seconds")
        
        # Export results
        output_dir = "./data/processed"
        os.makedirs(output_dir, exist_ok=True)
        
        exported_files = processor.export_results(output_dir, ['json', 'report'])
        print(f"\n=== Exported Files ===")
        for format_type, file_path in exported_files.items():
            print(f"{format_type}: {file_path}")
        
        # Get processed recipes
        processed_data = processor.get_processed_data()
        recipes = processed_data.get('recipes', [])
        
        if recipes:
            print(f"\n=== Validation Example ===")
            # Validate recipes
            validator = RecipeValidator()
            validation_results = validator.validate_batch(recipes)
            
            print(f"Validation Summary:")
            print(f"- Valid recipes: {validation_results['summary']['valid_recipes']}")
            print(f"- Recipes with errors: {validation_results['summary']['recipes_with_errors']}")
            print(f"- Recipes with warnings: {validation_results['summary']['recipes_with_warnings']}")
            
            # Generate embeddings example
            print(f"\n=== Embeddings Example ===")
            print("Generating embeddings for recipes...")
            
            # Initialize embeddings generator
            embeddings_generator = RecipeEmbeddingsGenerator()
            
            # Setup ChromaDB
            embeddings_generator.setup_chromadb("./data/embeddings")
            
            # Process recipes in batches
            embedding_results = embeddings_generator.process_recipes_batch(recipes[:10])  # Process first 10 recipes
            
            print(f"Embedding Results:")
            print(f"- Total recipes: {embedding_results['total_recipes']}")
            print(f"- Processed recipes: {embedding_results['processed_recipes']}")
            print(f"- Collection count: {embedding_results['collection_count']}")
            
            # Example search
            print(f"\n=== Search Example ===")
            search_results = embeddings_generator.search_recipes("pollo asado con verduras", n_results=3)
            
            print(f"Search Results for 'pollo asado con verduras':")
            for i, result in enumerate(search_results, 1):
                print(f"{i}. {result['metadata'].get('name', 'Unknown')}")
                print(f"   Category: {result['metadata'].get('category', 'Unknown')}")
                print(f"   Distance: {result['distance']:.4f}")
                print()
        
        print("=== Example completed successfully! ===")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()