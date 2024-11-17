def readfile(path):
    with open(path) as f:
        txt = ''
        for s in f.readlines():
            txt += s + '\n'
        return txt