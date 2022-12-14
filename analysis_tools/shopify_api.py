# -*- coding: utf-8 -*-

'''
Shopify helper functions

'''
from pathlib import Path
import json
from datetime import datetime, timedelta

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


# do this for gross sales. look at #1087, original total unit price set
def get_count_of_product(order, product) -> int:
    line_items = get_line_items(order)
    product_count = 0
    
    for index, item in enumerate(line_items):
        if product in item["name"]:
            product_count = product_count + 1
    
    return(product_count)


# get all items available in the time period

def get_items_available(orders):
    items_list = []
    
    for index, order in enumerate(orders):
        
        line_items = get_line_items(order)
        
        for index, item in enumerate(line_items):
            if item["name"] in items_list:
                pass
            else:
                items_list.append(item["name"])
            
    return items_list


def get_aggs(orders_list, timeframe) -> dict:
    '''

    Parameters
    ----------
    orders_dict : dict
        shopify order return

    Returns
    -------
    dict : agg_dict
        dictionary with summary aggregates

    '''
    
    timeframe = get_timeframe(timeframe)
    
    agg_dict = {}
    
    total_tips = 0
    total_collected = 0
    total_fees = 0
    total_cash_collected = 0
    order_count = 0
    
    items_available = get_items_available(orders_list)
    items_dict = {}
    
    for index, item in enumerate(items_available):
        entry = {}
        entry["product name"] = item
        entry["count"] = 0
        items_dict[index] = entry
    
    
    for index, order in enumerate(orders_list):
        
        pst = get_time_of_order(order)
        
        if timeframe[0].date() <= pst.date() <= timeframe[1].date():
        
            tip_amount = get_order_tips(order)

            for index, item in enumerate(items_available):
                items_dict[index]["count"] = items_dict[index]["count"] + get_count_of_product(order, item)
            
            
            total_tips = total_tips + tip_amount
                
            # MONEY COLLECTED AND FEES
            
            total_collected = total_collected + get_order_total_collected(order)
            total_fees = total_fees + get_fee(order)
    
            total_cash_collected = total_cash_collected + get_cash_collected(order)
            
            # SIMPLE COUNT OF ORDERS
            order_count = order_count + 1
        
    total_sales = total_collected - total_tips
        
    agg_dict.update({"Total Orders": order_count})
    agg_dict.update({"Total Collected": total_collected})
    agg_dict.update({"Total Tips Collected": total_tips})
    agg_dict.update({"Total Sales": total_sales})
    agg_dict.update({"Total Fees": total_fees})
    agg_dict.update({"Total Paid in Cash": total_cash_collected})
    agg_dict.update({"Total Paid in Credit": total_collected - total_cash_collected})
    agg_dict.update({"Product Dictionary": items_dict})
    
    return agg_dict

def is_void(order) -> bool:
    '''
    

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    bool
        True if order is voided

    '''
    financial_status = order["data"]["orders"]["nodes"][0]["displayFinancialStatus"]
    
    if financial_status == "VOIDED":
        return True
    
    return False
     

def is_unfulfilled(order) -> bool:
    '''
    

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    bool
        True if order is unfulfilled

    '''
    financial_status = order["data"]["orders"]["nodes"][0]["displayFulfillmentStatus"]
    
    if financial_status == "UNFULFILLED":
        return True
    
    return False


def has_tags(search_tags, tag_list) -> bool:
    '''
    

    Parameters
    ----------
    search_tags : list
        list of hashtags to look for in tag_list.
    
    tag_list : list
        list of hashtags to check.

    Returns
    -------
    bool
        True if tags are present.

    '''
    
    for tag in tag_list:
        if tag in search_tags:
            return True
        
    return False
        

def get_order_total_collected(order) -> float:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        Money collected from transaction.

    '''
    
    if is_void(order) or is_unfulfilled(order) or has_tags(["test"], get_order_data(order)["tags"]):
        return(float(0))
    
    total_amount = order["data"]["orders"]["nodes"][0]["originalTotalPriceSet"]["shopMoney"]["amount"]
    
    return float(total_amount)


def get_customer_orders(order) -> list:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        List of customer orders including Tip

    '''
    
    return order["data"]["orders"]["nodes"][0]["lineItems"]["nodes"]


