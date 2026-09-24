import re

with open('informe.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any `something_with_underscores` with \texttt{something\_with\_underscores}
def repl_code(match):
    inner = match.group(1)
    inner_escaped = inner.replace('_', '\\_')
    return f'\\texttt{{{inner_escaped}}}'

content_fixed = re.sub(r'`([^`\n]+)`', repl_code, content)

# Check for any remaining unescaped _ in normal text lines (excluding equations and commands)
# In equations ($...$, \[...\], \begin{equation}...\end{equation}), _ is subscript and valid.

with open('informe.tex', 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("informe.tex updated with escaped backticks.")
