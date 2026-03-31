#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_SPLIT_CHAR = "-"
CATEGORY_SPLIT_CHAR = "::"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

CATEGORIES_LIST = list()

MONTH_RANGE = range(1, 13)
DATE_LEN = 3
FEB = 2
VALID_PART_DATE_LEN = (2, 2, 4)

financial_transactions_storage: list[dict[str, Any]] = []

STATS_TEMPLATE = """Your statistics as of {stats_date}:
Total capital: {total_capital} rubles
This month, the {amount_word} amounted to {total_capital} rubles.
Income: {costs_amount} rubles
Expenses: {incomes_amount} rubles

Details (category: amount):
{category_details_stat}
"""


def init_categories() -> None:
    global CATEGORIES_LIST
    for category in EXPENSE_CATEGORIES.keys():
        for sub_category in EXPENSE_CATEGORIES[category]:
            CATEGORIES_LIST.append(category + CATEGORY_SPLIT_CHAR + sub_category)


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def is_valid_len_date(date: tuple[str, ...]) -> bool:
    for i in range(DATE_LEN):
        if len(date[i]) != VALID_PART_DATE_LEN[i]:
            return False
    return len(date) == DATE_LEN


def get_correct_day(month: int, year: int) -> int:
    correct_day = 30 + (month + (month // 8)) % 2
    if month == FEB:
        correct_day = 28 + int(is_leap_year(year))
    return correct_day


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    date = tuple(maybe_dt.split(DATE_SPLIT_CHAR))
    if not is_valid_len_date(date):
        return None

    day, month, year = map(int, date)
    if month not in MONTH_RANGE:
        return None
    if day > get_correct_day(month, year) or day <= 0:
        return None
    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    financial_transactions_storage.append({"amount": amount, "date": date})
    return OP_SUCCESS_MSG


def is_valid_category(category_name: str) -> bool:
    if CATEGORY_SPLIT_CHAR in category_name:
        category, sub_category = category_name.split(CATEGORY_SPLIT_CHAR)
        if category in EXPENSE_CATEGORIES and sub_category in EXPENSE_CATEGORIES[category]:
            return True
    return False


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date = extract_date(income_date)
    if not is_valid_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    init_categories()
    return "\n".join(CATEGORIES_LIST)


def calculate_stats(report_date: tuple[int, int, int]) -> tuple:
    report_day, report_month, report_year = report_date
    report_comparable = (report_year, report_month, report_day)

    costs_amount, incomes_amount = 0.0, 0.0
    category_details: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        raw_date = transaction["date"]
        day, month, year = raw_date if isinstance(raw_date, tuple) else extract_date(raw_date)

        if (year, month, day) > report_comparable:
            continue

        amount = float(transaction["amount"])
        if "category" in transaction:
            costs_amount += amount
            category = transaction["category"]
            category_details[category] = category_details.get(category, 0.0) + amount
        else:
            incomes_amount += amount

    for category in category_details:
        category_details[category] = round(category_details[category], 2)

    return round(costs_amount, 2), round(incomes_amount, 2), category_details


def format_stats_output(report_date: str, costs_amount: float, incomes_amount: float, category_details: dict) -> str:
    total_capital = round(costs_amount - incomes_amount, 2)
    amount_word = "loss" if total_capital < 0 else "profit"

    category_details_list = []
    for index, category in enumerate(category_details.keys()):
        category_details_list.append(f"{index}. {category}: {category_details[category]}")

    return STATS_TEMPLATE.format_map({
        "stats_date": report_date,
        "total_capital": total_capital,
        "amount_word": amount_word,
        "costs_amount": costs_amount,
        "incomes_amount": incomes_amount,
        "category_details_stat": "\n".join(category_details_list)
    })


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG

    costs_amount, incomes_amount, category_details = calculate_stats(date)
    return format_stats_output(report_date, costs_amount, incomes_amount, category_details)


def income_query_handler(*args) -> str:
    if len(args) == 2:
        return income_handler(float(args[0]), args[1])
    return UNKNOWN_COMMAND_MSG


def cost_query_handler(*args) -> str:
    if len(args) == 1 and args[0] == "categories":
        return cost_categories_handler()
    if len(args) == 3:
        return cost_handler(args[0], float(args[1]), args[2])
    return UNKNOWN_COMMAND_MSG


def stats_query_handler(*args) -> str:
    if len(args) == 1:
        return stats_handler(args[0])
    return UNKNOWN_COMMAND_MSG


def dispatch_command() -> None:
    parts = tuple(input().strip().split())
    if not parts:
        return
    cmd = parts[0]
    args = parts[1:]
    match cmd:
        case "income":
            print(income_query_handler(*args))
        case "cost":
            print(cost_query_handler(*args))
        case "stats":
            print(stats_query_handler(*args))
        case _:
            print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    init_categories()
    while True:
        dispatch_command()


if __name__ == "__main__":
    main()
