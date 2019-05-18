configfile: "config.yaml"

from os.path import join, expanduser
import os
import sys

# Snakemake workflow for neoantigen prediction


# If input variant file format is MAF
# extra steps are needed.

rule maf2vcf:
    input:
        maf = expanduser(config['input']['variants']['path'])
    # output:
    #     "tumor_normal_vcf_pair/{sample}_vs_NORMAL.vcf",
    #     "tumor_normal_vcf_pair/input.pairs.tsv",
    #     "tumor_normal_vcf_pair/input.vcf"
    run:
        if not os.path.isfile(input.maf):
            print("> Cannot find Maf file. Exiting...")
            sys.exit(1)
        print("> Maf file detected")
        output = join(config['output']['path'], 'tumor_normal_vcf_pair')
        print("> Output path is %s"%)
        print("> Run maf2vcf.pl ...")
        shell("echo Hello world")
