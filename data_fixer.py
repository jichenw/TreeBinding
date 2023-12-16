
with open(file, "r") as f1, open(file2, "w") as f2:
    lines = f1.readlines()
    for line in lines:
        if line.startswith(">"):
            f2.write("\n" +line)
        else:
            f2.write(line.strip())