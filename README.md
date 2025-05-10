````markdown
# 🔐 Data Obfuscator

A Python module to obfuscate and restore sensitive personal data or sensitive data. Useful for anonymising contracts, agreements, and similar documents before sharing, storing, or processing.

---

## ✨ Features

- Replace real names with fake but realistic names
- Replace dollar amounts with random values
- Hash email addresses into consistent, reversible placeholders
- Fully reversible obfuscation using internal mapping
- spaCy-powered entity recognition (PERSON, MONEY)

---

## 📦 Installation

1. Clone or download the repository:

```bash
git clone https://github.com/zoebchhatriwala/data-obfuscator.git
cd data-obfuscator
```
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

---

## Usage

### Example

```python
from data_obfuscator import DataObfuscator

obfuscator = DataObfuscator()

text = """
Agreement between John Doe (john.doe@example.com) and Jane Smith.
Payment: $7000.00 due on 2025-12-01.
Contact: jane.smith@example.com
"""

# Obfuscate data
obfuscated = obfuscator.obfuscate(text, document_id="contract_001")
print("Obfuscated:\n", obfuscated)

# Restore original data
restored = obfuscator.restore(obfuscated, document_id="contract_001")
print("\nRestored:\n", restored)
```

---

## 🛠️ Requirements

- Python 3.7+
- spaCy 3.x
- `en_core_web_sm` spaCy model

---

## 📃 License

MIT License. Use freely and modify as needed.

---

## 🤝 Contributing

PRs are welcome! For major changes, open an issue first to discuss what you'd like to change.
