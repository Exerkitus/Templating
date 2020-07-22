from bs4 import BeautifulSoup
from re import match
from json import dump

from get_text_data import extract_question_data

def get_json_from_xml(xml):
    questions_list = []

    for question in get_question_fields(xml):
        question_dict = get_html_properties(question)
        parts_list = []
        
        for part in get_part_fields(question):
            parts_list.append(get_part_properties(part))
        
        for part in question_dict["parts"]:
            if "response" in part:
                part["response"] = parts_list[part["response"]]
        
        questions_list.append(question_dict)

    return questions_list



def get_question_fields(xml):
    return xml.find_all("question", {"uid": True})

def get_html_properties(question):
    html = get_question_html(question)
    return extract_question_data(html)

def get_question_html(question):
    html_string = question.find("text").string
    return BeautifulSoup(html_string, 'html.parser')

def get_part_fields(question):
    return question.find_all("part")

def get_part_properties(part):
    part_dict = {}
    for prop in part.find_all():
        part_dict[prop.name] = get_xml_dictionary(prop)

    return part_dict

def get_xml_dictionary(prop):
    if prop.find_all():
        children = prop.find_all()
        if all_same_name(children):
            prop_list = []
            for child in children:
                prop_list.append(get_xml_dictionary(child))
            return prop_list
        else:
            prop_dict = {}
            for child in children:
                prop_dict[child.name] = get_xml_dictionary(child)
            return prop_dict
    elif prop.string:
        return get_prop_value(prop.string)

def all_same_name(li):
    return len(li) > 0 and all(x.name == li[0].name for x in li)

def get_prop_value(value):
    if match(r'^\s*\d+\s*$', value):
        return int(value)
    elif match(r'^\s*\d+\.\d+\s*$', value):
        return float(value)
    else:
        return value.strip()

"""
MAIN
"""

with open('./tests/sheet_64.xml', 'r') as xml_sheet_file:
    xml = BeautifulSoup(xml_sheet_file, 'lxml-xml')

with open('./tests/sheet_64.json', 'w') as json_sheet_file:
    dump(get_json_from_xml(xml), json_sheet_file, indent=4)

"""
for q in get_question_fields(xml):
    parts = get_part_fields(q)
    for p in parts:
        print(get_part_properties(p))
"""