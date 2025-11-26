"""
Data generation module for multilingual chatbot dataset.

This module provides tools to generate synthetic training data for
language detection across 5 languages: English, French, Standard Arabic,
Tunisian Dialect (Latin script), and Tunisian Dialect (Arabic script).
"""

from .generator import DatasetGenerator
from .vocabulary import VOCABULARY
from .templates import TEMPLATES

__all__ = ['DatasetGenerator', 'VOCABULARY', 'TEMPLATES']
