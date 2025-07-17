"""
Recipe Embeddings Generator.
Creates embeddings for recipes using sentence-transformers.
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class RecipeEmbeddingsGenerator:
    """
    Generates embeddings for recipes using sentence-transformers.
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize the embeddings generator."""
        self.model_name = model_name
        self.model = None
        self.chroma_client = None
        self.collection = None
        self.load_model()
        
    def load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def setup_chromadb(self, persist_directory: str = "./chroma_db"):
        """Setup ChromaDB client and collection."""
        try:
            logger.info(f"Setting up ChromaDB in: {persist_directory}")
            
            # Create persist directory if it doesn't exist
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="recipes",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up ChromaDB: {str(e)}")
            raise
    
    def generate_recipe_text(self, recipe: Dict[str, Any]) -> str:
        """Generate searchable text from recipe data."""
        text_parts = []
        
        # Add recipe name
        if recipe.get('name'):
            text_parts.append(f"Receta: {recipe['name']}")
        
        # Add description
        if recipe.get('description'):
            text_parts.append(f"Descripción: {recipe['description']}")
        
        # Add category and subcategory
        classification = recipe.get('classification', {})
        if classification.get('category'):
            text_parts.append(f"Categoría: {classification['category']}")
        if classification.get('subcategory'):
            text_parts.append(f"Subcategoría: {classification['subcategory']}")
        
        # Add ingredients
        ingredients = recipe.get('ingredients', [])
        if ingredients:
            ingredient_names = [ing.get('name', '') for ing in ingredients if ing.get('name')]
            if ingredient_names:
                text_parts.append(f"Ingredientes: {', '.join(ingredient_names)}")
        
        # Add preparation summary
        preparation_steps = recipe.get('preparation_steps', [])
        if preparation_steps:
            step_texts = [step.get('instruction', '') for step in preparation_steps if step.get('instruction')]
            if step_texts:
                # Use first few steps for summary
                summary_steps = step_texts[:3]
                text_parts.append(f"Preparación: {' '.join(summary_steps)}")
        
        # Add tags
        tags = classification.get('tags', [])
        if tags:
            text_parts.append(f"Tags: {', '.join(tags)}")
        
        # Add nutritional info
        nutritional_info = recipe.get('nutritional_info', {})
        if nutritional_info:
            nutrition_text = []
            for nutrient, data in nutritional_info.items():
                if isinstance(data, dict) and data.get('value'):
                    nutrition_text.append(f"{nutrient}: {data['value']} {data.get('unit', '')}")
            if nutrition_text:
                text_parts.append(f"Nutrición: {', '.join(nutrition_text)}")
        
        return " | ".join(text_parts)
    
    def generate_embeddings(self, recipes: List[Dict[str, Any]]) -> List[np.ndarray]:
        """Generate embeddings for a list of recipes."""
        if not self.model:
            raise ValueError("Model not loaded")
        
        logger.info(f"Generating embeddings for {len(recipes)} recipes")
        
        # Generate searchable text for each recipe
        texts = []
        for recipe in recipes:
            text = self.generate_recipe_text(recipe)
            texts.append(text)
        
        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        return embeddings
    
    def store_in_chromadb(self, recipes: List[Dict[str, Any]], embeddings: List[np.ndarray]):
        """Store recipes and embeddings in ChromaDB."""
        if not self.collection:
            raise ValueError("ChromaDB not initialized")
        
        logger.info(f"Storing {len(recipes)} recipes in ChromaDB")
        
        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        embeddings_list = []
        
        for i, (recipe, embedding) in enumerate(zip(recipes, embeddings)):
            # Generate ID
            recipe_id = recipe.get('id', f"recipe_{i}")
            ids.append(recipe_id)
            
            # Generate document text
            document_text = self.generate_recipe_text(recipe)
            documents.append(document_text)
            
            # Prepare metadata
            metadata = {
                'name': recipe.get('name', ''),
                'category': recipe.get('classification', {}).get('category', ''),
                'subcategory': recipe.get('classification', {}).get('subcategory', ''),
                'cooking_time': recipe.get('cooking_time'),
                'difficulty': recipe.get('difficulty'),
                'servings': recipe.get('servings'),
                'economic_level': recipe.get('economic_level'),
                'source_file': recipe.get('source_file', ''),
                'tags': json.dumps(recipe.get('classification', {}).get('tags', [])),
                'has_nutrition': bool(recipe.get('nutritional_info')),
                'ingredients_count': len(recipe.get('ingredients', [])),
                'steps_count': len(recipe.get('preparation_steps', []))
            }
            
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            metadatas.append(metadata)
            
            # Add embedding
            embeddings_list.append(embedding.tolist())
        
        # Store in ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings_list
        )
        
        logger.info(f"Stored {len(recipes)} recipes in ChromaDB")
    
    def search_recipes(self, query: str, n_results: int = 10, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for recipes using semantic similarity."""
        if not self.collection:
            raise ValueError("ChromaDB not initialized")
        
        logger.info(f"Searching for: {query}")
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Build where clause for filtering
        where_clause = None
        if filters:
            where_clause = {}
            for key, value in filters.items():
                if isinstance(value, list):
                    where_clause[key] = {"$in": value}
                else:
                    where_clause[key] = value
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            result = {
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            formatted_results.append(result)
        
        logger.info(f"Found {len(formatted_results)} results")
        
        return formatted_results
    
    def process_recipes_batch(self, recipes: List[Dict[str, Any]], 
                            batch_size: int = 100) -> Dict[str, Any]:
        """Process recipes in batches for better memory management."""
        if not self.collection:
            self.setup_chromadb()
        
        total_recipes = len(recipes)
        processed_count = 0
        
        logger.info(f"Processing {total_recipes} recipes in batches of {batch_size}")
        
        for i in range(0, total_recipes, batch_size):
            batch = recipes[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(total_recipes + batch_size - 1)//batch_size}")
            
            # Generate embeddings for batch
            embeddings = self.generate_embeddings(batch)
            
            # Store in ChromaDB
            self.store_in_chromadb(batch, embeddings)
            
            processed_count += len(batch)
            
            logger.info(f"Processed {processed_count}/{total_recipes} recipes")
        
        return {
            'total_recipes': total_recipes,
            'processed_recipes': processed_count,
            'collection_count': self.collection.count()
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection."""
        if not self.collection:
            return {}
        
        count = self.collection.count()
        
        # Get sample of metadata to understand categories
        sample_results = self.collection.get(limit=min(100, count))
        
        # Analyze categories
        categories = {}
        subcategories = {}
        difficulties = {}
        
        for metadata in sample_results['metadatas']:
            category = metadata.get('category', 'unknown')
            subcategory = metadata.get('subcategory', 'unknown')
            difficulty = metadata.get('difficulty', 'unknown')
            
            categories[category] = categories.get(category, 0) + 1
            subcategories[subcategory] = subcategories.get(subcategory, 0) + 1
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        return {
            'total_recipes': count,
            'categories': categories,
            'subcategories': subcategories,
            'difficulties': difficulties,
            'model_name': self.model_name
        }
    
    def export_embeddings(self, output_file: str):
        """Export embeddings to a file."""
        if not self.collection:
            raise ValueError("ChromaDB not initialized")
        
        logger.info(f"Exporting embeddings to: {output_file}")
        
        # Get all data from collection
        all_data = self.collection.get(include=['embeddings', 'metadatas', 'documents'])
        
        export_data = {
            'model_name': self.model_name,
            'total_recipes': len(all_data['ids']),
            'embeddings': all_data['embeddings'],
            'metadatas': all_data['metadatas'],
            'documents': all_data['documents'],
            'ids': all_data['ids']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported {len(all_data['ids'])} embeddings")
    
    def clear_collection(self):
        """Clear all data from the collection."""
        if not self.collection:
            return
        
        logger.info("Clearing ChromaDB collection")
        
        # Delete the collection and recreate it
        self.chroma_client.delete_collection("recipes")
        self.collection = self.chroma_client.create_collection(
            name="recipes",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info("Collection cleared")