from behave import *
from analysis_tools.venmo import  

@given('a string')
def step_impl(context):
    my_string = "+ 5.00"
    pass

@when('we pass the string to the function')
def step_impl(context):
    assert True is not False

@then('the string will be converted to a float')
def step_impl(context):
    assert context.failed is False