class IgnoreList(list):
    """
    A list like object that loads contents from a file and everything that is appended here gets also
    appended in the file
    """

    def __init__(self, filename):
        self.filename = filename
        self.load_file()

    def append(self, p_object):
        self.append_file(p_object)
        super().append(p_object)

    def load_file(self):
        with open(self.filename, 'a+') as f:
            f.seek(0)
            self.extend(int(x) for x in f.read().splitlines())

    def append_file(self, p_object):
        with open(self.filename, 'a+') as f:
            f.write(str(p_object) + '\n')
