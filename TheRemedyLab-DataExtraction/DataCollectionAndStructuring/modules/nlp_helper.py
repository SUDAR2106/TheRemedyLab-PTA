# modules/nlp_helper.py
"""Resolve medical term synonyms to standard keys."""
import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])


def standardize_term(raw_term: str) -> str:
 
    return raw_term.strip().title()