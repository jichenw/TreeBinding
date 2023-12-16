from pathlib import Path
import numpy as np
from collections import deque
neg_directory = Path("/results/struct/negatives/negatives/negatives_all")
pos_directory = Path("/results/struct/positives/positives/positives_all")
directories = [neg_directory, pos_directory]
files = []
seq_dicts = []
max=0
for file in files:
    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(">"):
                continue
            else:
                if len(line.strip())>max:
                    max = len(line.strip())
for directory in directories:
    seq_dict = {}
    for file in directory.iterdir():
        with open(file, "r") as f:
            mode =0
            if file.name.endswith(".fa"):
                mode = 1
            elif file.name.endswith(".txt"):
                mode = 2
            lines = f.readlines()
            for i in range(len(lines)):
                if mode==0 and i<=0:
                    continue
                if lines[i].startswith(">"):
                    id = lines[i].split(':')[0][1:]
                    #smt to trim line and get the sequence idenity
                    if seq_dict[id] is None:
                        seq_dict[id] = []
                    while(i<len(lines) and not lines[i].startswith(">")):
                        if mode == 0:
                            line = lines[i].strip().split(" ")[1]
                            for j in range(len(line),max):
                                line.append('0.0')
                        if mode == 1:
                            line = lines[i].strip().lfit(max,"n")
                        else:
                            line = lines[i].strip()
                        seq_dict[id].append(line)
                        i+=1
    seq_dicts.append((str(directory),seq_dict))

    lists = deque()
    for key, value in seq_dict.items():
        l = [key,list(value)]
        lists.append(l)
    arr = np.array(lists)
    np.savetxt(str(directory)+".csv", arr, delimiter=",", fmt='%s')
        
