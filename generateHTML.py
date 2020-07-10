from jinja2 import Environment, FileSystemLoader
import json
from os.path import join

# Load sheet data from file
with open("Sheet.json", 'r') as file:
    sheet = json.load(file)

# Configure jinja environment
env = Environment(
    loader=FileSystemLoader("./templates")
)

# Load master template from environment
master = env.get_template("master.html")

# Test render
renderedHTML = master.render(sheet)

# For debugging
print(renderedHTML)

# Save rendered HTML to File
with open(join("renders", "index.html"), 'w') as file:
    file.write(renderedHTML)
