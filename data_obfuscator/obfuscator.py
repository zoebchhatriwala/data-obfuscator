import spacy
import re
import hashlib
import random
from collections import defaultdict

# Load spaCy NLP model once
nlp = spacy.load("en_core_web_sm")

class DataObfuscator:
    def __init__(self):
        # Mapping: document_id -> { names, amounts, emails }
        self.data_mappings = defaultdict(lambda: {"names": {}, "amounts": {}, "emails": {}})

    def _generate_unique_random_name(self, used_names):
        first_names = ["Alice", "Bob", "Clara", "David", "Emma"]
        last_names = ["Smith", "Johnson", "Brown", "Taylor", "Wilson"]
        while True:
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            if name not in used_names:
                return name

    def _generate_unique_random_amount(self, used_amounts):
        while True:
            amount = f"${random.randint(1000, 10000)}.{random.randint(0, 99):02d}"
            if amount not in used_amounts:
                return amount

    def obfuscate(self, text, document_id="default_doc"):
        doc = nlp(text)
        replacements = []

        names_map = self.data_mappings[document_id]["names"]
        amounts_map = self.data_mappings[document_id]["amounts"]
        emails_map = self.data_mappings[document_id]["emails"]

        # Reverse maps for deterministic replacement
        name_reverse = {v: k for k, v in names_map.items()}
        amount_reverse = {v: k for k, v in amounts_map.items()}

        # Handle PERSON and MONEY entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                original = ent.text
                if original in name_reverse:
                    replacement = name_reverse[original]
                else:
                    replacement = self._generate_unique_random_name(set(names_map))
                    names_map[replacement] = original
                replacements.append((ent.start_char, ent.end_char, replacement))

            elif ent.label_ == "MONEY":
                original = ent.text
                if original in amount_reverse:
                    replacement = amount_reverse[original]
                else:
                    replacement = self._generate_unique_random_amount(set(amounts_map))
                    amounts_map[replacement] = original
                replacements.append((ent.start_char, ent.end_char, replacement))

        # Replace entities safely
        replacements.sort(reverse=True)
        redacted_text = text
        for start, end, replacement in replacements:
            redacted_text = redacted_text[:start] + replacement + redacted_text[end:]

        # Handle email obfuscation
        def hash_email(match):
            email = match.group()
            for hashed, original in emails_map.items():
                if original == email:
                    return hashed
            hashed = hashlib.sha256(email.encode()).hexdigest()[:10] + "@example.com"
            emails_map[hashed] = email
            return hashed

        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        redacted_text = re.sub(email_pattern, hash_email, redacted_text)

        return redacted_text

    def restore(self, obfuscated_text, document_id="default_doc"):
        restored_text = obfuscated_text

        names_map = self.data_mappings[document_id]["names"]
        amounts_map = self.data_mappings[document_id]["amounts"]
        emails_map = self.data_mappings[document_id]["emails"]

        # Restore names
        for fake, real in names_map.items():
            restored_text = restored_text.replace(fake, real)

        # Restore amounts
        for fake, real in amounts_map.items():
            restored_text = restored_text.replace(fake, real)

        # Restore emails
        for fake, real in emails_map.items():
            restored_text = restored_text.replace(fake, real)

        return restored_text
