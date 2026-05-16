import mistune
from mistune.plugins.formatting import strikethrough
from mistune.plugins.footnotes import footnotes
from mistune.plugins.table import table
from mistune.plugins.url import url
from mistune.plugins.task_lists import task_lists
from mistune.plugins.formatting import mark
from mistune.plugins.formatting import superscript
from mistune.plugins.formatting import subscript
from mistune.plugins.math import math
from mistune.directives import RSTDirective, TableOfContents


with open("example.md", "r", encoding="utf-8") as fp:
	mkdown_txt = ".. toc::\n" + fp.read()

renderer = mistune.HTMLRenderer()
markdown = mistune.create_markdown(renderer, \
		plugins=[strikethrough, \
				footnotes, \
				table, \
				url, \
				task_lists,\
				mark, \
				superscript, \
				subscript, \
				math, \
				RSTDirective([TableOfContents()])]
				)

html_txt = markdown(mkdown_txt)
with open("example.html", "w", encoding="utf-8") as fp:
	fp.write(html_txt)
