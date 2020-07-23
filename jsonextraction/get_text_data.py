from bs4 import BeautifulSoup
from json import load, dump
from re import search

"""
Main Method
"""

def extract_question_data(html):
    question = {}
    
    for element in elements_with_data_propname_attribute(html):
        properties = get_properties(element['data-propname'])

        value = get_response_value(element.string) \
            if properties[-1] == "response" \
            else element.string
        
        nest_dictionary(question, properties, value)

    return question

"""
BeautifulSoup and String Formatting Methods
"""

def elements_with_data_propname_attribute(html):
    return html.find_all(attrs={"data-propname": True})

def get_response_value(response_string):
    response_tag_match = search(r"<(\d+)>", response_string)
    return int(response_tag_match.group(1)) - 1 if response_tag_match else None    

def get_properties(propname):
    return [int(x) - 1 if x.isdigit() else x for x in propname.split(".")]

"""
JSON Nesting Methods
"""

def nest_dictionary(data, props, value):
    if len(props) == 1:
        set_value(data, props[0], value)
    else:
        if props[0] not in data:
            add_property(data, props)

        next_nest(data, props, value)

def nest_list(data, props, value):
    if len(props) == 1:
        set_value(data, props[0], value)
    else:
        if len(data) <= props[0]:
            add_property(data, props)

        next_nest(data, props, value) 

def next_nest(data, props, value):
    if type(data[props[0]]) == dict:
        nest_dictionary(data[props[0]], props[1:], value)
    elif type(data[props[0]]) == list:
        nest_list(data[props[0]], props[1:], value)
    else:
        previous_value = data[props[0]]
        data[props[0]] = {props[0]: previous_value}
        nest_dictionary(data[props[0]], props[1:], value)

def set_value(data, prop, value):
    if prop in data and type(data[prop]) == dict:
        data[prop][prop] = value
    else:
        data[prop] = value

def add_property(data, props):
    if type(props[0]) == int:
        fill_null_list(data, props[0] + 1)

    if type(props[1]) == int:
        data[props[0]] = []
    else:
        data[props[0]] = {}

def fill_null_list(li, length):
    for i in range(length):
        if i > len(li) - 1:
            li.append(None)