"""Generates synthetic transaction data for training the category classifier.

Real labelled bank data is personal financial data and can't be used here, so we
synthesise it. The generator deliberately keeps the classes hard to separate —
shared merchants, generic memos, overlapping amounts, a little label noise —
because a model trained on tidy data falls over on real statements.
"""
import random

import numpy as np
import pandas as pd

RANDOM_SEED = 42

# Share of rows that get a merchant trading in several categories.
AMBIGUOUS_MERCHANT_RATE = 0.30
# Share of rows whose memo carries no category signal.
GENERIC_DESCRIPTION_RATE = 0.35
# Share of labels randomly corrupted, standing in for user miscategorisation.
LABEL_NOISE_RATE = 0.05

GENERIC_DESCRIPTIONS = [
    "Card payment",
    "Contactless payment",
    "Online purchase",
    "Debit card transaction",
    "Payment",
    "POS purchase",
]

# Merchants listed under every category they plausibly sell in, so the merchant
# name alone is never a reliable label.
AMBIGUOUS_MERCHANTS = {
    "Tesco": ["Groceries", "Food & Drink", "Transport", "Health"],
    "Sainsbury's": ["Groceries", "Food & Drink"],
    "Amazon": ["Shopping", "Entertainment", "Groceries", "Health"],
    "Marks & Spencer": ["Groceries", "Food & Drink", "Shopping"],
    "Boots": ["Health", "Shopping"],
    "Co-op": ["Groceries", "Food & Drink"],
    "PayPal": ["Shopping", "Entertainment", "Other"],
    "Costco": ["Groceries", "Shopping"],
}

# category -> (merchants, descriptions, (amount_mean, amount_std, amount_min))
CATEGORY_PROFILES = {
    "Food & Drink": (
        ["Coffee Shop", "Starbucks", "Costa Coffee", "Local Cafe", "Pret A Manger", "Greggs", "Bubble Tea Co"],
        ["Coffee", "Latte and pastry", "Lunch coffee", "Tea and snack", "Breakfast order", "Meal deal", "Takeaway"],
        (8.5, 7.0, 1.5),
    ),
    "Groceries": (
        ["Supermarket", "Aldi", "Lidl", "Whole Foods", "Local Grocer", "Iceland"],
        ["Weekly shop", "Grocery run", "Household supplies", "Food shopping", "Top-up shop"],
        (38.0, 26.0, 3.0),
    ),
    "Transport": (
        ["Subway Ticket", "Uber", "Bus Pass", "Train Ticket", "Taxi", "Lyft", "City Metro", "Shell", "BP"],
        ["Commute fare", "Ride home", "Monthly travel pass", "Airport transfer", "Taxi ride", "Fuel", "Parking"],
        (14.0, 15.0, 1.5),
    ),
    "Entertainment": (
        ["Netflix", "Spotify", "Cinema", "Steam", "Disney+", "Concert Tickets", "PlayStation Store"],
        ["Monthly subscription", "Movie night", "Game purchase", "Streaming renewal", "Event ticket"],
        (18.0, 16.0, 2.0),
    ),
    "Utilities": (
        ["Electric Bill", "Water Bill", "Gas Bill", "Internet Provider", "Mobile Network", "Council Tax"],
        ["Monthly utility bill", "Energy payment", "Broadband bill", "Phone bill", "Utility direct debit"],
        (68.0, 32.0, 12.0),
    ),
    "Rent": (
        ["Landlord Payment", "Property Management Co", "Student Halls", "Letting Agency"],
        ["Monthly rent", "Rent payment", "Accommodation fee"],
        (620.0, 180.0, 250.0),
    ),
    "Health": (
        ["Pharmacy", "Dentist", "GP Surgery", "Gym Membership", "Opticians", "Superdrug"],
        ["Prescription", "Dental checkup", "Gym monthly fee", "Health insurance", "Eye test"],
        (32.0, 26.0, 4.0),
    ),
    "Shopping": (
        ["Zara", "H&M", "Apple Store", "eBay", "ASOS", "Electronics Store", "IKEA"],
        ["Online order", "Clothing purchase", "Gadget purchase", "Retail purchase", "Gift shopping"],
        (58.0, 45.0, 4.0),
    ),
    "Other": (
        ["ATM Withdrawal", "Bank Fee", "Charity Donation", "Miscellaneous", "Unknown Merchant"],
        ["Cash withdrawal", "Service charge", "Donation", "Misc expense", "One-off payment"],
        (35.0, 34.0, 1.0),
    ),
}

CATEGORIES = list(CATEGORY_PROFILES.keys())

_AMBIGUOUS_BY_CATEGORY = {category: [] for category in CATEGORIES}
for _merchant, _categories in AMBIGUOUS_MERCHANTS.items():
    for _category in _categories:
        _AMBIGUOUS_BY_CATEGORY[_category].append(_merchant)


def generate_dataset(n_per_category: int = 400, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    rows = []

    for category, (merchants, descriptions, (mean, std, minimum)) in CATEGORY_PROFILES.items():
        shared = _AMBIGUOUS_BY_CATEGORY[category]
        for _ in range(n_per_category):
            if shared and rng.random() < AMBIGUOUS_MERCHANT_RATE:
                merchant = rng.choice(shared)
            else:
                merchant = rng.choice(merchants)

            if rng.random() < GENERIC_DESCRIPTION_RATE:
                description = rng.choice(GENERIC_DESCRIPTIONS)
            else:
                description = rng.choice(descriptions)

            amount = max(minimum, round(float(np_rng.normal(mean, std)), 2))

            rows.append(
                {
                    "merchant": merchant,
                    "description": description,
                    "amount": amount,
                    "category": category,
                }
            )

    df = pd.DataFrame(rows)

    n_noisy = int(len(df) * LABEL_NOISE_RATE)
    for idx in np_rng.choice(len(df), size=n_noisy, replace=False):
        alternatives = [c for c in CATEGORIES if c != df.at[idx, "category"]]
        df.at[idx, "category"] = rng.choice(alternatives)

    return df.sample(frac=1, random_state=seed).reset_index(drop=True)
