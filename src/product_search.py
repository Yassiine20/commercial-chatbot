"""
Product Search Engine for ASOS Products
Searches products by category, color, and keywords
"""
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import re


class ProductSearch:
    """Search for products in ASOS catalog"""
    
    def __init__(self, products_csv_path: str = 'data/products/products_asos_cleaned.csv'):
        """
        Initialize product search with CSV data
        
        Args:
            products_csv_path: Path to the cleaned products CSV
        """
        self.products_csv_path = products_csv_path
        self.df = None
        self.load_products()
    
    def load_products(self):
        """Load products from CSV"""
        try:
            self.df = pd.read_csv(self.products_csv_path)
            print(f"✓ Loaded {len(self.df)} products from {self.products_csv_path}")
        except Exception as e:
            print(f"✗ Error loading products: {e}")
            self.df = None
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for products based on query
        
        Args:
            query: Search query (e.g., "black jacket", "red dress")
            max_results: Maximum number of results to return
            
        Returns:
            List of product dictionaries with relevant info
        """
        if self.df is None or len(self.df) == 0:
            return []
        
        # Prepare query
        query_lower = query.lower().strip()
        keywords = query_lower.split()
        
        # Score products based on matches
        scores = []
        
        for idx, row in self.df.iterrows():
            score = 0
            
            # Extract searchable fields
            name = str(row.get('name_clean', row.get('name', ''))).lower() if pd.notna(row.get('name_clean', row.get('name'))) else ''
            category = str(row.get('category_clean', row.get('category', ''))).lower() if pd.notna(row.get('category_clean', row.get('category'))) else ''
            color = str(row.get('color_clean', row.get('color', ''))).lower() if pd.notna(row.get('color_clean', row.get('color'))) else ''
            description = str(row.get('description', '')).lower() if pd.notna(row.get('description', '')) else ''
            
            # Score based on keyword matches
            for keyword in keywords:
                # Exact or partial matches in name (highest priority)
                if keyword in name:
                    score += 5
                # Matches in category
                if keyword in category:
                    score += 3
                # Matches in color
                if keyword in color:
                    score += 4
                # Matches in description
                if keyword in description:
                    score += 1
            
            if score > 0:
                scores.append({
                    'score': score,
                    'index': idx,
                    'product': row
                })
        
        # Sort by score (descending) and return top results
        scores.sort(key=lambda x: x['score'], reverse=True)
        results = []
        
        for item in scores[:max_results]:
            product = item['product']
            result = {
                'name': product.get('name_clean', product.get('name', 'N/A')),
                'category': product.get('category_clean', product.get('category', 'N/A')),
                'color': product.get('color_clean', product.get('color', 'N/A')),
                'price': product.get('price_clean', product.get('price', 'N/A')),
                'url': product.get('url', 'N/A'),
                'sku': product.get('sku', 'N/A'),
                'description': product.get('description', 'N/A') if pd.notna(product.get('description')) else 'N/A'
            }
            results.append(result)
        
        return results
    
    def search_by_category_and_color(
        self, 
        category: Optional[str] = None, 
        color: Optional[str] = None, 
        max_results: int = 5
    ) -> List[Dict]:
        """
        Search for products by specific category and/or color
        
        Args:
            category: Product category to filter (e.g., 'jacket', 'dress')
            color: Color to filter (e.g., 'black', 'red')
            max_results: Maximum number of results
            
        Returns:
            List of matching products
        """
        if self.df is None or len(self.df) == 0:
            return []
        
        filtered_df = self.df.copy()
        
        # Filter by category
        if category:
            category_lower = category.lower().strip()
            filtered_df = filtered_df[
                (filtered_df['category_clean'].fillna('').str.lower().str.contains(category_lower)) |
                (filtered_df['category'].fillna('').str.lower().str.contains(category_lower))
            ]
        
        # Filter by color
        if color:
            color_lower = color.lower().strip()
            filtered_df = filtered_df[
                (filtered_df['color_clean'].fillna('').str.lower().str.contains(color_lower)) |
                (filtered_df['color'].fillna('').str.lower().str.contains(color_lower))
            ]
        
        # Format results
        results = []
        for idx, product in filtered_df.head(max_results).iterrows():
            result = {
                'name': product.get('name_clean', product.get('name', 'N/A')),
                'category': product.get('category_clean', product.get('category', 'N/A')),
                'color': product.get('color_clean', product.get('color', 'N/A')),
                'price': product.get('price_clean', product.get('price', 'N/A')),
                'url': product.get('url', 'N/A'),
                'sku': product.get('sku', 'N/A'),
            }
            results.append(result)
        
        return results
