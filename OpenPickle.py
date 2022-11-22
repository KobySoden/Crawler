import pickle
from os import listdir, getcwd
from os.path import isfile, join

def loadfile(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
        #print(len(data))
        f.close()
    return data

def loaddirectory(directory = getcwd):
    onlyfiles = getfiles(directory)
    output = []

    for f in onlyfiles:
        output.append(loadfile(directory + "/" + f))
    return output    

def getfiles(directory):
    return [f for f in listdir(directory) if isfile(join(directory, f))]

if __name__ == "__main__":
    cwd = getcwd()
    directory = cwd + '/data'
    data = loaddirectory(directory)
    print("Loaded " + str(len(data)) + " Pickles!")