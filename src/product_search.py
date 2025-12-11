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
    
    def __init__(self, products_csv_path: str = 'data/products/products_asos_enhanced.csv'):
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
        Search for products based on query with SKU-based deduplication
        
        Args:
            query: Search query (e.g., "black jacket", "red dress")
            max_results: Maximum number of results to return
            
        Returns:
            List of unique product dictionaries with relevant info (deduplicated by SKU)
        """
        if self.df is None or len(self.df) == 0:
            return []
        
        # Prepare query
        query_lower = query.lower().strip()
        keywords = query_lower.split()
        
        # Extract product type keywords (dress, jacket, shirt, etc.)
        product_type_keywords = ['dress', 'jacket', 'coat', 'shirt', 'top', 'pants', 'jeans', 
                                 'skirt', 'sweater', 'jumper', 'blazer', 'cardigan', 'hoodie',
                                 'tshirt', 't-shirt', 'shorts', 'trousers']
        
        # Extract color keywords
        color_keywords = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 
                         'purple', 'brown', 'grey', 'gray', 'orange', 'beige', 'navy']
        
        # Identify query intent
        query_product_type = [k for k in keywords if k in product_type_keywords]
        query_colors = [k for k in keywords if k in color_keywords]
        
        # Score products based on matches
        scores = []
        
        for idx, row in self.df.iterrows():
            score = 0
            
            # Extract searchable fields
            name = str(row.get('name_clean', row.get('name', ''))).lower() if pd.notna(row.get('name_clean', row.get('name'))) else ''
            category = str(row.get('category_clean', row.get('category', ''))).lower() if pd.notna(row.get('category_clean', row.get('category'))) else ''
            color = str(row.get('color_clean', row.get('color', ''))).lower() if pd.notna(row.get('color_clean', row.get('color'))) else ''
            description = str(row.get('description', '')).lower() if pd.notna(row.get('description', '')) else ''
            
            # Enhanced fields from dataset
            product_type = str(row.get('product_type', '')).lower() if pd.notna(row.get('product_type')) else ''
            base_color = str(row.get('base_color', '')).lower() if pd.notna(row.get('base_color')) else ''
            brand = str(row.get('brand', '')).lower() if pd.notna(row.get('brand')) else ''
            
            # Exact phrase matching (highest priority)
            if query_lower in name:
                score += 15
            if query_lower in category:
                score += 12
            
            # Product type matching (very important for accuracy)
            for pt_keyword in query_product_type:
                if pt_keyword in product_type:
                    score += 10
                if pt_keyword in name:
                    score += 8
                if pt_keyword in category:
                    score += 6
            
            # Color matching (important for specificity)
            for color_keyword in query_colors:
                if color_keyword in base_color:
                    score += 8
                if color_keyword in color:
                    score += 7
                if color_keyword in name:
                    score += 5
            
            # Individual keyword matching
            for keyword in keywords:
                # Skip if already matched as product type or color
                if keyword in query_product_type or keyword in query_colors:
                    continue
                    
                # Word boundary matching (more accurate than substring)
                if f' {keyword} ' in f' {name} ':
                    score += 6
                elif keyword in name:
                    score += 4
                
                if f' {keyword} ' in f' {category} ':
                    score += 5
                elif keyword in category:
                    score += 3
                
                if keyword in brand:
                    score += 3
                    
                if keyword in description:
                    score += 1
            
            # Bonus for multiple keyword matches
            matched_keywords = sum(1 for k in keywords if k in name or k in category or k in color)
            if matched_keywords >= len(keywords) * 0.7:  # 70% of keywords match
                score += 5
            
            if score > 0:
                scores.append({
                    'score': score,
                    'index': idx,
                    'product': row
                })
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Deduplicate by SKU - keep only first occurrence of each SKU
        seen_skus = set()
        results = []
        
        for item in scores:
            product = item['product']
            sku = product.get('sku', 'N/A')
            
            # Skip if we've already seen this SKU
            if pd.notna(sku) and sku in seen_skus:
                continue
                
            # Add SKU to seen set
            if pd.notna(sku):
                seen_skus.add(sku)
            
            # Parse images from string representation of list
            images_raw = product.get('images', '[]')
            images = []
            if pd.notna(images_raw) and images_raw != 'N/A':
                try:
                    import ast
                    images = ast.literal_eval(str(images_raw)) if isinstance(images_raw, str) else images_raw
                    if not isinstance(images, list):
                        images = []
                except:
                    images = []
            
            result = {
                'name': product.get('name_clean', product.get('name', 'N/A')),
                'category': product.get('category_clean', product.get('category', 'N/A')),
                'color': product.get('color_clean', product.get('color', 'N/A')),
                'price': product.get('price_clean', product.get('price', 'N/A')),
                'url': product.get('url', 'N/A'),
                'sku': sku,
                'description': product.get('description', 'N/A') if pd.notna(product.get('description')) else 'N/A',
                'images': images[:3] if images else []  # Include first 3 images
            }
            results.append(result)
            
            # Stop when we have enough unique results
            if len(results) >= max_results:
                break
        
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
            # Parse images
            images_raw = product.get('images', '[]')
            images = []
            if pd.notna(images_raw) and images_raw != 'N/A':
                try:
                    import ast
                    images = ast.literal_eval(str(images_raw)) if isinstance(images_raw, str) else images_raw
                    if not isinstance(images, list):
                        images = []
                except:
                    images = []
            
            result = {
                'name': product.get('name_clean', product.get('name', 'N/A')),
                'category': product.get('category_clean', product.get('category', 'N/A')),
                'color': product.get('color_clean', product.get('color', 'N/A')),
                'price': product.get('price_clean', product.get('price', 'N/A')),
                'url': product.get('url', 'N/A'),
                'sku': product.get('sku', 'N/A'),
                'images': images[:3] if images else []
            }
            results.append(result)
        
        return results
