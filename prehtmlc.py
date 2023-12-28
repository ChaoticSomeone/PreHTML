import re, os
import argparse

parser = argparse.ArgumentParser(
	prog="prehtmlc",
    description="A simple precompiler for HTML, that implements C-like comments and the ability to embed other html-files"
)



def get_indent(line:str) -> str:
	match = re.search(r"^\s", line)
	return "" if match is None else match.group()

class PreHtmlError(Exception):
	def __init__(self, msg=""):
		super().__init__(msg)

class PreHtml:

	@staticmethod
	def precompile_comments(lines:list) -> list:
		i = 0
		while i < len(lines):
			# translate from /* to <!-- and account for the fact that you can escape the /* sequence
			if re.search(r"\\/\*", lines[i]) is None and re.search(r"/\*", lines[i]):
				lines[i] = re.sub(r"/\*", "<!--", lines[i])

			# translate from */ to --> and account for the fact that you can escape the */ sequence
			if re.search(r"\\\*/", lines[i]) is None and re.search(r"\*/", lines[i]):
				lines[i] = re.sub(r"\*/", "-->", lines[i])

			# translate from // to <!-- ... -->
			# only works at the start of a line
			if re.search(r"^\\//", lines[i].lstrip()) is None and lines[i].lstrip()[:2] == "//":
				indent = get_indent(lines[i])
				lines[i] = f'{indent}<!-- {lines[i].lstrip()[2:].rstrip("\n")} -->\n'

			i += 1

		return lines


	@staticmethod
	def precompile_tags(f:str, lines:list) -> list:
		i = 0

		while i < len(lines):
			# add functionality for the prehtml-embed tag
			if (match := re.search(r"^<prehtml-embed\s*src.*/>", lines[i].lstrip())) is not None:
				src = re.search(r"src=\".*\"", match.group())
				if src is not None and re.search(r"\.html$", src.group()[5:-1]):
					src = src.group()[5:-1]
					indent = get_indent(lines[i])
					embedded_lines = PreHtml._embed_html(src)
					lines[i:i + 1] = [indent + line for line in embedded_lines]
					i += len(embedded_lines)
				else:
					raise PreHtmlError(f"Invalid path and/or file extension for tag <prehtml-embed/> in line {i + 1} of file '{f}'")
			elif re.search(r"^<prehtml-embed\s*/>", lines[i].lstrip()) is not None:
				raise PreHtmlError(f"Invalid usage of tag <prehtml-embed/>, missing required attribute 'src'")
			elif re.search(r"^<prehtml-embed\.*>", lines[i].lstrip()) is not None:
				raise PreHtmlError(f"Invalid usage of tag <prehtml-embed/>, tag does not have a closing tag. Use <prehtml-embed [...]/> instead <prehtml-embed [...]>")

			i += 1

		return lines

	@staticmethod
	def _embed_html(src: str) -> list:
		with open(src, 'rt') as f:
			embedded_lines = f.readlines()
		embedded_lines = PreHtml.precompile_tags(src, embedded_lines)
		return embedded_lines

	@staticmethod
	def run(f:str, lines:list) -> list:
		lines = PreHtml.precompile_comments(lines)
		lines = PreHtml.precompile_tags(f, lines)
		return lines


if __name__ == '__main__':
	# iterate through all files in the current directory
	for root, dirs, files in os.walk(os.getcwd()):
		for file in list(filter(lambda f: f[-5:] == ".html", files)):

			# get the file content
			path = os.path.join(root, file)
			with open(path, "rt") as html_file:
				content = html_file.readlines()

			# run the precompiler
			new_code = PreHtml.run(path, content)

			with open(path, "wt") as html_file:
				html_file.writelines(new_code)
