import tifffile
import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from tkinter import messagebox, Scrollbar, Canvas
from tkinter.filedialog import askdirectory, askopenfilename
import re
import os
import imagej
import scyjava


class imageJProcessor:
    """Initialise the ImageJ window and gets user ImageJ location and ImageJ macro."""
    def __init__(self):
        
        self.root = tk.Tk()

        #self.root.geometry("800x150")
        self.root.title("ImageJ Selection Window")

         # Choose directories
        self.directoryframe = tk.Frame(self.root)
        self.directoryframe.columnconfigure(0, weight=1)
        self.directoryframe.columnconfigure(1, weight=1)
        self.directoryframe.columnconfigure(2, weight=1)

        self.src_label = ttk.Label(self.directoryframe, text="Fiji.app directory", font=("Segoe UI", 14))
        self.src_label.grid(row=0, column=0, padx=10, pady=10)

        self.src_entry_text = tk.StringVar()
        self.src_selected = ttk.Entry(self.directoryframe, text=self.src_entry_text, width=70, state='readonly')
        self.src_selected.grid(row=0, column=1, padx=10, pady=10)

        self.src_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("src_button"))
        self.src_button.grid(row=0, column=2, padx=10, pady=10)

        self.interactive_state = tk.IntVar()
        self.interactive_check = ttk.Checkbutton(self.directoryframe, text="Run ImageJ in interactive mode", variable=self.interactive_state)
        self.interactive_check.grid(row=1, column=1, padx=10, pady=5)

        self.macro_label = ttk.Label(self.directoryframe, text="ImageJ macro", font=("Segoe UI", 14))
        self.macro_label.grid(row=2, column=0, padx=10, pady=10)

        self.macro_entry_text = tk.StringVar()
        self.macro_selected = ttk.Entry(self.directoryframe, text=self.macro_entry_text, width=70, state='readonly')
        self.macro_selected.grid(row=2, column=1, padx=10, pady=10)

        self.macro_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("macro_button"))
        self.macro_button.grid(row=2, column=2, padx=10, pady=10)

        self.arg_label = ttk.Label(self.directoryframe, text="ImageJ Arguments", font=("Segoe UI", 14))
        self.arg_label.grid(row=3, column=0, padx=10, pady=10)

        self.arg_entry_text = tk.StringVar()
        self.arg_selected = ttk.Entry(self.directoryframe, text=self.arg_entry_text, width=70, state='readonly')
        self.arg_selected.grid(row=3, column=1, padx=10, pady=10)

        self.arg_button = ttk.Button(self.directoryframe, text="...", command=lambda: self.get_directory("arg_button"))
        self.arg_button.grid(row=3, column=2, padx=10, pady=10)

        self.directoryframe.pack()

        # Confirm button
        self.buttonframe = tk.Frame(self.root)
        self.buttonframe.columnconfigure(0, weight=1)

        self.confirm_button = ttk.Button(self.buttonframe, text="OK", command=self.src_confirm)
        self.confirm_button.grid(row=0, column=0, padx=58, pady=10, sticky=tk.E)
        
        self.buttonframe.pack(fill='x')

        self.root.mainloop()

    def get_directory(self, button):
        """Asks users to choose the source and saving directories."""
        if button == "src_button":
            src_dir = askdirectory(title="Choose location for Fiji.app on computer")
            self.src_entry_text.set(src_dir)
        if button == "macro_button":
            macro_file = askopenfilename(title="Choose file for ImageJ macro")
            self.macro_entry_text.set(macro_file)
        if button == "arg_button":
            arg_file = askopenfilename(title="Choose file for ImageJ arguments")
            self.arg_entry_text.set(arg_file)

    def src_confirm(self):
        """Checks the choices have been made for directories and processing steps. """
        if self.src_entry_text.get() == "":
            messagebox.showinfo(title="Missing Information", message="Please choose the Fiji.app directory")
        elif self.macro_entry_text.get() == "" or not self.macro_entry_text.get().endswith(".txt"):
            messagebox.showinfo(title="Missing Information", message="Please choose a .txt ImageJ macro file")
        elif self.arg_entry_text.get() != "" and not self.arg_entry_text.get().endswith(".txt"):
            messagebox.showinfo(title="Missing Information", message="Please choose a .txt ImageJ arguments file")
        else:
            self.src_dir = self.src_entry_text.get()
            self.plugin_dir = os.path.join(self.src_dir, "plugins")
            self.macro_file = self.macro_entry_text.get()
            self.arg_file = self.arg_entry_text.get()
            self.imageJ_options = {"interactive": self.interactive_state.get()} # Add more options here when needed

            self.root.destroy()

    def get_all_paths(self):
        return self.src_dir, self.plugin_dir, self.imageJ_options, self.macro_file, self.arg_file
    
    def initialise_imageJ(self):
        plugins_dir = self.plugin_dir
        scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')

        if self.imageJ_options["interactive"]:
            ij = imagej.init(self.src_dir, mode="interactive")
            ij.ui().showUI()
        else:
            ij = imagej.init(self.src_dir)
        return ij
    
    def read_macro(self):
        with open(self.macro_file, "r") as file:
            macro = file.read()
        return macro

    def read_arg(self):
        arg = {}
        with open(self.arg_file, "r") as file:
            arg_f = file.read().replace("\n", "")
        
        arguments = arg_f.split(",")
        for argument in arguments:
            pair = argument.split(":")
            try:
                arg[pair[0]] = int(pair[1])
            except:
                arg[pair[0]] = pair[1]
        return arg
     
    def run(self):
        
        ij = self.initialise_imageJ()

        macro = self.read_macro()
        arg = self.read_arg()

        ij.py.run_macro(macro, arg)

def main():
    processor = imageJProcessor()
    fiji_loc, plugins_loc, imageJ_options, macro_path, arg_path = processor.get_all_paths()

    #print(fiji_loc, plugins_loc, imageJ_options, macro_path, arg_path)

    processor.run()

main()

if __name__ == "main":
    processor = imageJProcessor()