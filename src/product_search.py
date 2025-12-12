"""Product search engine with structured filtering and scoring."""

import re
from typing import Dict, List, Optional

import pandas as pd


class ProductSearch:
    """Search for products in ASOS catalog."""
    
    def __init__(self, products_csv_path: str = 'data/products/products_asos_enhanced.csv'):
        """Initialize product search with CSV data."""
        self.products_csv_path = products_csv_path
        self.df = None
        self.load_products()
    
    def load_products(self):
        """Load products from CSV."""
        try:
            self.df = pd.read_csv(self.products_csv_path)
            print(f"✓ Loaded {len(self.df)} products from {self.products_csv_path}")
        except Exception as e:
            print(f"✗ Error loading products: {e}")
            self.df = None
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        filters: Optional[Dict] = None,
        sort_by: str = "relevance",
    ) -> List[Dict]:
        """Search for products based on query with SKU-based deduplication."""
        if self.df is None or len(self.df) == 0:
            return []
        
        filters = filters or {}

        query_lower = query.lower().strip()
        keywords = query_lower.split()
        
        product_type_keywords = ['dress', 'jacket', 'coat', 'shirt', 'top', 'pants', 'jeans', 
                                 'skirt', 'sweater', 'jumper', 'blazer', 'cardigan', 'hoodie',
                                 'tshirt', 't-shirt', 'shorts', 'trousers']
        
        color_keywords = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 
                         'purple', 'brown', 'grey', 'gray', 'orange', 'beige', 'navy']
        
        query_product_type = [k for k in keywords if k in product_type_keywords]
        query_colors = [k for k in keywords if k in color_keywords]

        def has_word(text: str, kw: str) -> bool:
            try:
                return bool(re.search(rf"\b{re.escape(kw)}\b", text))
            except Exception:
                return False

        filter_product_type = filters.get('product_type') or (query_product_type[0] if query_product_type else None)

        raw_colors = filters.get('colors')
        if isinstance(raw_colors, str):
            filter_colors = [raw_colors.lower()]
        elif isinstance(raw_colors, list):
            filter_colors = [c.lower() for c in raw_colors]
        else:
            filter_colors = query_colors

        filter_brand = filters.get('brand').lower() if isinstance(filters.get('brand'), str) else None
        price_min = filters.get('price_min')
        price_max = filters.get('price_max')
        raw_sizes = filters.get('sizes')
        if isinstance(raw_sizes, str):
            filter_sizes = [raw_sizes.lower()]
        elif isinstance(raw_sizes, list):
            filter_sizes = [s.lower() for s in raw_sizes]
        else:
            filter_sizes = []

        raw_features = filters.get('features')
        if isinstance(raw_features, str):
            filter_features = [raw_features.lower()]
        elif isinstance(raw_features, list):
            filter_features = [f.lower() for f in raw_features]
        else:
            filter_features = []
        
        df_filtered = self.df

        if filter_product_type:
            pt = filter_product_type.lower().strip()
            df_filtered = df_filtered[
                df_filtered['product_type'].fillna('').str.lower().str.contains(pt) |
                df_filtered['category_clean'].fillna('').str.lower().str.contains(pt) |
                df_filtered['category'].fillna('').str.lower().str.contains(pt)
            ]

        if filter_colors:
            mask = pd.Series([False] * len(df_filtered), index=df_filtered.index)
            for color_kw in filter_colors:
                kw = color_kw.lower().strip()
                mask = mask | (
                    df_filtered['color_clean'].fillna('').str.lower().apply(lambda t: has_word(t, kw)) |
                    df_filtered['color'].fillna('').str.lower().apply(lambda t: has_word(t, kw)) |
                    df_filtered['name'].fillna('').str.lower().apply(lambda t: has_word(t, kw))
                )
            df_filtered = df_filtered[mask]

        if filter_features:
            feat_mask = pd.Series([True] * len(df_filtered), index=df_filtered.index)
            for feat in filter_features:
                kw = feat.lower().strip()
                feat_mask = feat_mask & (
                    df_filtered['name'].fillna('').str.lower().apply(lambda t: has_word(t, kw)) |
                    df_filtered['category_clean'].fillna('').str.lower().apply(lambda t: has_word(t, kw)) |
                    df_filtered['category'].fillna('').str.lower().apply(lambda t: has_word(t, kw)) |
                    df_filtered['description'].fillna('').str.lower().apply(lambda t: has_word(t, kw))
                )
            df_filtered = df_filtered[feat_mask]

        if filter_brand:
            df_filtered = df_filtered[df_filtered['brand'].fillna('').str.lower().str.contains(filter_brand)]

        if price_min is not None:
            df_filtered = df_filtered[df_filtered['price_clean'].fillna(float('inf')) >= float(price_min)]

        if price_max is not None:
            df_filtered = df_filtered[df_filtered['price_clean'].fillna(0.0) <= float(price_max)]

        if filter_sizes:
            def has_size(val):
                try:
                    import ast
                    parsed = ast.literal_eval(str(val))
                    if isinstance(parsed, list):
                        parsed = [str(x).lower() for x in parsed]
                        return any(sz in parsed for sz in filter_sizes)
                except Exception:
                    return False
                return False
            df_filtered = df_filtered[df_filtered['sizes_available'].apply(has_size)]

        # Score products based on matches
        scores = []

        for idx, row in df_filtered.iterrows():
            score = 0
            
            # Extract searchable fields
            name = str(row.get('name', '')).lower() if pd.notna(row.get('name')) else ''
            category = str(row.get('category_clean', '')).lower() if pd.notna(row.get('category_clean')) else str(row.get('category', '')).lower() if pd.notna(row.get('category')) else ''
            color = str(row.get('color_clean', '')).lower() if pd.notna(row.get('color_clean')) else str(row.get('color', '')).lower() if pd.notna(row.get('color')) else ''
            description = str(row.get('description', '')).lower() if pd.notna(row.get('description', '')) else ''
            
            # Enhanced fields from dataset
            product_type = str(row.get('product_type', '')).lower() if pd.notna(row.get('product_type')) else ''
            base_color = str(row.get('base_color', '')).lower() if pd.notna(row.get('base_color')) else ''
            brand = str(row.get('brand', '')).lower() if pd.notna(row.get('brand')) else ''
            
            if query_lower in name:
                score += 15
            if query_lower in category:
                score += 12
            
            for pt_keyword in query_product_type:
                if pt_keyword in product_type:
                    score += 10
                if pt_keyword in name:
                    score += 8
                if pt_keyword in category:
                    score += 6
            
            is_multicolored = any(term in color for term in ['multicoloured', 'multi', 'floral', 'print'])

            # Use filter_colors if provided, otherwise inferred query colors
            active_colors = filter_colors if filter_colors else query_colors

            for color_keyword in active_colors:
                in_color = has_word(color, color_keyword)
                in_name = has_word(name, color_keyword)
                in_base = has_word(base_color, color_keyword)

                if in_color and not is_multicolored:
                    score += 10  # Solid color match
                elif in_color and is_multicolored:
                    score += 3  # Multicolored with this color present
                elif in_base and not is_multicolored:
                    score += 7  # Base color match for solid colors
                elif in_base and is_multicolored:
                    score += 2  # Base color for multicolored (less relevant)

                if in_name and not is_multicolored:
                    score += 5

            active_features = filter_features
            for feat in active_features:
                in_name = has_word(name, feat)
                in_cat = has_word(category, feat)
                in_desc = has_word(description, feat)
                if in_name or in_cat:
                    score += 6
                elif in_desc:
                    score += 3
            
            if filter_brand and filter_brand in brand:
                score += 10
            else:
                for keyword in keywords:
                    if keyword in brand:
                        score += 4

            if price_min is not None or price_max is not None:
                price_val = row.get('price_clean', None)
                if pd.notna(price_val):
                    try:
                        price_val = float(price_val)
                        if price_min is not None and price_max is not None:
                            mid = (float(price_min) + float(price_max)) / 2.0
                            # Up to 5 points for being near the middle of the requested range
                            distance = abs(price_val - mid)
                            span = max(1.0, float(price_max) - float(price_min))
                            score += max(0, 5 - (distance / span) * 5)
                        elif price_min is not None and price_val >= float(price_min):
                            score += 2
                        elif price_max is not None and price_val <= float(price_max):
                            score += 2
                    except Exception:
                        pass

            if filter_sizes:
                try:
                    import ast
                    parsed = ast.literal_eval(str(row.get('sizes_available', '[]')))
                    if isinstance(parsed, list):
                        parsed_lower = [str(x).lower() for x in parsed]
                        if any(sz in parsed_lower for sz in filter_sizes):
                            score += 3
                except Exception:
                    pass

            for keyword in keywords:
                # Skip if already matched as product type, color, or features
                if keyword in query_product_type or keyword in active_colors or keyword in active_features:
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
            
            matched_keywords = sum(1 for k in keywords if k in name or k in category or k in color)
            if matched_keywords >= len(keywords) * 0.7:  # 70% of keywords match
                score += 5
            
            if score > 0:
                scores.append({
                    'score': score,
                    'index': idx,
                    'product': row
                })
        
        # Sort by score (descending) or price if requested
        if sort_by == "price_asc":
            scores.sort(key=lambda x: x['product'].get('price_clean', float('inf')))
        elif sort_by == "price_desc":
            scores.sort(key=lambda x: x['product'].get('price_clean', 0), reverse=True)
        else:
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
                'name': product.get('name', 'N/A'),
                'category': product.get('category_clean', product.get('category', 'N/A')),
                'color': product.get('color_clean', product.get('color', 'N/A')),
                'price': product.get('price_clean', product.get('price', 'N/A')),
                'url': product.get('url', 'N/A'),
                'sku': sku,
                'description': product.get('description', 'N/A') if pd.notna(product.get('description')) else 'N/A',
                'brand': product.get('brand', 'N/A'),
                'base_color': product.get('base_color', 'N/A'),
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
                'name': product.get('name', 'N/A'),
                'category': product.get('category_clean', product.get('category', 'N/A')),
                'color': product.get('color_clean', product.get('color', 'N/A')),
                'price': product.get('price_clean', product.get('price', 'N/A')),
                'url': product.get('url', 'N/A'),
                'sku': product.get('sku', 'N/A'),
                'images': images[:3] if images else []
            }
            results.append(result)
        
        return results
