import pandas as pd
import os
from dotenv import load_dotenv
from threshold import ter_thresholds

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

ter_thresholds = ter_thresholds

def calculate_ter(marriage_status, dependencies):
    if not marriage_status:
        if dependencies <= 1:
            return "A"
        elif dependencies <= 3:
            return "B"
    else:
        if dependencies == 0:
            return "A"  # Correctly handles married with no dependencies
        elif dependencies <= 2:
            return "B"
        elif dependencies == 3:
            return "C" 
    return "C"

# Calculate taxable gross salary
def calculate_gross_salary(monthly_salary):
    bonus = (monthly_salary * 0.24 / 100) + (monthly_salary * 0.3 / 100)
    additional = monthly_salary * 4 / 100 if monthly_salary <= 10000000 else 480000
    return monthly_salary + bonus + additional

# Find Tax Rate using dictionary ter_thresholds
def find_tax_rate(gross_salary, classification):
    for range in ter_thresholds[classification]:
        if range["lower_threshold"] <= gross_salary <= range["upper_threshold"]:
            return range["tax_rate"]
    return 0

# Calculate Salary Tax 
def calculate_salary_tax(gross_salary, tax_rate):
    return gross_salary * tax_rate

# Calculate Net Salary
def calculate_nett_salary1(monthly_salary, salary_tax):
    bpjs_kes_deduction = monthly_salary * 0.01 if monthly_salary < 12000000 else 120000
    bpjs_tk_deduction = monthly_salary * 2 / 100
    conditional_deduction = monthly_salary * 1 / 100 if monthly_salary < 10042300 else 100423
    nett_salary = monthly_salary - bpjs_kes_deduction - bpjs_tk_deduction - conditional_deduction - salary_tax
    return nett_salary

# ------- Main Calculate Nett Salary Calculator ------
def monthly_to_net_calculator(monthly_salary: int, marriage_status: bool, dependencies: int) -> str:
    """Use this function to calculate an individual's nett salary when given their monthly salary, their marital status, and their number of dependents.

    Args:
        monthly_salary (int): The individual's monthly salary.
        marriage_status (bool): The individual's marital status.
        dependencies (int): The individual's number of dependents.
    
    Returns:
        str: A string containing the individual's TER, gross salary, tax rate, salary tax, and nett salary.
    """
    ter = calculate_ter(marriage_status, dependencies)
    gross_salary = calculate_gross_salary(monthly_salary)
    tax_rate = find_tax_rate(gross_salary, ter)
    salary_tax = calculate_salary_tax(gross_salary, tax_rate)
    nett_salary = calculate_nett_salary1(monthly_salary, salary_tax)

    result = (
        f"TER: {ter}\n"
        f"Gross Salary: IDR {gross_salary:,.0f}\n"
        f"Tax Rate (%): {tax_rate:.2%}\n"
        f"Salary Tax: IDR {salary_tax:,.0f}\n"
        f"Nett Salary: IDR {nett_salary:,.0f}"
    )

    return result

# ------- Main Calculate Monthyl Salary Calculator -------
def nett_to_monthly_calculator(nett_salary: int, marriage_status: bool, dependencies: int) -> str:
    """Calculate the monthly salary based on the given net salary, marital status, and number of dependents.

    Args:
        nett_salary (int): The individual's net salary.
        marriage_status (bool): The individual's marital status.
        dependencies (int): The individual's number of dependents.
    
    Returns:
        str: A string containing the individual's nett salary, monthly salary, TER, gross salary, tax rate, and salary tax.
    """
    # Initialize bounds
    lower_bound = nett_salary // 2
    upper_bound = nett_salary * 2
    monthly_salary = (lower_bound + upper_bound) // 2

    while lower_bound <= upper_bound:
        result = monthly_to_net_calculator(monthly_salary, marriage_status, dependencies)
        print(f"Debug: result = {result}")  # Debug print
        calculated_nett_salary = float(result["Nett Salary"].replace("IDR ", "").replace(",", ""))
        
        if abs(calculated_nett_salary - nett_salary) < 1:
            break
        elif calculated_nett_salary < nett_salary:
            lower_bound = monthly_salary + 1
        else:
            upper_bound = monthly_salary - 1
        
        monthly_salary = (lower_bound + upper_bound) // 2

    # If the binary search loop did not find an exact match, use linear search for fine adjustment
    for adjustment in range(-5, 6):
        test_salary = monthly_salary + adjustment
        result = monthly_to_net_calculator(test_salary, marriage_status, dependencies)
        print(f"Debug: test_salary = {test_salary}, result = {result}")  # Debug print
        calculated_nett_salary = float(result["Nett Salary"].replace("IDR ", "").replace(",", ""))
        
        if abs(calculated_nett_salary - nett_salary) < 1:
            monthly_salary = test_salary
            break

    result_string = (
        f"Nett Salary: IDR {nett_salary:,.0f}\n"
        f"Monthly Salary: IDR {monthly_salary:,.0f}\n"
        f"TER: {result['TER']}\n"
        f"Gross Salary: {result['Gross Salary']}\n"
        f"Tax Rate (%): {result['Tax Rate (%)']}\n"
        f"Salary Tax: {result['Salary Tax']}"
    )

    return result_string





assistant = Assistant(tools=[nett_to_monthly_calculator], show_tool_calls=True, markdown=True, debug_mode=True)
assistant.print_response("Nett salary: IDR 9,338,650, Marital Status: Single, Number of Dependents: 0")