def get_tip_amount(order_list) -> float:
    '''

    Parameters
    ----------
    order_list : list
        customer orders list.

    Returns
    -------
    float
        Money collected from tips.

    '''
    
    for index, order in enumerate(order_list):
        
        if "Tip" in order["name"]:
            tip_amount = order["originalTotalSet"]["shopMoney"]["amount"]
        else:
            tip_amount = 0.0
    
    return float(tip_amount)


def get_order_tips(order) -> float:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        Money collected from tips. If no tip is collected this is 0

    '''
    
    cutomer_orders = get_customer_orders(order)
    tip_amount = get_tip_amount(cutomer_orders)
    
    return tip_amount


def get_fee(order) -> float:
    '''

    Parameters
    ----------
    order : dict
        shopify order dictionary.

    Returns
    -------
    float
        Fees Collected

    '''
    
    data = get_order_data(order)
    
    # some have empty transactions
    if not data["transactions"]:
        return 0.0
    
    # some paid cash and there is no fee
    if not data["transactions"][0]["fees"]:
        return 0.0

    return float(data["transactions"][0]["fees"][0]["amount"]["amount"])


def get_timeframe(timeframe_str) -> list:
    '''
    

    Parameters
    ----------
    timeframe_str : str
        timeframe split by comma.

    Returns
    -------
    list
        List with start timeframe and end timeframe.

    '''
    
    timeframe = timeframe_str.split(',')
    timeframe = [datetime.strptime(x, '%Y-%m-%d') for x in timeframe]
    
    return timeframe


def get_transaction_gateway(order):
    
    data = get_order_data(order)
    
    # some have empty transactions
    if not data["transactions"]:
        return 0.0
    
    return data["transactions"][0]["gateway"]


def get_cash_collected(order):
    
    gateway = get_transaction_gateway(order)
    
    if gateway == "cash":
        return float(get_order_total_collected(order))
    
    return 0

def orders_to_df(orders_list):
    '''
    

    Parameters
    ----------
    orders_list : list
        Shopify orders list

    Returns
    -------
    df : DataFrame
        Dataframe version of orders
    '''
    
    data_list = []
    
    for index, order in enumerate(orders_list):
        data_list.append(get_order_data(order))
        
    return pd.DataFrame(data_list)


def add_event_variables(order_list, events) -> list:
    '''

    Parameters
    ----------
    orders_list : list
        Shopify orders list
        
    events : dict
        dictionary of dates: event name

    Returns
    -------
    orders_list : list
        Shopify orders list with added event variable and product collab variables

    '''
    
    mod_order_list = []
    
    for index, order in enumerate(order_list):

        pst = get_time_of_order(order)
        pst_str = pst.strftime('%Y-%m-%d')
   
        # I can use a hashmap method here because no transformation to keys are needed
        try:
            order["data"]["orders"]["nodes"][0]["event"] = events[pst_str]
        except KeyError:
            order["data"]["orders"]["nodes"][0]["event"] = "Non Event"
            
        mod_order_list.append(order)
        
    return mod_order_list
        
def add_collab_variables(order_list, collabs) -> list:
    '''
    TODO
    write docstring for collabs
    write access funcs for each variable
    
    Parameters
    ----------
    orders_list : list
        Shopify orders list
        
    events : dict
        dictionary of dates: event name

    Returns
    -------
    orders_list : list
        Shopify orders list with added event variable and product collab variables

    '''
    
    mod_order_list = []
    
    for index, order in enumerate(order_list):
        
        order["data"]["orders"]["nodes"][0]["collab"] = "No Collaboration"

        pst = get_time_of_order(order)
        
        # Will probably have to do this by product and date, not just date
        for index, collab in enumerate(collabs):
            timeframe = get_timeframe(collab["collab_timeframe"])

            # this needs a conditional that checks if varable exists and if it has another event name already (none or no collaboration ok)
            if timeframe[0].date() <= pst.date() <= timeframe[1].date() and order["data"]["orders"]["nodes"][0]["collab"] == "No Collaboration":
                order["data"]["orders"]["nodes"][0]["collab"] = collab["collab_name"]
                
            
        mod_order_list.append(order)
        
    return mod_order_list


def get_time_of_order(order):
    '''
    

    Parameters
    ----------
    order : dict
        Shopify order

    Returns
    -------
    date : dt
    datetime obj in pst

    '''
    
    # utc is 8hrs ahead of pst
    utc = datetime.strptime(get_order_data(order)["processedAt"], '%Y-%m-%dT%H:%M:%SZ')
    pst = utc - timedelta(hours=8, minutes=0)
    
    return pst