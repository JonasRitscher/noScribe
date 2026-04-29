import sys
from PyQt6 import QtGui
try:
    print("LineHeightTypes:", hasattr(QtGui.QTextBlockFormat, "LineHeightTypes"))
    print("LineHeightType:", hasattr(QtGui.QTextBlockFormat, "LineHeightType"))
    print("ProportionalHeight in LineHeightTypes:", hasattr(QtGui.QTextBlockFormat.LineHeightTypes, "ProportionalHeight"))
    print("ProportionalHeight in QtGui.QTextBlockFormat:", hasattr(QtGui.QTextBlockFormat, "ProportionalHeight"))
except Exception as e:
    print("Error:", e)
