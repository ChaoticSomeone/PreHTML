import re, os

def precompile(file:str):
    content = []
    with open(file, "rt") as f:
        content = f.readlines()

    i = 0
    while i < len(content):
        content[i] = re.sub(r"/\*", "<!--", content[i])
        content[i] = re.sub(r"\*/", "-->", content[i])
        
        if content[i].lstrip()[:2] == "//":
            match = re.search(r"^\s", content[i])
            indent = "" if match is None else match.group()
            content[i] = f'{indent}<!-- {content[i].lstrip()[2:].rstrip("\n")} -->\n'
            
        i += 1

    with open(file, "wt") as f:
        f.writelines(content)

for root, dirs, files in os.walk("."):
    for file in list(filter(lambda f: ".html" in f[-5:], files)):
        path = os.path.join(root, file)
        precompile(path)