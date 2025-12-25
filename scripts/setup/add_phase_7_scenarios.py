#!/usr/bin/env python3
"""
Add 13 additional scenarios to scenarios.json
Session 130 Phase 8: Integration & Testing
Achieving 3-per-category minimum standard
"""

import json
from datetime import datetime

# Read current scenarios
with open("data/scenarios/scenarios.json", "r") as f:
    scenarios = json.load(f)

timestamp = datetime.now().isoformat()

print("=" * 70)
print("SESSION 130 PHASE 8: ADDING 13 ADDITIONAL SCENARIOS")
print("=" * 70)
print(f"Current scenarios count: {len(scenarios)}")
print("Adding 13 new scenarios to reach 3-per-category minimum...")
print()

# Scenario 10: Banking and Financial Services
scenarios["banking_account_services"] = {
    "scenario_id": "banking_account_services",
    "name": "Banking and Financial Services",
    "category": "daily_life",
    "difficulty": "intermediate",
    "description": "Visit a bank to open an account, discuss financial products, understand banking services, and handle transactions.",
    "user_role": "customer",
    "ai_role": "bank_representative",
    "setting": "Bank branch or online banking consultation",
    "duration_minutes": 18,
    "phases": [
        {
            "phase_id": "opening_account",
            "name": "Opening an Account",
            "description": "Learn about account types and open a new account",
            "expected_duration_minutes": 5,
            "key_vocabulary": [
                "account",
                "checking",
                "savings",
                "deposit",
                "minimum balance",
                "interest rate",
                "fees",
                "documents",
                "identification",
                "signature",
            ],
            "essential_phrases": [
                "I'd like to open an account",
                "What types of accounts do you offer?",
                "What are the fees?",
                "Is there a minimum balance required?",
                "What documents do I need?",
                "I'd like to open a checking account",
            ],
            "learning_objectives": [
                "Understand different account types",
                "Ask about fees and requirements",
                "Provide necessary documentation",
            ],
            "cultural_notes": "Banks in many countries require government-issued ID and proof of address. Opening an account may require an initial deposit. Ask about all fees upfront - monthly maintenance, overdraft, ATM fees. Compare different account types before deciding.",
            "success_criteria": [
                "Ask about at least 2 account types",
                "Understand fee structure",
                "Successfully provide required information",
            ],
        },
        {
            "phase_id": "banking_services",
            "name": "Banking Services Overview",
            "description": "Learn about available banking services and products",
            "expected_duration_minutes": 5,
            "key_vocabulary": [
                "debit card",
                "credit card",
                "online banking",
                "mobile app",
                "direct deposit",
                "wire transfer",
                "bill pay",
                "overdraft protection",
                "ATM",
                "PIN",
            ],
            "essential_phrases": [
                "How does online banking work?",
                "Can I get a debit card?",
                "What about mobile banking?",
                "How do I set up direct deposit?",
                "Are there ATM fees?",
                "Can I transfer money internationally?",
            ],
            "learning_objectives": [
                "Understand modern banking services",
                "Learn about digital banking options",
                "Ask about card services",
            ],
            "cultural_notes": "Online and mobile banking are standard in most countries. Set up online banking immediately - it's more convenient than visiting branches. Direct deposit is preferred by most employers. Keep your PIN secret and change it regularly.",
            "success_criteria": [
                "Understand online banking setup",
                "Know how to get debit/credit cards",
                "Ask about fees for various services",
            ],
        },
        {
            "phase_id": "making_transaction",
            "name": "Making a Transaction",
            "description": "Perform common banking transactions",
            "expected_duration_minutes": 5,
            "key_vocabulary": [
                "deposit",
                "withdrawal",
                "transfer",
                "balance",
                "transaction",
                "receipt",
                "cash",
                "check",
                "account number",
                "routing number",
            ],
            "essential_phrases": [
                "I'd like to deposit this check",
                "I need to withdraw some cash",
                "Can I transfer money to another account?",
                "What's my current balance?",
                "May I have a receipt?",
                "How long will this transaction take?",
            ],
            "learning_objectives": [
                "Perform deposits and withdrawals",
                "Transfer money between accounts",
                "Check account balance",
            ],
            "cultural_notes": "Always get receipts for transactions. Checks take 1-5 business days to clear. Wire transfers are usually same-day but have fees. ATMs are convenient but may charge fees if not from your bank. Keep transaction records for taxes.",
            "success_criteria": [
                "Complete at least one transaction",
                "Understand processing times",
                "Keep proper documentation",
            ],
        },
        {
            "phase_id": "security",
            "name": "Questions and Security",
            "description": "Ask about security features and get contact information",
            "expected_duration_minutes": 3,
            "key_vocabulary": [
                "security",
                "fraud protection",
                "password",
                "security questions",
                "customer service",
                "phone number",
                "email",
                "branch hours",
                "two-factor authentication",
            ],
            "essential_phrases": [
                "How is my account protected?",
                "What if I see fraudulent charges?",
                "How do I contact customer service?",
                "What are your hours?",
                "Is my information secure?",
            ],
            "learning_objectives": [
                "Understand security measures",
                "Know how to report fraud",
                "Have contact information for help",
            ],
            "cultural_notes": "Banks have fraud protection, but report suspicious activity immediately. Use strong passwords and enable two-factor authentication. Never share passwords or PINs. Customer service is available 24/7 for most banks. Register your phone for alerts about unusual activity.",
            "success_criteria": [
                "Understand fraud protection procedures",
                "Have customer service contact info",
                "Know security best practices",
            ],
        },
    ],
    "prerequisites": ["basic_numbers", "identifying_documents", "financial_vocabulary"],
    "learning_outcomes": [
        "Successfully navigate banking system",
        "Open and manage accounts",
        "Perform transactions confidently",
    ],
    "vocabulary_focus": [
        "account",
        "deposit",
        "withdrawal",
        "balance",
        "transfer",
        "debit card",
        "online banking",
        "PIN",
        "fees",
        "security",
        "fraud",
        "transaction",
    ],
    "cultural_context": {
        "banking_hours": "Most banks open weekdays 9 AM - 5 PM, some Saturday mornings",
        "documentation": "Bring passport/ID and proof of address for new accounts",
        "fees": "Ask about ALL fees - monthly maintenance, ATM, overdraft, wire transfer",
        "online_banking": "Essential for modern banking; set up immediately",
        "security": "Banks never ask for passwords by email or phone",
    },
    "is_active": True,
    "created_at": timestamp,
    "updated_at": timestamp,
}

print("✅ Added: Banking and Financial Services (1/13)")

# Continue with remaining scenarios...
# (Due to length, I'll add them in batches)

print("\n" + "=" * 70)
print(f"Phase 8 Progress: 1/13 scenarios added")
print("Continuing with remaining scenarios...")
print("=" * 70)
