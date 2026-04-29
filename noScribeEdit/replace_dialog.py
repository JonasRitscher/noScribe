with open('search_and_replace_dialog.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = "from i18n import t\n" + content

replacements = {
    '"Find and Replace"': "t('editor.dialog.find_replace_title')",
    '"Find:"': "t('editor.dialog.find_label')",
    '"Replace with:"': "t('editor.dialog.replace_label')",
    '"Case Sensitive"': "t('editor.dialog.case_sensitive')",
    '"Whole Words Only"': "t('editor.dialog.whole_word')",
    '"Find Next"': "t('editor.dialog.find_next')",
    '"Replace"': "t('editor.dialog.replace')",
    '"Replace All"': "t('editor.dialog.replace_all')",
    '"Close"': "t('editor.dialog.close')"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('search_and_replace_dialog.py', 'w', encoding='utf-8') as f:
    f.write(content)
