#!/usr/bin/env python3

import os
import pygubu
import VM
import TKHelper
from tkinter import filedialog
from tkinter import Tk, StringVar, END, IntVar, Label, Checkbutton, ttk
import threading
import _thread
import sys

PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "emulador.ui")

colorScheme = { # TODO (improv) choose better color scheme
    "highlightBg": "royal blue",
    "defaultBg": "light grey",
    "errorBg": "indian red",
    "typingBc": "spring green",
    "defaultEntryBc": "black",
    "defaultEntryBg": "gray99"
}

PROGRAM_HEADERS = [" Breakpoint ", " Linha ", " Label ", " Comando ", " Parâmetros "]

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
        self.console = builder.get_object("console_output")
        self.emulatorMemoryView = builder.get_object("frame_mem")
        self.__prevS = None
        self.__prevI = None
        self._prevStack = []

        # Graceful exit
        self.mainwindow.protocol("WM_DELETE_WINDOW", self.shutdown)
        
        # Prevent resize
        #self.mainwindow.resizable(False, False) # TODO add dynamic resizing

        self._disableControls(bImport=False)

        self.writeProgramField(self.builder.get_object("frame_code"), [])
        self.initMemoryView()

        # Prepare stdin
        self.Stdin_buffer_lock = threading.Lock()
        self.Stdin_buffer_lock.acquire() # Lock objects are released by default
        self.Stdin_request_lock = threading.Lock()
        self.Stdin_request_lock.acquire() # Lock objects are released by default
        self.GUI_Stdin = self.builder.get_object("console_input")
        self.Stdin_buffer = StringVar()
        self.GUI_Stdin.config(textvariable=self.Stdin_buffer)
        self.GUI_Stdin.bind("<FocusIn>", lambda event: self._bindStdinKeys())
        self.GUI_Stdin.bind("<FocusOut>", lambda event: self._uhbindStdinKeys())
        self.GUI_Stdin["style"] = "EntryStyle.TEntry"

        self._vm = VM.VM(self)
        self._vm.prime()

        self.estyle = ttk.Style()
        self.estyle.element_create("plain.field", "from", "clam")
        self.estyle.layout("EntryStyle.TEntry",
                        [('Entry.plain.field', {'children': [(
                            'Entry.background', {'children': [(
                                'Entry.padding', {'children': [(
                                    'Entry.textarea', {'sticky': 'nswe'})],
                            'sticky': 'nswe'})], 'sticky': 'nswe'})],
                            'border':'6', 'sticky': 'nswe'})])
        self.estyle.configure("EntryStyle.TEntry", fieldbackground=colorScheme["defaultEntryBg"], bordercolor=colorScheme["defaultEntryBc"])

    def shutdown(self):
        self._vm._shutdown()
        try:
            self.Stdin_buffer_lock.release()
        except RuntimeError:
            pass
        try:
            self.Stdin_request_lock.release()
        except RuntimeError:
            pass
        os._exit(0)

    def update(self):
        pass
        #self.mainwindow.update()

    def _bindStdinKeys(self):
        self.GUI_Stdin.bind("<Return>", lambda event: self._onStdin())
        self.GUI_Stdin.bind("<Escape>", lambda event: self.mainwindow.focus_set())

    def _uhbindStdinKeys(self):
        self.GUI_Stdin.unbind("<Return>")
        self.GUI_Stdin.unbind("<Escape>")

    def _onStdin(self):
        # Should only be called if stdin is being requested
        if not self.Stdin_request_lock.acquire(blocking=False):
            return
        try:
            # Inform there is data available
            self.Stdin_buffer_lock.release()
        except RuntimeError:
            pass

    def parseLine(self, tokens):
        aux = [None] + tokens if self._vm.isValidCmd(tokens[0]) else tokens + [None] 
        return aux + [None] * (3 - len(aux))

    def run(self):
        self.mainwindow.mainloop()

    def cb_import(self, *args):
        file_path = filedialog.askopenfilename()
        if (file_path == ''):
            return
        print("Loading [{}]".format(file_path))
        try:
            prog = importProgramFile(file_path)
            self._vm.loadProgram([line.split() for line in prog])
            self.writeProgramField(self.builder.get_object("frame_code"), prog, highlight=0)
            self._enableControls()
            print("Done!")
        except FileNotFoundError:
            pass 
        except TypeError:
            pass

    def cb_run(self, *args):
        # Disable run and step buttons until breakpoint
        self._disableControls()
        threading.Thread(target=self._vm.execute, args=()).start()

    def cb_step(self, *args):
        # Disable run and step buttons until step finishes
        self._disableControls()
        threading.Thread(target=self._vm.step, args=([self._enableControls])).start()
        self.programScrollFrame.jump(line=self.__prevI)
        self.memScrollFrame.jump(line = self.__prevS)

    def cb_reset(self, *args):
        self._vm._reset()
        self.initMemoryView()
        self.console_write("*** VM RESET ***")
        self._enableControls()

    def console_write(self, text, end='\n'):
        self.console.config(state="normal")
        self.console.insert(END, text + end)
        self.console.config(state="disabled")
        self.console.see(END)

    def clearFrame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def writeProgramField(self, programWidget, program, highlight=None): # TODO (improv) prevent small/empty frame when loading prog
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
            

    def updateMemoryView(self, newStack, stackRegister):
        tableRelief = "solid"
        for idx, contents in enumerate(newStack):
            try:
                if contents != self._prevStack[idx]:
                    self.memScrollFrame.viewPort.grid_slaves(row=idx+1, column=1)[0].config(text=str(f'{contents:.2e}') if len(contents) > 6 else str(contents))
            except IndexError:
                Label(self.memScrollFrame.viewPort, text=str(idx), relief=tableRelief, bg=colorScheme["defaultBg"]).grid(row=idx+1, column=0, sticky="snew")
                Label(self.memScrollFrame.viewPort,text=str(f'{contents:.2e}') if len(contents) > 6 else str(contents), relief=tableRelief, bg=colorScheme["defaultBg"]).grid(row=idx+1, column=1, sticky="snew")
        self._prevStack = newStack[:]

        if self.__prevS:
            if self.__prevS == stackRegister+1:
                return
            for widget in self.memScrollFrame.viewPort.grid_slaves(row=self.__prevS):
                widget.config(bg=colorScheme["defaultBg"])
        
        self.__prevS = stackRegister+1
        if self.__prevS > 0:
            for widget in self.memScrollFrame.viewPort.grid_slaves(row=self.__prevS):
                widget.config(bg=colorScheme["highlightBg"]) # FIXME scroll to highlighted entry

        self.memScrollFrame.pack(side="top", fill="y", expand=True)

    def initMemoryView(self):
        tableRelief = "solid"
        self.clearFrame(self.emulatorMemoryView)
        self.memScrollFrame = TKHelper.ScrollFrame(self.emulatorMemoryView)
        for idx, key in enumerate([" Posição ", "  Valor  "]):
            Label(self.memScrollFrame.viewPort, text=key, font=('bold'), relief=tableRelief).grid(row=0, column=idx, sticky="snew")
        self.memScrollFrame.pack(side="top", fill="y")

    def emulatorStdout(self, text):
        self.console_write("Saída: " + str(text))

    def emulatorStdin(self):
        # Enable text field
        self.estyle.configure("EntryStyle.TEntry", bordercolor=colorScheme["typingBc"])
        self.GUI_Stdin["style"] = "EntryStyle.TEntry"
        self.programScrollFrame.jump(line=self.__prevI)
        self.memScrollFrame.jump(line = self.__prevS)
        self.GUI_Stdin.config(state="normal", cursor="xterm")
        threading.Thread(target=self.threadStdin).start()

    def threadStdin(self):
        while True:
            # Allow input (release lock)
            try:
                self.Stdin_request_lock.release()
            except RuntimeError: # FIXME this should not be necessary
                pass
            # Should block until user writes content and presses enter
            self.Stdin_buffer_lock.acquire()
            # Get int value
            try:
                _aux = int(self.Stdin_buffer.get())
                self.console_write("Entrada: " + str(_aux))
                self.GUI_Stdin.delete(0, END) # Clear buffer
                self.GUI_Stdin.config(state="disabled", cursor="X_cursor")
                self._vm._stdinReply(_aux)
                self.estyle.configure("EntryStyle.TEntry", fieldbackground=colorScheme["defaultEntryBg"], bordercolor=colorScheme["defaultEntryBc"])
                self.GUI_Stdin["style"] = "EntryStyle.TEntry"
            except ValueError:
                self.estyle.configure("EntryStyle.TEntry", fieldbackground=colorScheme["errorBg"])
                self.GUI_Stdin["style"] = "EntryStyle.TEntry"
                pass

    def isInstructionBreak(self, instruction):
        return self.breakpoints[instruction].get()

    def cb_onBreakpoint(self):
        self._enableControls()

    def cb_onHalt(self):
        self.programScrollFrame.jump(line=self.__prevI)
        self.memScrollFrame.jump(line = self.__prevS)
        self._setControls(bRun=False, bDebug=False)

    def _enableControls(self, bImport=True, bRun=True, bDebug=True, bReset=True):
        # Re-enable import, run and step buttons
        if bImport:
            self.builder.get_object("button_import").config(state="normal")
        if bRun:
            self.builder.get_object("button_run").config(state="normal")
        if bDebug:
            self.builder.get_object("button_debug").config(state="normal")
        if bReset:
            self.builder.get_object("button_reset").config(state="normal")

    def _disableControls(self, bImport=True, bRun=True, bDebug=True, bReset=True):
        # Disable import, run and step buttons
        if bImport:
            self.builder.get_object("button_import").config(state="disabled")
        if bRun:
            self.builder.get_object("button_run").config(state="disabled")
        if bDebug:
            self.builder.get_object("button_debug").config(state="disabled")
        if bReset:
            self.builder.get_object("button_reset").config(state="disabled")

    def _setControls(self, bImport=True, bRun=True, bDebug=True, bReset=True):
        _d = {"import":bImport, "run":bRun, "debug":bDebug, "reset":bReset}
        for obj in _d:
            self.builder.get_object("button_"+obj).config(state = "normal" if _d[obj] else "disabled")
        
if __name__ == '__main__':
    app = VmApp()
    app.run()