#!/usr/bin/env python

from typing import Any

DateTuple = tuple[int, int, int]
StatsResult = tuple[float, float, dict[str, float]]

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_SPLIT_CHAR = "-"
CATEGORY_SPLIT_CHAR = "::"
USER_FLOAT_POINT_CHAR = ","
NORMAL_FLOAT_POINT_CHAR = "."

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

CATEGORIES_TUPLE: tuple[str, ...] = tuple(
    f"{category}{CATEGORY_SPLIT_CHAR}{sub}"
    for category, sub_categories in EXPENSE_CATEGORIES.items()
    for sub in sub_categories
)

MONTH_RANGE = range(1, 13)
DATE_LEN = 3
VALID_PART_DATE_LEN = (2, 2, 4)
MIN_DAY = 1
FEB = 2

CATEGORIES_LEN = 2
CMD_INCOME_ARGS = 2
CMD_COST_ARGS = 3

financial_transactions_storage: list[dict[str, Any]] = []

STATS_TEMPLATE = """Your statistics as of {stats_date}:
Total capital: {total_capital} rubles
This month, the {amount_word} amounted to {unsigned_total_capital} rubles.
Income: {incomes_amount} rubles
Expenses: {costs_amount} rubles

Details (category: amount):
{category_details_stat}
"""


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


def get_max_day(month: int, year: int) -> int:
    correct_day = 30 + (month + (month // 8)) % 2
    if month == FEB:
        correct_day = 28 + int(is_leap_year(year))
    return correct_day


def extract_date(maybe_dt: str) -> DateTuple | None:
    date_parts = tuple(maybe_dt.split(DATE_SPLIT_CHAR))
    if not is_valid_len_date(date_parts):
        return None

    if not all(part.isdigit() for part in date_parts):
        return None

    day, month, year = map(int, date_parts)

    if month not in MONTH_RANGE:
        return None
    if day not in range(MIN_DAY, get_max_day(month, year) + 1):
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
        parts = category_name.split(CATEGORY_SPLIT_CHAR)
        if len(parts) == CATEGORIES_LEN:
            category, sub_category = parts
            if category in EXPENSE_CATEGORIES and sub_category in EXPENSE_CATEGORIES[category]:
                return True
    return False


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_valid_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    date = extract_date(income_date)
    if date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(CATEGORIES_TUPLE)


def calculate_stats(report_date: DateTuple) -> StatsResult:
    report_comp = (report_date[2], report_date[1], report_date[0])

    costs_amount = float(0)
    incomes_amount = float(0)
    category_details: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        date = transaction.get("date")
        if not date:
            continue
        trans_date = (date[2], date[1], date[0])
        if trans_date > report_comp:
            continue

        amount = float(transaction.get("amount", 0))
        category_full = transaction.get("category")
        if category_full:
            costs_amount += amount
            _category, sub_category = category_full.split(CATEGORY_SPLIT_CHAR)
            category_details[sub_category] = category_details.get(sub_category, 0) + amount
        else:
            incomes_amount += amount

    for category, amount in category_details.items():
        category_details[category] = round(amount, 2)

    return round(incomes_amount, 2), round(costs_amount, 2), category_details


def convert_to_user_point_char(num: float) -> str:
    return str(num).replace(NORMAL_FLOAT_POINT_CHAR, USER_FLOAT_POINT_CHAR)


def convert_to_normal_point_char(num: str) -> str:
    return num.replace(USER_FLOAT_POINT_CHAR, NORMAL_FLOAT_POINT_CHAR)


def format_stats_output(
    report_date: str,
    incomes_amount: float,
    costs_amount: float,
    category_details: dict[str, float],
) -> str:
    total_capital = round(incomes_amount - costs_amount, 2)
    unsigned_total_capital = abs(total_capital)
    amount_word = "loss" if total_capital < 0 else "profit"

    total_capital_str = convert_to_user_point_char(total_capital)
    unsigned_total_capital_str = convert_to_user_point_char(unsigned_total_capital)
    costs_amount_str = convert_to_user_point_char(costs_amount)
    incomes_amount_str = convert_to_user_point_char(incomes_amount)

    category_details_list: list[str] = []
    for idx, (category, amount) in enumerate(category_details.items(), start=1):
        amount_str = convert_to_user_point_char(amount)
        category_details_list.append(f"{idx}. {category}: {amount_str}")

    return STATS_TEMPLATE.format_map(
        {
            "stats_date": report_date,
            "total_capital": total_capital_str,
            "unsigned_total_capital": unsigned_total_capital_str,
            "amount_word": amount_word,
            "costs_amount": costs_amount_str,
            "incomes_amount": incomes_amount_str,
            "category_details_stat": "\n".join(category_details_list),
        },
    )


def stats_handler(report_date: str) -> str:
    date = extract_date(report_date)
    if date is None:
        return INCORRECT_DATE_MSG
    incomes_amount, costs_amount, category_details = calculate_stats(date)
    return format_stats_output(report_date, incomes_amount, costs_amount, category_details)


def is_valid_float_str(s: str) -> bool:
    if s.count(".") > 1:
        return False
    return s.replace(".", "", 1).isdigit()


def income_query_handler(*args: str) -> str:
    if len(args) == CMD_INCOME_ARGS:
        amount_str, date_str = args
        if not is_valid_float_str(amount_str):
            return UNKNOWN_COMMAND_MSG
        return income_handler(float(amount_str), date_str)
    return UNKNOWN_COMMAND_MSG


def cost_query_handler(*args: str) -> str:
    if len(args) == 1 and args[0] == "categories":
        return cost_categories_handler()
    if len(args) == CMD_COST_ARGS:
        category, amount_str, date_str = args
        if not is_valid_float_str(amount_str):
            return UNKNOWN_COMMAND_MSG
        return cost_handler(category, float(amount_str), date_str)
    return UNKNOWN_COMMAND_MSG


def stats_query_handler(*args: str) -> str:
    if len(args) == 1:
        return stats_handler(args[0])
    return UNKNOWN_COMMAND_MSG


def dispatch_command(cmd: str, args: tuple[str, ...]) -> None:
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
    while True:
        user_input_str = input().strip()
        if not user_input_str:
            break

        user_input_parts = convert_to_normal_point_char(user_input_str).split()
        if not user_input_parts:
            continue

        cmd, *args = user_input_parts
        dispatch_command(cmd, tuple(args))


if __name__ == "__main__":
    main()
