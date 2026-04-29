import re

with open('noScribeEdit.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert i18n setup after get_config
setup_code = """
import i18n
from i18n import t

i18n.set('filename_format', '{namespace}.{locale}.{format}')
i18n.load_path.append(os.path.join(app_dir, 'trans'))

# Try to get locale from main noScribe config
app_locale = 'auto'
try:
    with open(os.path.join(config_dir, 'config.yml'), 'r') as main_file:
        main_config = yaml.safe_load(main_file)
        if main_config and 'locale' in main_config:
            app_locale = main_config['locale']
except:
    pass

if app_locale == 'auto':
    try:
        import locale
        app_locale = locale.getdefaultlocale()[0][0:2]
    except:
        app_locale = 'en'

i18n.set('fallback', 'en')
i18n.set('locale', app_locale)
"""

content = content.replace("def get_config(key: str, default):\n    \"\"\" Get a config value, set it if it doesn't exist \"\"\"\n    if key not in config:\n        config[key] = default\n    return config[key]", 
                          "def get_config(key: str, default):\n    \"\"\" Get a config value, set it if it doesn't exist \"\"\"\n    if key not in config:\n        config[key] = default\n    return config[key]\n\n" + setup_code)

# Replace strings
replacements = {
    '"&File"': "t('editor.menu.file')",
    '"Open file..."': "t('editor.menu.open_file')",
    '"Open file"': "t('editor.tooltip.open_file')",
    '"Recent Files"': "t('editor.menu.recent_files')",
    '"Save"': "t('editor.menu.save')",
    '"Save current file"': "t('editor.tooltip.save')",
    '"Save As..."': "t('editor.menu.save_as')",
    '"Save current file to specified file"': "t('editor.tooltip.save_as')",
    '"Audio source..."': "t('editor.menu.audio_source')",
    '"Locate the audio source file of the current transcript"': "t('editor.tooltip.audio_source')",
    '"noScribe"': "t('editor.menu.noScribe')",
    '"Play/Pause Audio"': "t('editor.action.play_pause')",
    '"Listen to the audio source of the current text"': "t('editor.tooltip.play_pause')",
    '"Playback speed"': "t('editor.tooltip.playback_speed')",
    '"Set playback speed"': "t('editor.tooltip.playback_speed')", # Same text
    '"Edit"': "t('editor.menu.edit')", # Wait, toolbars might be named "Edit"
    '"&Edit"': "t('editor.menu.edit')",
    '"Undo"': "t('editor.action.undo')",
    '"Undo last change"': "t('editor.tooltip.undo')",
    '"Redo"': "t('editor.action.redo')",
    '"Redo last change"': "t('editor.tooltip.redo')",
    '"Cut"': "t('editor.action.cut')",
    '"Cut selected text"': "t('editor.tooltip.cut')",
    '"Copy"': "t('editor.action.copy')",
    '"Copy selected text"': "t('editor.tooltip.copy')",
    '"Paste"': "t('editor.action.paste')",
    '"Paste from clipboard"': "t('editor.tooltip.paste')",
    '"Select all"': "t('editor.action.select_all')",
    '"Select all text"': "t('editor.tooltip.select_all')",
    '"Find and Replace"': "t('editor.action.find_replace')",
    '"Find (and replace) text"': "t('editor.tooltip.find_replace')",
    '"Zoom in"': "t('editor.action.zoom_in')",
    '"Zoom out"': "t('editor.action.zoom_out')",
    '"Increase Line Spacing"': "t('editor.action.line_spacing_increase')",
    '"Decrease Line Spacing"': "t('editor.action.line_spacing_decrease')",
    '"Format"': "t('editor.menu.format')",
    '"&Format"': "t('editor.menu.format')",
    '"Bold"': "t('editor.action.bold')",
    '"Italic"': "t('editor.action.italic')",
    '"Underline"': "t('editor.action.underline')",
    '"Align left"': "t('editor.action.align_left')",
    '"Align text left"': "t('editor.tooltip.align_left')",
    '"Align center"': "t('editor.action.align_center')",
    '"Align text center"': "t('editor.tooltip.align_center')",
    '"Align right"': "t('editor.action.align_right')",
    '"Align text right"': "t('editor.tooltip.align_right')",
    '"Justify"': "t('editor.action.justify')",
    '"Justify text"': "t('editor.tooltip.justify')"
}

# we have to be careful not to replace toolbars' names if they are used as identifiers,
# but in pyqt6 QToolBar("Name") is just the title. 
for old, new in replacements.items():
    content = content.replace(old, new)

# specific replacements for strings not matched correctly above
content = content.replace('"The document has been modified.\\n"\n                                                "Do you want to save your changes?"', "t('editor.msg.modified')")
content = content.replace('"Audio source file not found.\\n"\n                                                     "Do you want to search for it?"', "t('editor.msg.audio_not_found')")
content = content.replace('"Loading... please wait."', "t('editor.msg.loading')")
content = content.replace('"Copy saved as: "', "t('editor.msg.saved_as')")

with open('noScribeEdit.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete.")
