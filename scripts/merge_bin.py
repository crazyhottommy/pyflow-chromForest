
#! /usr/bin/env python3

"""
merge consecutive bins together if the states across samples
are the same. It does not matter how many samples (columns after chr, start, end)
you have.

python merge_bin.py --infile input.txt --ofile output.txt

chr1    0   200 E1  E2  E2  E3
chr1    200 400 E1  E2  E2  E3
chr1    400 600 E2  E2  E2  E3

will be merged to

chr1    0   400 E1  E2  E2  E3
chr1    400 600 E2  E2  E2  E3

This assumes the coordinates are sorted and consecutive across the chromosome.
If the chromHMM calls are not tiled in to the bin size (200bp in the case). use
the tile_genome.R script to do it.
"""

import argparse
import sys

def merge_bin(ifile, ofile):
    ofile = open(ofile, "w")
    with open(ifile, "r") as f:
        # keep the first line
        header = f.readline()
        ofile.write(header)
        # a set of chromosomes seen so far
        chrSet = set()
        # loop over each line
        for line in f:
            # split each line to a list
            lineSplit = line.strip().split()
            chr = lineSplit[0]
            start = lineSplit[1]
            end = lineSplit[2]
            states = lineSplit[3:]

            # the first time process this chromosome
            if chr not in chrSet:
                chrSet.add(chr)
                previous_line = [chr, start, end, states]
            else:
                if states != previous_line[3]:
                    ofile.write(previous_line[0] + "\t" + previous_line[1] + "\t" + \
                    previous_line[2] + "\t" + "\t".join(previous_line[3]) + "\n")
                    # set previous line to current line
                    previous_line = [chr, start, end, states]
                else:
                    new_start = previous_line[1]
                    new_end = end
                    previous_line = [chr, new_start, new_end, states]
    ## always remember to close the file!
    ofile.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifile", help="Required. the FULL path to the input segment file. must coordinate sorted ")
    parser.add_argument("--ofile", help="Required. the FULL path to the merged segment file")
    args = parser.parse_args()
    assert args.ifile is not None, "please provide the path to the coordinate sorted input segment file"
    assert args.ofile is not None, "please provide the path to the merged segment file"
    merge_bin(args.ifile, args.ofile)


if __name__ == "__main__":
    main()
