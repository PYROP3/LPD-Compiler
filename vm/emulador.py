import os
import pygubu


PROJECT_PATH = os.path.dirname(__file__)
PROJECT_UI = os.path.join(PROJECT_PATH, "vm.ui")


class VmApp:
    def __init__(self):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object('toplevel')
        builder.connect_callbacks(self)
    

    def run(self):
        self.mainwindow.mainloop()

if __name__ == '__main__':
    app = VmApp()
    app.run()