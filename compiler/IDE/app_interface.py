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
#print("Emulador: " + VM_APP_DIRECTORY)

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

        self.text.bind("<KeyRelease>", self.keyRelease)
        self.text.bind("<Button-1>", self.keyRelease)
        self.text.bind_all('<<Modified>>', self.cb_on_text_update)   
        self.text.tag_configure("erro", background="coral1")

        self.text_console = Text(self.console_frame, width=92, height=10, undo = True)
        self.text_console.pack(fill="both")

        self.text_console.config(state="disabled")

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

        #Add Menu Opções
        self.opcoes_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label="Opções", menu=self.opcoes_menu)
        self.var_ex_unreachable_code = tk.BooleanVar()
        self.var_ex_unreachable_code.set(True)
        self.opcoes_menu.add_checkbutton(label="Lançar exceção código inalcançável", variable=self.var_ex_unreachable_code)
        self.var_ex_nondeterministic_function = tk.BooleanVar()
        self.var_ex_nondeterministic_function.set(True)
        self.opcoes_menu.add_checkbutton(label="Lançar exceção função não-determinística", variable=self.var_ex_nondeterministic_function)
        self.var_accept_accents = tk.BooleanVar()
        self.opcoes_menu.add_checkbutton(label="Aceitar acentuação", variable=self.var_accept_accents)

        #Add index_bar - Linha/Coluna
        self.index_variable = StringVar()
        self.index_bar = Label(self.root,  textvariable=self.index_variable, anchor=E)
        self.index_bar.pack(fill=X, side=BOTTOM, ipady=5)
        self.keyRelease(None)

        self.setup_shortcuts()
        self.root.mainloop()

    def keyRelease(self, event):
        position = self.text.index(tk.CURRENT).split(".")
        self.index_variable.set('Ln ' + position[0] + ' | Col ' + str(int(position[1]) + 1))
        #print(self.text.index(tk.CURRENT))
        

    def setup_shortcuts(self):
        self.root.bind('<Control-s>', lambda event: self.cb_menu_save())
        self.root.bind('<Control-o>', lambda event: self.cb_menu_open())
        self.root.bind('<Control-n>', lambda event: self.cb_menu_new())
        self.root.bind('<Control-r>', lambda event: self.cb_menu_compile())
        self.root.bind('<Control-c>', lambda event: "<<Copy>>")
        self.root.bind('<Control-v>', lambda event: "<<Paste>>")

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

        # Get ignored exceptions
        _rules = []
        if not self.var_ex_unreachable_code.get():
            _rules.append("UnreachableCodeException")
        if not self.var_ex_nondeterministic_function.get():
            _rules.append("NonDeterministicFunctionException")
        if self.var_accept_accents.get():
            _rules.append("AcceptAccents")

        # Create compiler object
        _compiler = compiler.Compiler(self.file_manager.working_filename, debug=False, rules=_rules)

        # Execute
        _objfile = None
        try:
            if self.text.linha_erro != -1:
                self.text.linha_erro = -1
            _objfile = _compiler.run()
            self.console_log("Sucesso!")
        except lpd_exceptions.LPDException as e:
            # TODO write to errors window
            self.console_log(str(e))
            self.text.tag_add('erro', str(e.line+1) + '.0', str(e.line + 2) + '.0')
            self.text.linha_erro = e.line
            self.text.see(str(e.line) + '.0')
            self.frame_text.linenumbers.redraw()
        except Exception as e:
            self.console_log("Erro inesperado:" + str(e))

        if _objfile is not None:
            if self._subp is not None:
                self._subp.kill()
            self._subp = subprocess.Popen(["py", VM_APP_DIRECTORY, _objfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def cb_menu_new(self):
        if self.file_manager.is_edited:
            # TODO Show a warning saying will lose current file
            pass

        self.file_manager.create_new_file()

        # Clear previous text
        self.text.delete("1.0", tk.END)

        self.update_title('New', True)

        self.keyRelease(None)

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
        self.text.insert(tk.INSERT, _file.read().rstrip())

        # Close file
        self.file_manager.close_file()

        # Update window title
        self.update_title(self.file_manager.working_filename, self.file_manager.is_edited)

        self.keyRelease(None)

    def cb_menu_save(self):
        if self.file_manager.is_file_named():
            self.file_manager.save_to_file(self.text.get("1.0", tk.END))
        else:
            file_path = filedialog.asksaveasfilename()
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
        file_path = filedialog.asksaveasfilename()
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