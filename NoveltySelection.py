from Utils import distance
import os

class Novelty:
    def __init__(self):
        self.MIN_ARCHIVE_ADD_DISTANCE = 10.0
        self.archive = {(0, 0)}

    def select(self, coords):
        dists = [sum([distance(a, b) for b in self.archive]) / len(self.archive) for a in coords]
        ids = list(range(len(coords)))
        ids.sort(key=lambda i: dists[i], reverse=True)
        i = 0
        while i < len(ids) and dists[ids[i]] > self.MIN_ARCHIVE_ADD_DISTANCE:
            self.archive.add(coords[ids[i]])
            i += 1
        print("archive len: ", len(self.archive))
        return dists

def save_novelty_archive(novelty):
    path = os.path.join(os.getcwd(), "archive.nvl")
    with open(path, "w") as file:
        for x, y in novelty.archive:
            file.write(F"{x} {y}\n")

def load_novelty_archive(novelty):
    path = os.path.join(os.getcwd(), "archive.nvl")
    novelty.archive.clear()
    with open(path, "r") as file:
        for line in file.readlines():
            line = line.strip().split()
            if not line: continue
            assert len(line) == 2, "Corrupt archive.nvl"
            novelty.archive.add((int(line[0]), int(line[1])))

