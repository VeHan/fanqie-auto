def readfile(path):
    with open(path, encoding='utf-8') as f:
        txt = ''
        for s in f.readlines():
            txt += s + '\n'
        return txt