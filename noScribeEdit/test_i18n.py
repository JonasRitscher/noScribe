import i18n

i18n.set('filename_format', '{namespace}.{locale}.{format}')
i18n.load_path.append('.')

with open('noScribe.en.yml', 'w') as f:
    f.write('en:\n  hello: "world"\n')

i18n.set('locale', 'en')
print("noScribe.hello:", i18n.t('noScribe.hello'))
