import os
import pygubu
import VM
import TKHelper
from tkinter import filedialog
from tkinter import *

vm_emu = VM.VM()

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "emulador.ui")

def importProgramFile(file_path):
    fd = open(file_path, "r")
    return [line.rstrip() for line in fd.readlines()]

def parseLine(tokens):
    aux = [None] + tokens if vm_emu.isValidCmd(tokens[0]) else tokens + [None] 
    return aux + [None] * (3 - len(aux))

def writeProgramField(programWidget, program):
    scrollFrame = TKHelper.ScrollFrame(programWidget)
    tableRelief = "solid"
    global programTableView 
    programTableView = scrollFrame.viewPort

    for idx, key in enumerate(["Breakpoint", "Linha", "Label", "Comando", "Parâmetros"]):
        Label(scrollFrame.viewPort, text=key, font=('bold'), relief=tableRelief).grid(row=0, column=idx, sticky="snew")
        scrollFrame.viewPort.columnconfigure(idx, minsize=len(key))

    for _lineNo, pLine in enumerate(program):
        Checkbutton(scrollFrame.viewPort, relief=tableRelief).grid(row=_lineNo+1, column=0, sticky="snew")
        Label(scrollFrame.viewPort, text=str(_lineNo + 1), relief=tableRelief).grid(row=_lineNo+1, column=1, sticky="snew")

        for idx, token in enumerate(parseLine(pLine.split(" "))):
            Label(scrollFrame.viewPort, text=token, relief=tableRelief).grid(row=_lineNo+1, column=2+idx, sticky="snew")

    scrollFrame.pack(side="top", fill="both", expand=True)

class VmApp:
    def __init__(self):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('toplevel')
        builder.connect_callbacks(self)
        self.console = builder.get_object("console_output")

    def run(self):
        self.mainwindow.mainloop()

    def cb_import(self, *args):
        file_path = filedialog.askopenfilename()
        print("Usuario escolheu [{}]".format(file_path))
        prog = importProgramFile(file_path)
        vm_emu.loadProgram([line.split() for line in prog])
        writeProgramField(self.builder.get_object("frame_code"), prog)

    def cb_run(self, *args):
        self.console_write("test 1")
        self.console_write("test 2")
        self.console_write("test 3")
        self.console_write("test 4")
        pass

    def cb_step(self, *args):
        pass

    def console_write(self, text, end='\n'):
        self.console.config(state="normal")
        self.console.insert(END, text + end)
        self.console.config(state="disabled")


if __name__ == '__main__':
    app = VmApp()
    app.run()