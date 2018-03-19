#! /usr/bin/env python3

"""
change the state coding and color of dense.bed output from chromHMM. (--file_type dense)
change the state coding for the segments.bed output from chromHMM. (--file_type seg)
sometimes, several states are very similar, you want to combine them.
or you do not like the color schem of the file and you want to rename the state by yourself.
you will need to provide a mapping file for new state and color.

for segment.bed file, there is no header and the 4th state column has a prefix E. e.g. E1, E2...E15
for dense.bed file, there is a header and the 4th state column is just a number. e.g. 1,2...15. The 9th column is RGB color.
python recode_dense_seg_state_color.py --file_type [dense, seg] --infile segment_dense.bed --state_color_map my_map.txt  --ofile segment_new_color.bed

The my_map.txt file looks like (header required):
old_state	new_state	new_color
1	1	0,0,255
10	10	204,153,255
11	11	204,204,102
12	12	255,255,0
13	13	255,255,204
14	14	102,51,153
15	15	102,153,51
2	2	0,153,204
3	3	0,255,255
4	3	0,255,255
5	5	0,204,51
6	6	0,102,0
7	7	0,0,51
8	3	0,255,255
9	9	255,0,204

The easiest way to create this file: cat segment_dense.bed | sed '1d' | cut -f4,9 | sort | uniq > my_map.txt
then edit by hand.
...

In this example, state 3,4,8 changed to 3.

new_color should be the same for the same new_state.


"""
import argparse

# borrow from https://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (red, green, blue)


#hex_to_rgb("#ffffff")           #==> (255, 255, 255)
#hex_to_rgb("#ffffffffffff")     #==> (65535, 65535, 65535)
#rgb_to_hex(255, 255, 255)       #==> '#ffffff'
#rgb_to_hex(65535, 65535, 65535) #==> '#ffffffffffff'

def check_state_num(file_type, ifile):
    """ check how many states in the input file """
    states = []
    with open(ifile, "r") as f:
        if file_type == "seg":
            for line in f:
                line_split = line.strip().split('\t')
                state = line_split[3]
                if state not in states:
                    states.append(state)
        elif file_type == "dense":
            # skipt the header
            f.readline()
            for line in f:
                line_split = line.strip().split('\t')
                state = line_split[3]
                if state not in states:
                    states.append(state)
        return len(states)

def check_file_type(file_type, ifile):
    f = open(ifile, "r")
    if file_type == "seg":
        line1 = f.readline()
        if len(line1.strip().split("\t")) != 4:
            raise Exception("the seg file should have only 4 columns.")
    elif file_type == "dense":
        f.readline()
        line2 = f.readline()
        if len(line2.strip().split("\t")) != 9 :
            raise Exception("the dense file should have only 9 columns.")


def read_map(file_type, ifile, map_file):
    map_dict = {}
    with open(map_file) as f:
        # skip header
        f.readline()
        for line in f:
            line_split = line.strip().split('\t')
            old_state = line_split[0]
            new_state = line_split[1]
            new_color = line_split[2]
            map_dict[old_state] = [new_state, new_color]
        if len(map_dict) == check_state_num(file_type, ifile):
            return map_dict
        else:
            raise Exception("the number of states in the mapping file is not the same as the input file ")

def remap_per_line(file_type, line, map_dict):
    """
    change state and color for a line
    need a dictionary:
    {'1': ['1', '0,0,255'], '2':['2', '0,153,204'], '3':['3', '0,255,255'], '4':['3', '0,255,255']...}
    """
    line_split = line.strip().split('\t')
    if file_type == "seg":
        old_state = line_split[3].replace("E", "")
        new_state = map_dict[old_state][0]
        return [line_split[0], line_split[1], line_split[2], "E" + new_state]

    elif file_type == "dense":
        old_state = line_split[3]
        new_state = map_dict[old_state][0]
        new_color = map_dict[old_state][1]
        return [line_split[0], line_split[1], line_split[2], new_state, line_split[4], \
    line_split[5], line_split[6], line_split[7], new_color]

def remap_state_color(file_type, ifile, map_file, ofile):
    ofile = open(ofile, "w")
    map_dict = read_map(file_type, ifile, map_file)
    with open(ifile, "r") as f:
        if file_type == "seg":
            for line in f:
                new_line = remap_per_line(file_type, line, map_dict)
                ofile.write("\t".join(new_line) + "\n")
        elif file_type == "dense":
            header = f.readline()
            ofile.write(header)
            for line in f:
                new_line = remap_per_line(file_type, line, map_dict)
                ofile.write("\t".join(new_line) + "\n")
    ofile.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_type", help="Required. file type of the input file. either seg or dense ")
    parser.add_argument("--ifile", help="Required. the FULL path to the input dense.bed or segment.bed file ")
    parser.add_argument("--map_file", help="Required. the FULL path to the state color map file ")
    parser.add_argument("--ofile", help="Required. the FULL path to the output modified segment_dense.bed file")
    args = parser.parse_args()
    assert args.file_type == "seg" or args.file_type == "dense", "please specify either seg or dense as file_type"
    assert args.ifile is not None, "please provide the path to the input dense.bed or segment.bed file"
    assert args.map_file is not None, "please provide the path to the state color map file"
    assert args.ofile is not None, "please provide the path to the output modified dense.bed or segment.bed file"

    check_file_type(args.file_type, args.ifile)
    remap_state_color(args.file_type, args.ifile, args.map_file, args.ofile)


if __name__ == "__main__":
    main()
