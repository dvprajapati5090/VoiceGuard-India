import re

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix JS colors to use CSS variables from the theme
html = html.replace("#EF4444", "var(--brand-orange)")
html = html.replace("#10B981", "var(--brand-green)")
html = html.replace("#3B82F6", "var(--blue)")
html = html.replace("#6366F1", "var(--blue)")
html = html.replace("#A855F7", "var(--blue)")

with open('c:/Users/jeend/OneDrive/Desktop/AGENTIS/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
