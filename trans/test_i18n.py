import i18n
import os

i18n.set('filename_format', '{locale}.{format}')
i18n.load_path.append('.')

with open('noScribe.en.yml', 'w') as f:
    f.write('en:\n  hello: "world"\n')
with open('en.yml', 'w') as f:
    f.write('en:\n  hello2: "world2"\n')

i18n.set('locale', 'en')
print("hello:", i18n.t('hello'))
print("hello2:", i18n.t('hello2'))
