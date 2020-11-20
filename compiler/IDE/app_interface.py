from tkinter import *
import pygubu
import tkinter as tk
from tkinter import filedialog
from tkinter import font
import Caixa_texto
import file_manager
from CSD import compiler
from CSD.LPDExceptions import lpd_exceptions
import subprocess
import os.path

VM_APP_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "vm", "emulador.py")
print("Emulador: " + VM_APP_DIRECTORY)

class Tela():
    def create_ui(self):
        self.root = Tk()
        self.root.title('LPD Editor')
        self.root.iconbitmap()
        self.root.geometry("1200x650")

        self._subp = None

        self.file_manager = file_manager.FileManager()
        
        #Create frame

        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill="both", pady=5)
        self.frame_text = Caixa_texto.IndexedTextWrapper(self.main_frame)
        self.text = self.frame_text.text
        self.frame_text.pack(side="top", fill="both", expand=True)
        self.text.linha_erro = -1

        self.console_frame = Frame(self.root)
        self.console_frame.pack(fill="both", pady=5)

        self.text.bind_all("<<Change>>", self.cb_on_change)
        self.text.bind_all('<<Modified>>', self.cb_on_text_update)    
        self.text.tag_configure("erro", background="coral1")
        #Create scrollbar
        #text_scroll = Scrollbar(main_frame)
        #text_scroll.pack(side=RIGHT, fill=Y)

        #Add caixa de texto e set scrollbar
        #text_ide = Text(main_frame, width=92, height=25, undo = True, yscrollcommand=text_scroll.set)
        #text_ide.pack(fill="both")

        self.text_console = Text(self.console_frame, width=92, height=10, undo = True)
        self.text_console.pack(fill="both")

        self.text_console.config(state="disabled")
        #Config scrollbar
        #text_scroll.config(command=text_ide.yview)

        #Add Menu
        self.my_menu = Menu(self.root)
        self.root.config(menu=self.my_menu)

        #Add Menu Arquivo
        self.arquivo_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label="Arquivo", menu=self.arquivo_menu)
        self.arquivo_menu.add_command(label="Novo [Ctrl-N]", command=self.cb_menu_new)
        self.arquivo_menu.add_separator()
        self.arquivo_menu.add_command(label="Abrir [Ctrl-O]", command=self.cb_menu_open)
        self.arquivo_menu.add_separator()
        self.arquivo_menu.add_command(label="Salvar [Ctrl-S]", command=self.cb_menu_save)
        self.arquivo_menu.add_command(label="Salvar como", command=self.cb_menu_saveas)

        #Add Menu Compilador
        self.compilador_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label="Compilador", menu=self.compilador_menu)
        self.compilador_menu.add_command(label="Compilar", command=self.cb_menu_compile)

        #Add index_bar - Linha/Coluna
        self.index_bar = Label(self.root, text='Ln ' + str(0) + ' | Col ' + str(0), anchor=E)
        self.index_bar.pack(fill=X, side=BOTTOM, ipady=5)

        self.setup_shortcuts()
        self.root.mainloop()

    def check_pos(self, event):
        self.local = self.text.index(tk.INSERT)
        #self.line = local[0]
        #self.col = local[1]

    def setup_shortcuts(self):
        self.root.bind('<Control-s>', lambda event: self.cb_menu_save())
        self.root.bind('<Control-o>', lambda event: self.cb_menu_open())
        self.root.bind('<Control-n>', lambda event: self.cb_menu_new())
        self.root.bind('<Control-r>', lambda event: self.cb_menu_compile())
        self.root.bind('<Control-c>', lambda event: "<<Copy>>")
        self.root.bind('<Control-v>', lambda event: "<<Paste>>")

    def cb_on_change(self, event):
        if self.text.linha_erro != -1:
            self.text.tag_remove('erro','1.0', 'end')
            self.text.linha_erro = -1

    def cb_menu_compile(self):
        # Save file
        if not self.cb_menu_save():
            return

        # Clear error log
        self.console_clear()

        # Remove VM screen
        if self._subp is not None:
            self._subp.kill()
            self._subp = None

        # Create compiler object
        _compiler = compiler.Compiler(self.file_manager.working_filename, debug=True)

        # Execute
        _objfile = None
        try:
            if self.text.linha_erro != -1:
                self.text.tag_remove('erro', '1.0', 'end')
                self.text.linha_erro = -1
            _objfile = _compiler.run()
            self.console_log("Sucesso!")
        except lpd_exceptions.LPDException as e:
            # TODO write to errors window
            self.console_log(str(e))
            self.text.tag_add('erro', str(e.line+1) + '.0', str(e.line + 2) + '.0')
            self.text.linha_erro = e.line
            #Text(text_ide, backgrount=('red').grid(line=e.line))
            #print(e)

        if _objfile is not None:
            if self._subp is not None:
                self._subp.kill()
            self._subp = subprocess.Popen(["py", VM_APP_DIRECTORY, _objfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Opened subprocess: " + str(self._subp))
            #print(_p.communicate())

    def cb_menu_new(self):
        if self.file_manager.is_edited:
            # TODO Show a warning saying will lose current file
            pass

        self.file_manager.create_new_file()

        # Clear previous text
        self.text.delete("1.0", tk.END)

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
        self.text.delete("1.0", tk.END)

        # Write new program
        self.text.insert(tk.INSERT, _file.read())

        # Close file
        self.file_manager.close_file()

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)

    def cb_menu_save(self):
        if self.file_manager.is_file_named():
            self.file_manager.save_to_file(self.text.get("1.0", tk.END))
        else:
            file_path = filedialog.askopenfilename()
            if (file_path == '' or file_path is None):
                return False
            self.file_manager.open_file_write(filename=file_path)
            self.file_manager.save_to_file(self.text.get("1.0", tk.END))

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)
        if self.text.linha_erro != -1:
            self.text.tag_remove('erro','1.0', 'end')
            self.text.linha_erro = -1

        return True

    def cb_menu_saveas(self):
        file_path = filedialog.askopenfilename()
        if (file_path == '' or file_path is None):
            return False
        self.file_manager.open_file_write(filename=file_path)
        self.file_manager.save_to_file(self.text.get("1.0", tk.END))

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)

        if self.text.linha_erro != -1:
            self.text.tag_remove('erro','1.0', 'end')
            self.text.linha_erro = -1
            
        return True

    def update_title(self, filename, is_edited=False):
        self.root.title("CSD - {} {}".format(filename, '*' if is_edited else ''))

    def cb_on_text_update(self, event):
        self.file_manager.edit_file()

        # Update window title
        self.update_title(self.file_manager.working_filename, is_edited=True)

        # Reset event
        # self.text_ide.bind_all('<<Modified>>', self.cb_on_text_update)

    def do_console(self, action):
        self.text_console.config(state="normal")
        action()
        self.text_console.config(state="disabled")

    def console_clear(self):
        self.do_console(lambda: self.text_console.delete("1.0", tk.END))

    def console_log(self, text, end='\n'):
        self.do_console(lambda: self.text_console.insert("end", str(text) + end))
        

if __name__ == '__main__':
    app = Tela()
    app.create_ui()