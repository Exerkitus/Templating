from jinja2 import Environment, FileSystemLoader
import json
from os.path import join
from datasource.stringify_datasource import validate_and_stringify

# Load sheet data from file
with open("Sheet.json", 'r') as file:
    sheet = json.load(file)

# Load schemas
with open("datasource/schema_validator/question_schemas.json", 'r') as file:
    schemas = json.load(file)

# Configure jinja environment
env = Environment(loader=FileSystemLoader("./templates"),
                         trim_blocks=True,
                         lstrip_blocks=True)

# Load custom validate_and_stringify filter
env.globals.update(validate_and_stringify=validate_and_stringify)

# Load master template from environment
master = env.get_template("master.html")

# Test render
renderedHTML = master.render(sheet=sheet, schemas=schemas)

# For debugging
print(renderedHTML)

# Save rendered HTML to File
with open(join("renders", "index.html"), 'w') as file:
    file.write(renderedHTML)
