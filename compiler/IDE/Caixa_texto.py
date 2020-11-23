import tkinter as tk
import tkinter.ttk as ttk

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

class IndexedText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, height = 25, *args, **kwargs)
        self.result = 0
        self.escreveu = False
        self.cursor = self.index(tk.INSERT)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        try:
            self.result = self.tk.call(cmd)
        except:
            pass
        


        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        if (args[0] in ("insert", "replace", "delete")):
            self.escreveu = True

        # return what the actual widget returned
        return self.result

class IndexedTextWrapper(tk.Frame):
    def __init__(self, main):
        tk.Frame.__init__(self, main)
        self.text = IndexedText(self)
        self.vsb = tk.Scrollbar(main, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        #self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
        self.linenumbers = TextLineNumbers(self, width=50)
        self.linenumbers.attach(self.text)

        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)


    def _on_change(self, event):
        if self.text.escreveu:
            self.text.tag_remove('erro','1.0', 'end')
            self.text.escreveu = False
        self.linenumbers.redraw()
        self.text.cursor = self.text.index(tk.INSERT)

        
if __name__ == "__main__":
    root = tk.Tk()
    IndexedTextWrapper(root).pack(side="top", fill="both", expand=True)
    root.mainloop()

    