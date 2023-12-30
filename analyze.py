
from encoding.decode import decode
from main import DUMP_FILE_PATH


def process_line(line):
    print("Line {} has length {}".format(line[0], len(line[1])))
    if input("See line content? (y/n)") == "y":
        decoded = decode(line[1])
        deserialized = decoded.deserialize()
        print("Deserialized: {}".format(deserialized))


if __name__ == "__main__":
    print("Analyzing dump file: {}".format(DUMP_FILE_PATH))

    # open file
    file = open(DUMP_FILE_PATH, "r")

    # read file
    lines = list(enumerate([line.strip() for line in file.readlines()]))
    print("Read {} lines".format(len(lines)))

    # sort lines by length
    lines.sort(key=lambda x: len(x[1]), reverse=True)

    # print longest line lengths
    print("Longest lines:")
    for i in range(10):
        line_number, line = lines[i]
        print("Line {} has length {}".format(line_number, len(line)))
        decoded = decode(line)
        deserialized = decoded.deserialize()
        print(deserialized, file=open(f"line_{line_number}_deserialized.txt", "w"))

    input("Press any key to see next line...")
    for line in lines:
        process_line(line)
        input("Press any key to see next line...")
