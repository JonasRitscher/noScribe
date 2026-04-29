import re

with open('noScribeEdit.py', 'r', encoding='utf-8') as f:
    content = f.read()

helper = """
    # AI-Generated Feature: Custom Dialog Translations
    def custom_msg_box(self, icon, title, text, buttons, default_button):
        msg = QtWidgets.QMessageBox(icon, title, text, buttons, self)
        if buttons & QtWidgets.QMessageBox.StandardButton.Save:
            msg.setButtonText(QtWidgets.QMessageBox.StandardButton.Save, t('editor.action.save', default='Save'))
        if buttons & QtWidgets.QMessageBox.StandardButton.Discard:
            msg.setButtonText(QtWidgets.QMessageBox.StandardButton.Discard, t('editor.action.discard', default='Discard'))
        if buttons & QtWidgets.QMessageBox.StandardButton.Cancel:
            msg.setButtonText(QtWidgets.QMessageBox.StandardButton.Cancel, t('editor.action.cancel', default='Cancel'))
        if buttons & QtWidgets.QMessageBox.StandardButton.Ok:
            msg.setButtonText(QtWidgets.QMessageBox.StandardButton.Ok, t('editor.action.ok', default='OK'))
        if buttons & QtWidgets.QMessageBox.StandardButton.Yes:
            msg.setButtonText(QtWidgets.QMessageBox.StandardButton.Yes, t('editor.action.yes', default='Yes'))
        if buttons & QtWidgets.QMessageBox.StandardButton.No:
            msg.setButtonText(QtWidgets.QMessageBox.StandardButton.No, t('editor.action.no', default='No'))
        msg.setDefaultButton(default_button)
        return msg.exec()
"""

# Insert the helper before update_title
content = content.replace("    def update_title(self):", helper + "\n    def update_title(self):")

# Replace existing QMessageBox.warning calls
content = re.sub(r'QtWidgets\.QMessageBox\.warning\(\s*self,\s*"noScribeEdit",\s*(t\([^)]+\)),\s*(QtWidgets\.QMessageBox\.StandardButton\.[^\n]+)\s*\|\s*(QtWidgets\.QMessageBox\.StandardButton\.[^\n,]+)(?:\s*\|\s*QtWidgets\.QMessageBox\.StandardButton\.[^,]+)?,\s*(QtWidgets\.QMessageBox\.StandardButton\.[^\)]+)\)',
                 r'self.custom_msg_box(QtWidgets.QMessageBox.Icon.Warning, "noScribeEdit", \1, \2 | \3' + \
                 r', \4)', content)

# The regex above is tricky because it might not match multiline perfectly if not careful.
# Let's just do simple replacements for the exact strings.

content = content.replace('QtWidgets.QMessageBox.warning(self, "noScribeEdit", \n                                                t(\'editor.msg.audio_not_found\'),\n                                                QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel, \n                                                QtWidgets.QMessageBox.StandardButton.Ok)',
                          'self.custom_msg_box(QtWidgets.QMessageBox.Icon.Warning, "noScribeEdit", t(\'editor.msg.audio_not_found\'), QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel, QtWidgets.QMessageBox.StandardButton.Ok)')

content = content.replace('QtWidgets.QMessageBox.warning(self, "noScribeEdit", \n                                                t(\'editor.msg.modified\'),\n                                                QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard\n                                                | QtWidgets.QMessageBox.StandardButton.Cancel, QtWidgets.QMessageBox.StandardButton.Save)',
                          'self.custom_msg_box(QtWidgets.QMessageBox.Icon.Warning, "noScribeEdit", t(\'editor.msg.modified\'), QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel, QtWidgets.QMessageBox.StandardButton.Save)')

content = content.replace('QtWidgets.QMessageBox.warning(self, "noScribeEdit", \n                                            t(\'editor.msg.audio_not_found\'),\n                                            QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel, \n                                            QtWidgets.QMessageBox.StandardButton.Ok)',
                          'self.custom_msg_box(QtWidgets.QMessageBox.Icon.Warning, "noScribeEdit", t(\'editor.msg.audio_not_found\'), QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel, QtWidgets.QMessageBox.StandardButton.Ok)')

content = content.replace('QtWidgets.QMessageBox.warning(self, "noScribeEdit", \n                                    t(\'editor.msg.audio_not_found\'),\n                                    QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel, \n                                    QtWidgets.QMessageBox.StandardButton.Ok)',
                          'self.custom_msg_box(QtWidgets.QMessageBox.Icon.Warning, "noScribeEdit", t(\'editor.msg.audio_not_found\'), QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel, QtWidgets.QMessageBox.StandardButton.Ok)')

content = content.replace('QtWidgets.QMessageBox.question(\n                    self, "noScribeEdit", t(\'editor.msg.save_as_play_along_warning\'),\n                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No\n                )',
                          'self.custom_msg_box(QtWidgets.QMessageBox.Icon.Question, "noScribeEdit", t(\'editor.msg.save_as_play_along_warning\', default=\'Changing the file name will break the connection to the audio source.\\nDo you want to continue?\\nIf so, the audio file will no longer be played back.\\nUse \\"Save\\" instead if you want to keep the connection to the audio.\\n\\n\\nAlternatively you can also change the audio file over the menu:\nFile -> Audio source...\\n\\n\'), QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No)')

with open('noScribeEdit.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dialog replacement complete.")
