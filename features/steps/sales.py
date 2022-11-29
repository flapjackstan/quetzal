from behave import *
from analysis_tools.venmo import transaction_to_float

@given('a string')
def step_impl(context):
    context.my_string = "+ 5.00"
    pass

@when('we pass the string to the function')
def step_impl(context):
    context.result = transaction_to_float(context.my_string)

@then('the string will be converted to a float')
def step_impl(context):
    assert context.result == float(5.00)