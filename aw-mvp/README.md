## Architecture

```
Research Papers → KeyBERT → Keywords → DeepSeek → Field Classification → Final Output
     ↓              ↓         ↓           ↓              ↓                    ↓
  arXiv,        KeyBERT   Technical   DeepSeek R1   Research        JSON + Summary
  PubMed,       Model     Keywords    (OpenRouter)  Fields
  DOAJ,         (BERT)    (Precise)   (Context)     (High-level)
  Zenodo,
  Crossref
```