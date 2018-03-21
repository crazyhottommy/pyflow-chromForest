shell.prefix("set -eo pipefail; echo BEGIN at $(date); ")
shell.suffix("; exitstat=$?; echo END at $(date); echo exit status was $exitstat; exit $exitstat")

configfile: "config.yaml"

# load cluster config file
CLUSTER = json.load(open(config['CLUSTER_JSON']))
FILES = json.load(open(config['SAMPLES_JSON']))

SAMPLES = sorted(FILES.keys())
chrs = config["CHR"]
CHR = chrs.split(" ")


ALL_TILTED_SEG = expand("01tile_seg/{sample}_seg.bed", sample = SAMPLES)
ALL_RECODE_SEG = expand("02state_recode/{sample}_recode_seg.bed", sample = SAMPLES)
EPILOGOS_INPUT = ["03combine_sample_segs/epilogos_input.txt"]
EPILOGOS_OUTPUT = ["06epilogos_output/merged_epilogos_qcat.bed.gz"]
VSURF_OUTPUT = expand("09vsurf_output_by_chr/{chromosome}_vsurf_out.rda", chromosome = CHR)

TARGETS = []
TARGETS.extend(ALL_TILTED_SEG)
TARGETS.extend(ALL_RECODE_SEG)
TARGETS.extend(EPILOGOS_INPUT)
TARGETS.extend(EPILOGOS_OUTPUT)
TARGETS.extend(VSURF_OUTPUT)

localrules: all
rule all:
    input: TARGETS


rule tile_seg:
    input: lambda wildcards: FILES[wildcards.sample]
    output: "01tile_seg/{sample}_seg.bed"
    log: "00log/{sample}_tile_seg.log"
    threads: 1
    params:
        jobname = "{sample}"
    message: "tiling chromHMM state call back to bin size for {input}"
    script: "scripts/tile_seg.R"


rule state_recode_seg:
    input: "01tile_seg/{sample}_seg.bed"
    output: "02state_recode/{sample}_recode_seg.bed"
    log: "00log/{sample}_state_recode.log"
    threads: 1
    params: jobname = "{sample}"
    message: "recoding the chromatin state for {input}"
    shell:
        r"""
        scripts/recode_dense_seg_state_color.py --file_type seg --ifile {input} \
        --map_file {config[map_file]} --ofile {output}
        """

## this rule will create a dataframe with a header. rows are segs, columns are chr, start, end,
## sample1, sample2...
## and epilogos input without header and state need to be changed from E1 to 1, E2 to 2...
rule combine_sample_segs:
    input: ALL_RECODE_SEG
    output:
        "03combine_sample_segs/combined_seg.txt",
        "03combine_sample_segs/epilogos_input.txt"
    threads: 1
    message: "combining the recoded segments across samples and make epilogos input file"
    script: "scripts/combine_sample_segs.R"

rule split_epilogos_input_by_chr:
    input: "03combine_sample_segs/epilogos_input.txt"
    output: expand("04epilogos_input_by_chr/{chromosome}.txt", chromosome = CHR)
    threads: 1
    message: "splitting eilogos input by chromosome for {input}"
    shell:
        """
        # snakemake will create that folder if it is not exsit
        awk '{{print $0 >> "04epilogos_input_by_chr/"$1".txt"}}' {input}

        """

rule run_epilogos_by_chr:
    input : "04epilogos_input_by_chr/{chromosome}.txt"
    output: "05epilogos_output_by_chr/{chromosome}/qcat.bed.gz"
    threads: 1
    params: jobname = "{chromosome}"
    message: "computing epilogos for {input}"
    shell:
        r"""
        output_dir=$(dirname {output})
        computeEpilogos_singleChromosomeSingleProcessor.sh {input}  {config[measurementType]} \
        {config[numStates]} $output_dir {config[groupSpec]} > {output}
        """

rule merge_epilogos:
    input: expand("05epilogos_output_by_chr/{chromosome}/qcat.bed.gz", chromosome = CHR)
    output: "06epilogos_output/merged_epilogos_qcat.bed.gz"
    threads: 1
    message: "merging epilogos from {input}"
    shell:
        r"""
        zcat {input} | bgzip > {output}
        """

rule merge_bin_vsurf:
    input: "03combine_sample_segs/combined_seg.txt"
    output: "07vsurf_input/vsurf_bin_merged_seg.txt"
    threads: 1
    message: "merging bins for vsurf input"
    shell:
        r"""
        scripts/merge_bin.py --ifile {input} --ofile {output}
        """

rule prefilter_vsurf:
    input: "07vsurf_input/vsurf_bin_merged_seg.txt"
    output:
        "07vsurf_input/vsurf_prefilter_bin_merge_seg_id.txt",
        "07vsurf_input/vsurf_prefilter_bin_merge_seg.txt"
    threads: 1
    message: "pre-filtering segments for vsurf."
    script: "scripts/prefilter_vsurf.R"

rule split_vsurf_input_by_chr:
    input: "07vsurf_input/vsurf_prefilter_bin_merge_seg.txt"
    output: expand("08vsurf_input_by_chr/{chromosome}_vsurf.txt", chromosome = CHR)
    threads: 1
    message: "splitting vsurf input by chromosome for {input}"
    shell:
        """
        # snakemake will create that folder if it is not exsit
        # keep the header to each of the chromosome data.
        awk 'NR == 1 {{header=$0; next}}
            f!= "08vsurf_input_by_chr/"$1"_vsurf.txt"{{
            if(f) close(f)
            f="08vsurf_input_by_chr/"$1"_vsurf.txt"
            print header > f
            }}
            {{print $0 >> f;close(f)}}'  {input}
        """

rule run_vsurf_by_chr:
    input:
        vsurf_input = "08vsurf_input_by_chr/{chromosome}_vsurf.txt",
        meta_data = config["meta_data"]
    output: "09vsurf_output_by_chr/{chromosome}_vsurf_out.rda"
    threads: 24
    params: jobname = "{chromosome}"
    message: "runing vsurf random forest feature selection for {input}"
    script: "scripts/vsurf_feature_selection.R"
