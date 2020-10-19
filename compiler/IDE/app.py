import os
import pygubu
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

from CSD import compiler
from Widgets import IndexedText
import file_manager
from CSD.LPDExceptions import lpd_exceptions

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "app.ui")


class App(pygubu.TkApplication):
    def _create_ui(self):
        self.file_manager = file_manager.FileManager()
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)

        self.mainwindow = builder.get_object('frame_main', self.master)

        self.mainmenu = menu = builder.get_object('menu_1', self.master)
        self.set_menu(menu)

        # self.text_ide = IndexedText.IndexedTextWrapper(builder.get_object('frame_ide', self.master))
        self.text_ide = builder.get_object('text_default')

        self.text_ide.bind_all('<<Modified>>', self.cb_on_text_update)

        builder.connect_callbacks(self)

        self.setup_shortcuts()

        self.set_title('CSD')

    def setup_shortcuts(self):
        self.master.bind('<Control-s>', lambda event: self.cb_menu_save())
        self.master.bind('<Control-o>', lambda event: self.cb_menu_open())
        self.master.bind('<Control-n>', lambda event: self.cb_menu_new())
        self.master.bind('<Control-r>', lambda event: self.cb_menu_compile())

    def run(self):
        self.mainwindow.mainloop()

    def update_title(self, filename, is_edited=False):
        self.set_title("CSD - {} {}".format(filename, '*' if is_edited else ''))

    def cb_menu_new(self):
        if self.file_manager.is_edited:
            # TODO Show a warning saying will lose current file
            pass

        self.file_manager.create_new_file()

        # Clear previous text
        self.text_ide.delete("1.0", tk.END)

        self.update_title('New', True)

    def cb_menu_open(self):
        if self.file_manager.is_edited:
            # TODO Show a warning saying will lose current file
            pass

        file_path = filedialog.askopenfilename()
        if (file_path == '' or file_path is None):
            return
        _file = self.file_manager.open_file_read(file_path)

        # Clear previous text
        self.text_ide.delete("1.0", tk.END)

        # Write new program
        self.text_ide.insert(tk.INSERT, _file.read())

        # Close file
        self.file_manager.close_file()

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)

    def cb_menu_save(self):
        if self.file_manager.is_file_named():
            self.file_manager.save_to_file(self.text_ide.get("1.0", tk.END))
        else:
            file_path = filedialog.askopenfilename()
            if (file_path == '' or file_path is None):
                return False
            self.file_manager.open_file_write(filename=file_path)
            self.file_manager.save_to_file(self.text_ide.get("1.0", tk.END))

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)

        return True

    def cb_menu_saveas(self):
        file_path = filedialog.askopenfilename()
        if (file_path == '' or file_path is None):
            return False
        self.file_manager.open_file_write(filename=file_path)
        self.file_manager.save_to_file(self.text_ide.get("1.0", tk.END))

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)

        return True

    def cb_menu_compile(self):
        # Save file
        if not self.cb_menu_save():
            return

        # Create compiler object
        _compiler = compiler.Compiler(self.file_manager.working_filename)

        # Execute
        try:
            _compiler.run()
        except Exception as e:
            # TODO write to errors window
            print(e)

    def cb_on_text_update(self, event):
        self.file_manager.edit_file()

        # Update window title
        self.update_title(self.file_manager.working_filename, is_edited=True)

        # Reset event
        # self.text_ide.bind_all('<<Modified>>', self.cb_on_text_update)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    app.run()
