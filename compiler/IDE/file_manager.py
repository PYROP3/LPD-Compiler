
class FileManager:
    def __init__(self):
        self.working_filename = None
        self.working_file = None
        self.is_edited = False

    def create_new_file(self, filename=None):
        self.working_filename = filename
        self.working_file = None
        self.is_edited = False

    def edit_file(self):
        self.is_edited = True

    def open_file_read(self, filename):
        self.working_filename = filename
        self.working_file = open(filename, 'r', encoding='utf-8')
        self.is_edited = False
        return self.working_file

    def open_file_write(self, filename=None):
        self.working_filename = filename or self.working_filename
        self.working_file = open(self.working_filename, 'w', encoding='utf-8')

    def close_file(self):
        self.working_file.close()
        self.working_file = None

    def is_file_named(self):
        return self.working_filename is not None

    def save_to_file(self, contents):
        if self.working_file is None:
            self.open_file_write()

        self.working_file.write(contents)
        
        self.close_file()

        self.is_edited = False