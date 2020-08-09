import os
import pygubu
import VM
import TKHelper
from tkinter import filedialog
from tkinter import *

# TODO (improv) add reset button (i=0, stack=[], s=-1)
# TODO (improv) prevent window resizing

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "emulador.ui")

colorScheme = { # TODO (improv) choose better color scheme
    "highlightBg": "royal blue",
    "defaultBg": "light grey"
}

PROGRAM_HEADERS = ["Breakpoint", "Linha", "Label", "Comando", "Parâmetros"]

def importProgramFile(file_path):
    fd = open(file_path, "r")
    return [line.rstrip() for line in fd.readlines()]

class VmApp:
    def __init__(self):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('toplevel')
        builder.connect_callbacks(self)
        self.console = builder.get_object("console_output") # TODO implement console auto scrolling when text is inserted
        self.emulatorMemoryView = builder.get_object("frame_mem")
        self.__prevS = None
        self.__prevI = None

        self.writeProgramField(self.builder.get_object("frame_code"), [])
        self.updateMemoryView([], -1)

        self._vm = VM.VM(self)
        self._vm.prime()

    def parseLine(self, tokens):
        aux = [None] + tokens if self._vm.isValidCmd(tokens[0]) else tokens + [None] 
        return aux + [None] * (3 - len(aux))

    def run(self):
        self.mainwindow.mainloop()

    def cb_import(self, *args):
        file_path = filedialog.askopenfilename()
        print("Usuario escolheu [{}]".format(file_path))
        prog = importProgramFile(file_path)
        self._vm.loadProgram([line.split() for line in prog])
        self.writeProgramField(self.builder.get_object("frame_code"), prog, highlight=0)
        print("Done!")

    def cb_run(self, *args):
        self._vm.execute()

    def cb_step(self, *args):
        self._vm.step()

    def console_write(self, text, end='\n'):
        self.console.config(state="normal")
        self.console.insert(END, text + end)
        self.console.config(state="disabled")

    def clearFrame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def writeProgramField(self, programWidget, program, highlight=None): # TODO (improv) prevent empty frame when loading prog
        self.clearFrame(programWidget)
        self.breakpoints = []
        self.programScrollFrame = TKHelper.ScrollFrame(programWidget)
        tableRelief = "solid"
        global programTableView 
        programTableView = self.programScrollFrame.viewPort

        for idx, key in enumerate(PROGRAM_HEADERS):
            Label(self.programScrollFrame.viewPort, text=key, font=('bold'), relief=tableRelief).grid(row=0, column=idx, sticky="snew")
            self.programScrollFrame.viewPort.columnconfigure(idx, minsize=len(key))

        for _lineNo, pLine in enumerate(program):
            _var = IntVar()
            self.breakpoints.append(_var)
            _bg = colorScheme["highlightBg"] if _lineNo == highlight else colorScheme["defaultBg"]
            Checkbutton(self.programScrollFrame.viewPort, relief=tableRelief, bg=_bg, variable=_var).grid(row=_lineNo+1, column=0, sticky="snew")
            Label(self.programScrollFrame.viewPort, text=str(_lineNo + 1), relief=tableRelief, bg=_bg).grid(row=_lineNo+1, column=1, sticky="snew")

            for idx, token in enumerate(self.parseLine(pLine.split(" "))):
                Label(self.programScrollFrame.viewPort, text=token, relief=tableRelief, bg=_bg).grid(row=_lineNo+1, column=2+idx, sticky="snew")

        self.programScrollFrame.pack(side="top", fill="both", expand=True)

    def updateProgramHighlight(self, instrRegister):
        if instrRegister < 0:
            return

        if self.__prevI:
            if self.__prevI == instrRegister+1:
                return
            for widget in self.programScrollFrame.viewPort.grid_slaves(row=self.__prevI):
                widget.config(bg=colorScheme["defaultBg"])
        
        self.__prevI = instrRegister+1

        for widget in self.programScrollFrame.viewPort.grid_slaves(row=self.__prevI):
            widget.config(bg=colorScheme["highlightBg"])

    # TODO (improv) use this function when stack does not grow
    def updateMemoryField(self, stackRegister):
        if stackRegister < 0:
            return

        if self.__prevS:
            if self.__prevS == stackRegister+1:
                return
            for widget in self.memScrollFrame.viewPort.grid_slaves(row=self.__prevS):
                widget.config(bg=colorScheme["defaultBg"])
        
        self.__prevS = stackRegister+1

        for widget in self.memScrollFrame.viewPort.grid_slaves(row=self.__prevS):
            widget.config(bg=colorScheme["highlightBg"])

    def updateMemoryView(self, memory, stackRegister):
        self.clearFrame(self.emulatorMemoryView)
        self.memScrollFrame = TKHelper.ScrollFrame(self.emulatorMemoryView)
        tableRelief = "solid"

        for idx, key in enumerate(["Posição", "Valor"]):
            Label(self.memScrollFrame.viewPort, text=key, font=('bold'), relief=tableRelief).grid(row=0, column=idx, sticky="snew")

        for idx, val in enumerate(memory):
            _bg = colorScheme["highlightBg" if idx == stackRegister else "defaultBg"]
            Label(self.memScrollFrame.viewPort, text=str(idx), relief=tableRelief, bg=_bg).grid(row=idx+1, column=0, sticky="snew")
            Label(self.memScrollFrame.viewPort, text=str(val), relief=tableRelief, bg=_bg).grid(row=idx+1, column=1, sticky="snew")

        self.memScrollFrame.pack(side="top", fill="y", expand=True)
        
        self.__prevS = stackRegister+1

    def emulatorStdout(self, text):
        self.console_write("Saída: " + str(text))

    def emulatorStdin(self):
        # TODO implement this mess
        # Should block until user writes content and presses enter
        # Optionally loop if input is invalid
        return 6 # Mock

    def isInstructionBreak(self, instruction):
        return self.breakpoints[instruction].get()
        #return self.programScrollFrame.viewPort.grid_slaves(row=instruction+1, column=PROGRAM_HEADERS.index("Breakpoint"))[0].var.get()

if __name__ == '__main__':
    app = VmApp()
    app.run()