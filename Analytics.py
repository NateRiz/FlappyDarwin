import os


class Analytics:
    def __init__(self):
        self.file_name = "analytics.txt"

    def save(self, gen, data):
        path = os.path.join(os.getcwd(), self.file_name)
        if not os.path.exists(path):
            assert (len(data) == gen)
            open(self.file_name, "w").close()
        self._append_data(gen, data)

    def _append_data(self, gen, new_data):
        with open(self.file_name, "r") as file:
            data = [float(x.strip()) for x in file.readlines() if x.strip()]

        assert len(data) >= gen - len(new_data)
        del data[gen-len(new_data)::]

        with open(self.file_name, "w") as file:
            [file.write(F"{d}\n") for d in data]
            [file.write(F"{d}\n") for d in new_data]
