"""Legacy node shims for backward compatibility only.

Authoritative implementations now live in:
- `clinical_coder.notes`
- `clinical_coder.retrieval`
- `clinical_coder.rules`
- `clinical_coder.reasoning.tasks`
"""

from . import coder, explainer, extractor, parser, retriever, validator

__all__ = ["coder", "explainer", "extractor", "parser", "retriever", "validator"]
