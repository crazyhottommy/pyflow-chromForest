#! /usr/bin/env python3

"""
choose state from a epilogos output. It does not matter how many states in the model.
This script will choose the state with the greates value.

python choose_state.py --infile input.txt --ofile output.txt

chr1	126474600	126474800	id:632374,qcat:[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.5832,15] ]
chr1	103536000	103536200	id:517681,qcat:[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.5832,15] ]
chr1	235431400	235431600	id:1177158,qcat:[ [-0.2303,15], [0,1], [0,2], [0,3], [0,4], [0,6], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.9458,7], [1.688,5] ]
chr1	130883200	130883400	id:654417,qcat:[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.5832,15] ]
chr1	168036200	168036400	id:840182,qcat:[ [0,1], [0,2], [0,3], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0,15], [0.8748,5], [2.135,4] ]
chr1	134171800	134172000	id:670860,qcat:[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.5832,15] ]
chr1	32956200	32956400	id:164782,qcat:[ [-0.3222,15], [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [1.595,14] ]
chr1	36426200	36426400	id:182132,qcat:[ [-0.3513,15], [0,1], [0,2], [0,3], [0,4], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [2.291,5] ]
chr1	237380600	237380800	id:1186904,qcat:[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0.04442,14], [0.3093,15] ]
chr1	71615400	71615600	id:358078,qcat:[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.5832,15] ]

will change to

chr1	126474600	126474800	E15
chr1	103536000	103536200	E15
chr1	235431400	235431600	E5
chr1	130883200	130883400	E15
chr1	168036200	168036400	E4
chr1	134171800	134172000	E15
chr1	32956200	32956400	E14
chr1	36426200	36426400	E5
chr1	237380600	237380800	E15
chr1	71615400	71615600	E15

"""
import argparse

def choose_state_per_line(line):
    line_split = line.strip().split('\t')
    chr = line_split[0]
    start = line_split[1]
    end = line_split[2]
    qcat = line_split[3]
    states = qcat.split(":")[2].split(",")
    # something like '[ [0,1], [0,2], [0,3], [0,4], [0,5], [0,6], [0,7], [0,8], [0,9], [0,10], [0,11], [0,12], [0,13], [0,14], [0.5832,15] ]'
    states_clean = [state.replace("[", "").replace("]", "").strip()  for state in states]
    ## make a dict comprehension
    states_dict = {"E" + states_clean[i+1]:float(states_clean[i]) for i in range(0,len(states_clean),2)}
    max_state = max(states_dict.keys(), key=(lambda key: states_dict[key]))
    # or even simpler max(states_dict, key=states_dict.get)
    return [chr, start, end, max_state]

def choose_state(ifile, ofile):
    ofile = open(ofile, "w")
    with open(ifile, "r") as f:
        for line in f:
            line_to_write = choose_state_per_line(line)
            ofile.write(line_to_write[0] + "\t" + line_to_write[1] + "\t" \
            + line_to_write[2] + "\t" + line_to_write[3] + "\n")
    ofile.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifile", help="Required. the FULL path to the input qcat epilogos file ")
    parser.add_argument("--ofile", help="Required. the FULL path to the output chromHMM state file")
    args = parser.parse_args()
    assert args.ifile is not None, "please provide the path to the qcat epilogos file"
    assert args.ofile is not None, "please provide the path to the output chromHMM state file"
    choose_state(args.ifile, args.ofile)


if __name__ == "__main__":
    main()
