#!/usr/bin/env python3


import json
import os
import csv
import re
from os.path import join
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--segment_dir", help="Required. the FULL path to the chromHMM segment folder")
args = parser.parse_args()

assert args.segment_dir is not None, "please provide the path to the chromHMM segment folder"


FILES = defaultdict(list)

for root, dirs, files in os.walk(args.segment_dir):
    for file in files:
        if file.endswith("segments.bed"):
            full_path = join(root, file)
            # SKCM-7226_15_segments.bed
            m = re.search(r"(.+)_[0-9]+_segments.bed", file)
            sample = m.group(1)
            FILES[sample].append(full_path)



print()
sample_num = len(FILES.keys())
print ("total {} unique samples will be processed".format(sample_num))

print ("------------------------------------------")
for sample in sorted(FILES.keys()):
	print ("{sample}".format(sample = sample))
print ("------------------------------------------")
print("check the samples.json file for segment file belong to each sample")
print()

js = json.dumps(FILES, indent = 4, sort_keys=True)
open('samples.json', 'w').writelines(js)
