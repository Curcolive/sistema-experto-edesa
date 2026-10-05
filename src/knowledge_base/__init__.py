"""
Paquete de Base de Conocimiento (Knowledge Base)
Cátedra: Principios de Inteligencia Artificial (GT110) - UGD 2026
Estudiante: Estudiante UGD (100001)
"""

from .concept_glossary import ConceptGlossary, BillingConcept, BILLING_CONCEPTS_ONTOLOGY
from .default_facts import load_default_facts_from_json, extract_facts_from_dict, get_builtin_default_facts
from .rules_enresp import Rule, get_all_enresp_rules

__all__ = [
    "ConceptGlossary",
    "BillingConcept",
    "BILLING_CONCEPTS_ONTOLOGY",
    "load_default_facts_from_json",
    "extract_facts_from_dict",
    "get_builtin_default_facts",
    "Rule",
    "get_all_enresp_rules"
]
