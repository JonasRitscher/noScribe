import sys
from PyQt6 import QtWidgets, QtCore

app = QtWidgets.QApplication(sys.argv)

app_locale = 'de'
translator = QtCore.QTranslator()
translations_path = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
# Note: For PyQt6, it might be qtbase_de.qm instead of qt_de.qm
loaded = translator.load("qtbase_de", translations_path)
if not loaded:
    loaded = translator.load("qt_de", translations_path)

print("Translator loaded:", loaded)
if loaded:
    app.installTranslator(translator)

msg = QtWidgets.QMessageBox()
msg.setText("Dies ist ein Test.")
msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel)

# Just check what the button text is conceptually, though QMessageBox doesn't expose it directly before show.
