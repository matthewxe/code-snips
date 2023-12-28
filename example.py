from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


print(
    HtmlFormatter(
        style='one-dark', linenos='table', wrapcode=True
    ).get_style_defs()
)
code = 'print "Hello World"'
print(highlight(code, PythonLexer(), HtmlFormatter(style='one-dark')))
