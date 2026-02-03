from http.client import HTTPException
# from attr import dataclass
import requests
from typing import List, Dict, Any
from dataclasses import dataclass
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
    













# # ============================================================================================================================
# # custom product matching service with fuzzy logic
# # ============================================================================================================================
# from typing import List, Dict, Any, Optional
# from dataclasses import dataclass
# from rapidfuzz import fuzz
# import re



# class ProductNotFoundError(Exception):
#     """Raised when product is not found"""
#     pass


# # ============================================================================
# # UNIT NORMALIZATION
# # ============================================================================

# @dataclass
# class NormalizedUnit:
#     value: float
#     unit_type: str
#     base_unit: str


# class UnitNormalizer:
#     WEIGHT_CONVERSIONS = {
#         'kg': 1000, 'kilogram': 1000, 'kilo': 1000,
#         'g': 1, 'gram': 1, 'gr': 1,
#         'mg': 0.001, 'milligram': 0.001,
#         'lb': 453.592, 'pound': 453.592,
#         'oz': 28.3495, 'ounce': 28.3495,
#     }
    
#     VOLUME_CONVERSIONS = {
#         'l': 1000, 'liter': 1000, 'litre': 1000,
#         'ml': 1, 'milliliter': 1, 'millilitre': 1,
#         'cl': 10, 'centiliter': 10,
#         'dl': 100, 'deciliter': 100,
#     }
    
#     COUNT_UNITS = {'stuks', 'stuk', 'piece', 'pieces', 'items', 'item', 'count', 'pak', 'pack', 'pcs', 'pc', 'st', 'x'}
    
#     def normalize(self, unit_string: str) -> Optional[NormalizedUnit]:
#         if not unit_string:
#             return None
            
#         unit_string = unit_string.lower().strip()
        
#         # Handle "6 x 330 ml" format
#         multipack = re.search(r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*([a-z]+)', unit_string)
#         if multipack:
#             value = float(multipack.group(2))
#             unit = multipack.group(3)
#             unit_string = f"{value} {unit}"
        
#         # Extract number and unit
#         match = re.search(r'(\d+\.?\d*|\d*\.\d+)\s*([a-zA-Z]+)', unit_string)
#         if not match:
#             return None
            
#         value = float(match.group(1))
#         unit = match.group(2).lower()
        
#         if unit in self.WEIGHT_CONVERSIONS:
#             return NormalizedUnit(value * self.WEIGHT_CONVERSIONS[unit], 'weight', 'g')
        
#         if unit in self.VOLUME_CONVERSIONS:
#             return NormalizedUnit(value * self.VOLUME_CONVERSIONS[unit], 'volume', 'ml')
        
#         if unit in self.COUNT_UNITS:
#             return NormalizedUnit(value, 'count', 'piece')
        
#         return None


# class MatchingService:
    
#     def find_matches(self, product_id: int, target_supermarket_id: Optional[int] = None) -> List[int]:
#         """
#         Find matching product IDs across different supermarkets
        
#         Args:
#             product_id: Source product ID to find matches for
#             target_supermarket_id: Optional - specific supermarket to search in. 
#                                    If None, searches all other supermarkets.
#         """
        
#         all_products_cached = get_all_products_cached()
        
#         # Get source product
#         source = next(
#             (p for p in all_products_cached if p['id'] == product_id),
#             None
#         )
#         print(f"Source product: {source}")
#         print("--------------------------------------------------")
#         if not source:
#             raise ProductNotFoundError(f"Product with id {product_id} not found")
        
#         # Check if unit normalization succeeded
#         if not source.get('unit_value_normalized') or not source.get('unit_type_normalized'):
#             return []
        
#         source_supermarket_id = source.get('supermarket_id')
        
#         # Get candidates from cached data (filter by different supermarket, brand, and unit)
#         candidates = [
#             p for p in all_products_cached
#             if p.get('supermarket_id') != source_supermarket_id  # Must be different supermarket
#             and (target_supermarket_id is None or p.get('supermarket_id') == target_supermarket_id)  # Optional target filter
#             and p.get('normalized_brand') == source.get('normalized_brand')
#             and p.get('unit_value_normalized') == source.get('unit_value_normalized')
#             and p.get('unit_type_normalized') == source.get('unit_type_normalized')
#             and p['id'] != product_id  # Exclude source product
#         ]
        
#         if not candidates:
#             return []
        
#         # Fuzzy match names
#         matches = []
#         source_name = source['name'].lower()
        
#         for candidate in candidates:
#             score = fuzz.token_set_ratio(source_name, candidate['name'].lower())
#             if score >= 75:
#                 matches.append((candidate['id'], score))
        
#         # Sort by score and return IDs
#         matches.sort(key=lambda x: x[1], reverse=True)
#         return [match[0] for match in matches]


# service = MatchingService()


# def product_matching_service(product_id: int = 1, target_supermarket_id: Optional[int] = None) -> Dict[str, Any]:
#     """
#     Find matching products across supermarkets
    
#     Args:
#         product_id: Source product ID
#         target_supermarket_id: Optional - specific supermarket to search. 
#                                If None, searches all other supermarkets.
#     """
#     try:
#         product_ids = service.find_matches(product_id, target_supermarket_id)
        
#         print(f"product_id: {product_id}, target_supermarket_id: {target_supermarket_id}")
#         print(f"Matched product IDs: {product_ids}")
#         print(f"Total matches found: {len(product_ids)}")
#         print("--------------------------------------------------")
#         return {"product_ids": product_ids}
    
#     except ProductNotFoundError as e:
#         return {"error": str(e), "product_ids": []}
#     except Exception as e:
#         return {"error": str(e), "product_ids": []}