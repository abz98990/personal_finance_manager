"""Synthetic transaction data generator.

Real, labelled personal-transaction data is sensitive and hard to obtain (see
IPR section 4.2/5.2), so training data here is generated from realistic
merchant/description templates and amount distributions per category. This
keeps the pipeline fully reproducible and free of PII while still exercising
the same text + amount feature space real bank data would produce.
"""
import random

import numpy as np
import pandas as pd

RANDOM_SEED = 42

# category -> (merchants, description templates, (amount_mean, amount_std, amount_min))
CATEGORY_PROFILES = {
    "Food & Drink": (
        ["Coffee Shop", "Starbucks", "Costa Coffee", "Local Cafe", "Pret A Manger", "Greggs", "Bubble Tea Co"],
        ["Coffee", "Latte and pastry", "Lunch coffee", "Tea and snack", "Breakfast order"],
        (5.5, 3.0, 1.5),
    ),
    "Groceries": (
        ["Supermarket", "Tesco", "Sainsbury's", "Aldi", "Lidl", "Whole Foods", "Local Grocer"],
        ["Weekly shop", "Grocery run", "Household supplies", "Food shopping", "Top-up shop"],
        (42.0, 22.0, 5.0),
    ),
    "Transport": (
        ["Subway Ticket", "Uber", "Bus Pass", "Train Ticket", "Taxi", "Lyft", "City Metro"],
        ["Commute fare", "Ride home", "Monthly travel pass", "Airport transfer", "Taxi ride"],
        (9.0, 8.0, 1.5),
    ),
    "Entertainment": (
        ["Netflix", "Spotify", "Cinema", "Steam", "Disney+", "Concert Tickets", "PlayStation Store"],
        ["Monthly subscription", "Movie night", "Game purchase", "Streaming renewal", "Event ticket"],
        (14.0, 12.0, 3.0),
    ),
    "Utilities": (
        ["Electric Bill", "Water Bill", "Gas Bill", "Internet Provider", "Mobile Network", "Council Tax"],
        ["Monthly utility bill", "Energy payment", "Broadband bill", "Phone bill", "Utility direct debit"],
        (65.0, 25.0, 15.0),
    ),
    "Rent": (
        ["Landlord Payment", "Property Management Co", "Student Halls", "Letting Agency"],
        ["Monthly rent", "Rent payment", "Accommodation fee"],
        (650.0, 150.0, 300.0),
    ),
    "Health": (
        ["Pharmacy", "Boots", "Dentist", "GP Surgery", "Gym Membership", "Opticians"],
        ["Prescription", "Dental checkup", "Gym monthly fee", "Health insurance", "Eye test"],
        (28.0, 20.0, 4.0),
    ),
    "Shopping": (
        ["Amazon", "Zara", "H&M", "Apple Store", "eBay", "ASOS", "Electronics Store"],
        ["Online order", "Clothing purchase", "Gadget purchase", "Retail purchase", "Gift shopping"],
        (55.0, 40.0, 5.0),
    ),
    "Other": (
        ["ATM Withdrawal", "Bank Fee", "Charity Donation", "Miscellaneous", "Unknown Merchant"],
        ["Cash withdrawal", "Service charge", "Donation", "Misc expense", "One-off payment"],
        (30.0, 30.0, 1.0),
    ),
}

CATEGORIES = list(CATEGORY_PROFILES.keys())


def generate_dataset(n_per_category: int = 400, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    rows = []

    for category, (merchants, descriptions, (mean, std, minimum)) in CATEGORY_PROFILES.items():
        for _ in range(n_per_category):
            merchant = rng.choice(merchants)
            description = rng.choice(descriptions)
            amount = float(np_rng.normal(mean, std))
            amount = max(minimum, round(amount, 2))
            rows.append(
                {
                    "merchant": merchant,
                    "description": description,
                    "amount": amount,
                    "category": category,
                }
            )

    df = pd.DataFrame(rows)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)
