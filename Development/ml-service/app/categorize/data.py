"""Synthetic transaction data generator.

Real, labelled personal-transaction data is sensitive and hard to obtain (see
FPR chapter on ethics), so training data here is generated from realistic
merchant/description templates and amount distributions per category. This
keeps the pipeline fully reproducible and free of PII while still exercising
the same text + amount feature space real bank data would produce.

The generator deliberately models the four properties that make real
transaction categorisation hard, rather than producing trivially separable
classes:

1. **Ambiguous merchants** - a supermarket sells groceries, fuel and a coffee;
   Amazon sells books, groceries and a streaming subscription. Such merchants
   are sampled into several categories, so the merchant token alone is not a
   reliable label.
2. **Uninformative descriptions** - a large share of real bank rows carry
   generic memos ("CARD PAYMENT", "CONTACTLESS") that provide no signal, so
   the classifier must fall back on merchant and amount.
3. **Overlapping amounts** - category amount distributions are heavy-tailed
   and overlap, so amount is informative but not decisive.
4. **Label noise** - users miscategorise their own spending; a small
   proportion of labels are randomly corrupted.

Together these give a realistic, non-saturated evaluation in which different
algorithms can be meaningfully compared.
"""
import random

import numpy as np
import pandas as pd

RANDOM_SEED = 42

# Proportion of rows whose description is replaced by an uninformative memo.
GENERIC_DESCRIPTION_RATE = 0.35
# Proportion of rows whose label is randomly corrupted (user miscategorisation).
LABEL_NOISE_RATE = 0.05

# Memos that carry no category signal, mirroring real bank statement exports.
GENERIC_DESCRIPTIONS = [
    "Card payment",
    "Contactless payment",
    "Online purchase",
    "Debit card transaction",
    "Payment",
    "POS purchase",
]

# Merchants that legitimately sell across several categories. Each is listed
# under every category it plausibly belongs to, so the model cannot treat the
# merchant token as a unique key for a class.
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

# category -> (merchants, description templates, (amount_mean, amount_std, amount_min))
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

# Reverse index: category -> ambiguous merchants that can appear under it.
_AMBIGUOUS_BY_CATEGORY = {category: [] for category in CATEGORIES}
for _merchant, _categories in AMBIGUOUS_MERCHANTS.items():
    for _category in _categories:
        _AMBIGUOUS_BY_CATEGORY[_category].append(_merchant)


def generate_dataset(
    n_per_category: int = 400,
    seed: int = RANDOM_SEED,
    ambiguous_merchant_rate: float = 0.30,
    generic_description_rate: float = GENERIC_DESCRIPTION_RATE,
    label_noise_rate: float = LABEL_NOISE_RATE,
) -> pd.DataFrame:
    """Builds a labelled transaction dataset with realistic class overlap.

    Set the three rate arguments to 0.0 to recover a trivially separable
    dataset; the FPR uses that configuration as an ablation baseline to show
    how much of the achievable score is due to the task rather than the model.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    rows = []

    for category, (merchants, descriptions, (mean, std, minimum)) in CATEGORY_PROFILES.items():
        shared = _AMBIGUOUS_BY_CATEGORY[category]
        for _ in range(n_per_category):
            # Some rows come from merchants that also trade in other categories.
            if shared and rng.random() < ambiguous_merchant_rate:
                merchant = rng.choice(shared)
            else:
                merchant = rng.choice(merchants)

            # Some rows carry a generic memo with no category signal.
            if rng.random() < generic_description_rate:
                description = rng.choice(GENERIC_DESCRIPTIONS)
            else:
                description = rng.choice(descriptions)

            # Log-normal-ish amounts: right-skewed and overlapping between classes.
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

    # Users miscategorise their own spending; corrupt a small share of labels.
    if label_noise_rate > 0:
        n_noisy = int(len(df) * label_noise_rate)
        noisy_idx = np_rng.choice(len(df), size=n_noisy, replace=False)
        for idx in noisy_idx:
            true_label = df.at[idx, "category"]
            alternatives = [c for c in CATEGORIES if c != true_label]
            df.at[idx, "category"] = rng.choice(alternatives)

    return df.sample(frac=1, random_state=seed).reset_index(drop=True)
