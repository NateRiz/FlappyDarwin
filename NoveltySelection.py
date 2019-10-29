from math import sqrt


class Novelty:
    def __init__(self):
        self.MIN_ARCHIVE_ADD_DISTANCE = 10.0
        self.archive = {(0, 0)}
        print("X ISNT REAL. ADD FRAMES. DIST IS WRONG")

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


def distance(a, b):
    return abs(sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2))
