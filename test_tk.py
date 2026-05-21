import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
tv = tk.StringVar(value='My Type')
print(filedialog.SaveAs(root, typevariable=tv).options)
