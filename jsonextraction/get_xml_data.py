from bs4 import BeautifulSoup
from re import match
from json import dump

from get_html_data import get_question_data

"""
Main Method
"""

def get_sheet_from_xml(xml):
    return [get_question_from_xml(q) for q in get_questions(xml)]

def get_question_from_xml(question_xml):
    question = get_question_html_properties(question_xml)
    parts = get_list_of_part_properties(question_xml)
    
    add_parts_to_question(question, parts)
    
    return question

def get_question_html_properties(question_xml):
    html = get_question_html(question_xml)
    return get_question_data(html)

def get_list_of_part_properties(question_xml):
    return [get_part_properties(p) for p in get_parts(question_xml)]

def add_parts_to_question(question, parts):
    for p in question["parts"]:
        if "response" in p:
            p["response"] = parts[p["response"]]

"""
BeautifulSoup Methods
"""

def get_questions(xml):
    return xml.find_all("question", {"uid": True})

def get_question_html(question_xml):
    html_string = question_xml.find("text").string
    return BeautifulSoup(html_string, 'html.parser')

def get_parts(question_xml):
    return question_xml.find_all("part")

def get_part_properties(part_xml):
    # finds all children in parts, which are its properties
    return {prop_xml.name:get_prop_value(prop_xml) for prop_xml in part_xml.find_all()}

"""
JSON Nesting Methods
"""

def get_prop_value(prop_xml):
    if prop_xml.find_all():
        return add_deeper_nest(prop_xml)
    elif prop_xml.string:
        return format_prop_string(prop_xml.string)

def add_deeper_nest(prop_xml):
    children = prop_xml.find_all()
    if all_same_name(children):
        return add_nested_list(prop_xml)
    else:
        return add_nested_dictionary(prop_xml)

def all_same_name(li):
    return len(li) > 0 and all(x.name == li[0].name for x in li)

def add_nested_list(prop_xml):
    return [get_prop_value(child) for child in prop_xml]

def add_nested_dictionary(prop_xml):
    return {child.name:get_prop_value(child) for child in prop_xml}

def format_prop_string(value):
    if match(r'^\s*\d+\s*$', value): # check if int
        return int(value)
    elif match(r'^\s*\d+\.\d+\s*$', value): # check if float
        return float(value)
    else:
        return value.strip() # remove whitespace at ends of string from CDATA

"""
MAIN
"""

with open('./tests/sheet_64.xml', 'r') as xml_sheet_file:
    xml = BeautifulSoup(xml_sheet_file, 'lxml-xml')

with open('./tests/sheet_64.json', 'w') as json_sheet_file:
    dump(get_sheet_from_xml(xml), json_sheet_file, indent=4)
