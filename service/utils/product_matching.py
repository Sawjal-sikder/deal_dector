from http.client import HTTPException
import requests
from typing import List, Dict, Any
import os
from service.views.products_views import get_all_products_cached

def product_matching_service(product_id: int = 1, supermarket_id: int = 1) -> List[Dict[str, Any]]:
      
    url = os.getenv("BASE_URL_AI", "http://localhost:8015") + "/api/match"
    payload = {
        "product_id": product_id,
        "supermarket_id": supermarket_id
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # Changed from "matched_products" to "product_ids"
        matched_products = response.json().get("product_ids", [])
        return matched_products
    
    except requests.RequestException as e:
        print(f"Error fetching matched products: {e}")
        return []
    



# ============================================================================================================================
# custom product matching service with fuzzy logic
# ============================================================================================================================


# class MatchingService:
#     def __init__(self):
#         self.db = ProductDatabase()
#         self.api_url = "http://10.10.7.76:14003/api/shop/products/"
#         self.fuzzy_threshold = 75
    
#     def sync_products(self):
#         """Fetch and store products from external API"""
#         try:
#             response = requests.get(self.api_url, timeout=30)
#             response.raise_for_status()
#             products = response.json().get('products', [])
            
#             for product in products:
#                 self.db.insert_product(product)
            
#             return len(products)
#         except Exception as e:
#             raise Exception(f"Failed to sync products: {str(e)}")
    
#     def find_matches(self, product_id: int, supermarket_id: int) -> List[int]:
#         """Find matching product IDs across different supermarkets"""
        
#         # Get source product
#         source = self.db.get_product(product_id)
#         if not source:
#             raise HTTPException(status_code=404, detail="Product not found")
        
#         # Check if unit normalization succeeded
#         if not source['unit_value_normalized'] or not source['unit_type_normalized']:
#             return []
        
#         # Get candidates by brand and unit
#         candidates = self.db.get_candidates(
#             supermarket_id,
#             source['normalized_brand'],
#             source['unit_value_normalized'],
#             source['unit_type_normalized']
#         )
        
#         if not candidates:
#             return []
        
#         # Fuzzy match names
#         matches = []
#         source_name = source['name'].lower()
        
#         for candidate in candidates:
#             score = fuzz.token_set_ratio(source_name, candidate['name'].lower())
#             if score >= self.fuzzy_threshold:
#                 matches.append((candidate['id'], score))
        
#         # Sort by score and return IDs
#         matches.sort(key=lambda x: x[1], reverse=True)
#         return [match[0] for match in matches]



# service = MatchingService()

# def product_matching_service(product_id: int = 1, supermarket_id: int = 1) -> List[Dict[str, Any]]:
    
#     all_products_cached = get_all_products_cached()
#     if not all_products_cached:
#         return []
    
#     try:
#         product_ids = service.find_matches(product_id, supermarket_id)
#         return MatchResponse(product_ids=product_ids)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


