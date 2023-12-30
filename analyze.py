
from encoding.decode import decode
from main import DUMP_FILE_PATH

if __name__ == "__main__":
    print("Analyzing dump file: {}".format(DUMP_FILE_PATH))

    # open file
    file = open(DUMP_FILE_PATH, "r")

    # read file
    lines = list(enumerate(file.readlines()))
    print("Read {} lines".format(len(lines)))

    # sort lines by length
    lines.sort(key=lambda x: len(x[1]), reverse=True)

    # print longest line lengths
    print("Longest lines:")
    for i in range(10):
        print("Line {} has length {}".format(lines[i][0], len(lines[i][1])))

    # deserialize longest line
    decoded = decode(lines[0][1])
    deserialzed = decoded.deserialize()
    print("Deserialized longest line:")
    print(deserialzed)
