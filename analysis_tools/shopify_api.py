# -*- coding: utf-8 -*-

'''
Shopify helper functions

'''
from pathlib import Path
import json

def read_json(path, filename, ext) -> dict:
    '''
    
    Parameters
    ----------
    path : Path object
        Path object / destination.
    filename : str
        Name of file to write
    ext : str
        File type extension.

    Returns
    -------
    dict
        json converted to dictionary

    '''
    
    read_path = Path(path)
    
    with open(read_path.joinpath(filename + ext)) as json_file:
        data = json.load(json_file)
        
    return json.loads(data)


def write_file(obj, path, filename, ext) -> None:
    '''
    Parameters
    ----------
    obj : df | dict
        Object to write.
    path : Path object
        Path object / destination.
    filename : str
        Name of file to write
    ext : str
        File type extension.

    Returns
    -------
    None.
    '''
    
    write_path = Path(path)

    with open(write_path.joinpath(filename + ext), "w+") as f:
        json.dump(obj, f)


def read_file_as_text(path) -> str:
    """
    Parameters
    ----------
    path  :   str
    path to file to be read
    
    Returns
    -------
    file_text    :   str
    text from file
    
    Example
    -------
    read_sql("my_file.gql")
        "query { shop { name id } }"
    """
    file_text = Path(path).read_text(encoding="utf-8")
    
    # error handling?
    
    return file_text


def convert_dict_to_json(py_dict) -> str:
    """
    Parameters
    ----------
    py_dict  :   dict
    dict to convert to json
    
    Returns
    -------
    json_return    :   str
    json version of dict
    
    Example
    -------
    convert_dict_to_json({key:"value"})
        "{key:"value"}"
    """
    json_return = json.dumps(py_dict)
    
    # error handling?
    
    return json_return


def execute_gql(gql, variables, json_return=0):
    """
    Parameters
    ----------
    gql  :   str
    gql to be executed
    
    Returns
    -------
    query_return    :   dict | str
    text from file
    
    Example
    -------
    execute_gql("query { shop { name id } }")
        {shop: tazacafe}
    """
    
    with shopify.Session.temp(SHOP_URL, API_VERSION, SHOPIFY_ADMIN_TOKEN):

        # below converts shopify return json (not ecma-262) into a python dict
        query_return = json.loads(shopify.GraphQL().execute(gql, variables=variables))
        
    if json_return:
        # below converts the python dict into a json (ecma-262) that is able to be uploaded to postgres
        query_return = convert_dict_to_json(query_return["data"])
    
    # error handling?
    
    return query_return


def get_orders_between_dates(date_1, date_2) -> list:
    """
    Parameters
    ----------
    date_1  :   str
    Begin date filter
    
    date_2  :   str
    End date fiter
    
    Returns
    -------
    query_return    :   dict | str
    text from file
    
    Example
    -------
    get_orders_between_dates("2022-12-01", "2022-12-31")
        orders return from shopify
    """
    
    print(f"Getting orders between {date_1} and {date_2}")
    
    query = read_file_as_text("analysis_tools/queries/orders.gql")
    date_filter = f"processed_at:>{date_1} AND processed_at:<{date_2}"
    input_vars = {"user_query": date_filter}
    
    first_return = execute_gql(gql=query, json_return=0, variables=input_vars)
    
    has_next_page = first_return["data"]["orders"]["pageInfo"]["hasNextPage"]
    end_cursor = first_return["data"]["orders"]["pageInfo"]["endCursor"]
    
    print(f"Has Next Page: {has_next_page}")
    # print(f"End Cursor: {end_cursor}")
    
    return_list = []
    return_list.append(first_return)
    
    while has_next_page and len(return_list) < 100:
        
        query = read_file_as_text("analysis_tools/queries/keep_getting_orders.gql")
        date_filter = f"processed_at:>{date_1} AND processed_at:<{date_2}"
        input_vars = {"user_query": date_filter, "prev_cursor": end_cursor}
        
        shopify_returns = execute_gql(gql=query, json_return=0, variables=input_vars)
        print(shopify_returns["data"]["orders"]["nodes"][0]["name"])
        return_list.append(shopify_returns)
        
        has_next_page = shopify_returns["data"]["orders"]["pageInfo"]["hasNextPage"]
        end_cursor = shopify_returns["data"]["orders"]["pageInfo"]["endCursor"]
        
        # print(f"Has Next Page: {has_next_page}")
        # print(f"End Cursor: {end_cursor}")
        print(f"Request Number: {len(return_list)}")
    
    query_return = return_list
    
    # error handling?
    
    return query_return


def get_order_data(order) -> dict:
    '''
    

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    dict
        data dict from individual order.

    '''
    
    return order["data"]["orders"]["nodes"][0]


def get_line_items(order) -> dict:
    data = get_order_data(order)
    return data["lineItems"]["nodes"]

def get_count_orders(order) -> int:
    line_items = get_line_items(order)
    return len(line_items)

def get_count_of_product(order, product) -> int:
    line_items = get_line_items(order)
    product_count = 0
    
    for index, item in enumerate(line_items):
        if product in item["name"]:
            product_count = product_count + 1
    
    return(product_count)
