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
        alphabets = 'abcdefghijklmnopqrstuvwxyz'
        first_name = ''.join(random.choices(alphabets, k=8)).capitalize()
        last_name = ''.join(random.choices(alphabets, k=8)).capitalize()
        while True:
            name = f"{first_name} {last_name}"
            if name not in used_names:
                return name

    def _generate_unique_random_amount(self, used_amounts):
        while True:
            amount = f"{random.randint(1000, 10000)}.{random.randint(0, 999999):06d}"
            if amount not in used_amounts:
                return amount
    
    def is_valid_email(self, email):
        # Simple regex for email validation
        pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        return re.match(pattern, email) is not None
    
     # Handle email obfuscation
    def hash_email(self, email):
        hashed = hashlib.sha256(email.encode()).hexdigest()[:10] + "@example.com"
        return hashed

    def obfuscate(self, text, document_id="default_doc"):
        doc = nlp(text)
        replacements = []

        # Initialize the mappings for the document if not already done
        names_map = self.data_mappings[document_id]["names"]
        amounts_map = self.data_mappings[document_id]["amounts"]
        emails_map = self.data_mappings[document_id]["emails"]

        # Handle PERSON and MONEY entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Get the original name
                original = ent.text

                # Initialize the replacement
                replacement = ''

                # If it's an email, hash it
                if self.is_valid_email(original):
                    # Check if the email is already in the map
                    if original in emails_map:
                        # If it is, use the mapped email
                        replacement = emails_map[original]
                    else:
                        # If not, hash the email
                        replacement = self.hash_email(original)

                    # Store the mapping
                    emails_map[original] = replacement
                else:
                    # Check if the name is already in the map
                    if original in names_map:
                        # If it is, use the mapped name
                        replacement = names_map[original]
                    else:
                        # If not, generate a new unique name
                        replacement = self._generate_unique_random_name(set(names_map))

                        # Store the mapping
                        names_map[original] = replacement
                    
                # Add the replacement to the list
                replacements.append((ent.start_char, ent.end_char, replacement))
            elif ent.label_ == "MONEY":
                # Get the original amount
                original = ent.text

                # Check if the amount is already in the map
                if original in amounts_map:
                    # If it is, use the mapped amount
                    replacement = amounts_map[original]
                else:
                    # If not, generate a new unique amount
                    replacement = self._generate_unique_random_amount(set(amounts_map))

                    # Store the mapping
                    amounts_map[original] = replacement
                
                # Add the replacement to the list
                replacements.append((ent.start_char, ent.end_char, replacement))

        # Handle EMAIL entities
        for token in doc:
            # Check if the token is an email
            if token.like_email:
                # Get the original email
                original = token.text

                # Check if the email is already in the map
                if original in emails_map:
                    # If it is, use the mapped email
                    replacement = emails_map[original]
                else:
                    # If not, hash the email
                    replacement = self.hash_email(original)

                    # Store the mapping
                    emails_map[original] = replacement
                
                # Add the replacement to the list
                replacements.append((token.idx, token.idx + len(token.text), replacement))

        # Replace entities safely
        replacements.sort(reverse=True)
        redacted_text = text
        for start, end, replacement in replacements:
            redacted_text = redacted_text[:start] + replacement + redacted_text[end:]

        # Store the mappings
        self.data_mappings[document_id]["names"] = {v: k for k, v in names_map.items()}
        self.data_mappings[document_id]["amounts"] = {v: k for k, v in amounts_map.items()}
        self.data_mappings[document_id]["emails"] = {v: k for k, v in emails_map.items()}

        # Return the redacted text
        return redacted_text

    def restore(self, obfuscated_text, document_id="default_doc"):
        # Initialize the restored text
        restored_text = obfuscated_text

        # Check if the document_id exists
        if document_id not in self.data_mappings:
            raise ValueError(f"No mappings found for document ID: {document_id}")
        
        # Get the mappings for the document
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

        # Return the restored text
        return restored_text
