from data_obfuscator import DataObfuscator

obfuscator = DataObfuscator()

text = """
Agreement between John Doe (john.doe@example.com) and John Doe.
Payment: $7000.00 due on 2025-12-01.
Contact: john.doe@example.com
Company: Acme Corp.
"""

obfuscated = obfuscator.obfuscate(text, document_id="contract_001")
print("Obfuscated:\n", obfuscated)

restored = obfuscator.restore(obfuscated, document_id="contract_001")
print("\nRestored:\n", restored)
