import tkinter as tk

# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)
        self.currentLine = 0

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((0,0), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the viewPort frame changes.

        # Bind entering/leaving to bind scroll wheel events
        self.bind('<Enter>', self.bindScrolling)
        self.bind('<Leave>', self.unbindScrolling)

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def bindScrolling(self, event):
        # if x11
        self.canvas.bind_all("<Button-4>", lambda event: self.resolveScrollEvent(event, k=1))
        self.canvas.bind_all("<Button-5>", lambda event: self.resolveScrollEvent(event, k=-1))
        # if win/osx
        self.canvas.bind_all("<MouseWheel>", self.resolveScrollEvent)

    def resolveScrollEvent(self, event, k=1):
        if self.canvas.bbox("all")[3] <= self.winfo_height(): # Fits in view, no need to scroll
            return
        self.canvas.yview_scroll(k * self.translateScrollEvent(event), "units")
        
    def unbindScrolling(self, event):
        # if x11
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
        # if win/osx
        self.canvas.unbind_all("<MouseWheel>")

    def jump(self, line):
        self.canvas.yview_scroll(line - self.currentLine, "units")
        self.currentLine = line

    def translateScrollEvent(self, event): # TODO (improv) choose correct method using system os
        return int(-1*(event.delta/120)) if event.delta else -1

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = self.viewPort.bbox("all")[2] #event.width
        #print(self.viewPort.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)            #whenever the size of the canvas changes alter the window region respectively.
        self.canvas.config(width=canvas_width)