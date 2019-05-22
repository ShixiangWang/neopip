configfile: "config.yaml"

import os
import sys
import glob
import re
import csv

from pathlib import Path
from os.path import join
from subprocess import run, PIPE
from utils import create_dir
from prepare import neopip_loc, vep_loc


# Global definition
if (config['input']['variants']['type']) == 'MAF':
    MAF = Path(config['input']['variants']['path']).absolute()
    VCF = None
else:
    MAF = None
    VCF = Path(config['input']['variants']['path']).absolute()
    VCF_dir = VCF.parent
    VCF = glob.glob(str(VCF))

HLA = Path(config['input']['hla']['path']).absolute()

predict_args = {} # args of prediction
predict_args['methods']     = config['prediction_args']['argorithms']
predict_args['epitope_len'] = config['prediction_args']['epitope_len']
predict_args['iedb']        = join(neopip_loc, 'iedb') 

vep_args = {}  # args of VEP
vep_args['vep']             = config['vep']['vep_path'] if config['vep']['vep_path'] is not None else 'vep'
vep_args['dir_plugin']      = config['vep']['dir_plugin'] if config['vep']['dir_plugin'] is not None else join(vep_loc, 'VEP_plugins') 
vep_args['dir_cache']       = config['vep']['dir_cache'] if config['vep']['dir_cache'] is not None else join(neopip_loc, 'vep')
vep_args['cache_version']   = config['vep']['cache_version']
vep_args['assembly_version'] = config['vep']['assembly_version']

reference_fasta   = config['reference']['fasta']

# Output directories
#dir_annotated = create_dir(config['output']['path'], 'neoantigen_calling', "vep_annotated_vcfs")


# Conda
conda_exe = os.environ['CONDA_EXE']
activate_exe = join(os.path.dirname(conda_exe), 'activate')
env_name = config['prepare']['conda']['env_name']


# Target 
# rule all:
#     input:


# If input variant file format is MAF
# extra steps are needed.
# >>>>>>>>>>>>>>>>>>>>>>
rule maf2vcf:
    input:
        maf = str(MAF) if MAF is not None else ''
    output:
        "neopip_output/maf2vcf/tumor_normal_vcf_pair/{sample}_vs_NORMAL.vcf"
    threads: config['threads']
    params:
        maf2vcf = config['vcf2maf']['maf2vcf'],
        output = "neopip_output/maf2vcf/tumor_normal_vcf_pair",
        fasta = reference_fasta,
        activate = activate_exe,
        env_name = env_name
    message: "> Run maf2vcf.pl..."
    shell:
        """
        set +u; source {params.activate} {params.env_name}; set -u
        {params.maf2vcf} --input-maf {input.maf} \
                            --output-dir {params.output} \
                            --ref-fasta {params.fasta}   \
                            --per-tn-vcfs
        """
rule del_vcf_normal_column:
    input:
        rules.maf2vcf.output
    output:
        "neopip_output/maf2vcf/tumor_single_vcfs/{sample}.vcf"
    message: "> Delete VCF column of normal sample..."
    shell:
        """
        echo ">>> processing {wildcards.sample}"
        cat {input} | awk 'BEGIN{{FS="\\t";OFS="\\t"}}{{if($1 ~ /^##]/){{print $0}}else{{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}}}}' \
            > {output}
        echo ">>> done"
        """
# <<<<<<<<<<<<<<<<<<<<<<

def get_input_vcfs(wildcards):
    if VCF is not None:
        return str(VCF_dir) + "/" + wildcards.sample + ".vcf"
    else:
        return rules.del_vcf_normal_column.output

# Annotate VCFs with VEP
rule vep_annotate:
    input: get_input_vcfs
    output: "neopip_output/vep_annotated_vcfs/{sample}.vcf"
    message: "> Annotate VCF with VEP..."
    params:
        activate = activate_exe,
        env_name = env_name,
        vep = vep_args['vep'],
        dir_plugin = vep_args['dir_plugin'],
        assembly_version = vep_args['assembly_version'], 
        fasta = reference_fasta,
        dir_cache = vep_args['dir_cache'], 
        cache_version = vep_args['cache_version']
    shell:
        """
        echo ">>> processing {wildcards.sample}"
        set +u; source {params.activate} {params.env_name}; set -u
        {params.vep} --input_file {input} --format vcf --output_file stdout \
             --vcf --symbol --terms SO --plugin Downstream --plugin Wildtype \
             --dir_plugins {params.dir_plugin} --assembly {params.assembly_version} --fasta {params.fasta} \
             --dir_cache {params.dir_cache} --offline --cache_version {params.cache_version} --pick --force_overwrite \
             > {output}
        echo ">>> done"
        """

rule pvacseq_predict:
    input: 
        vcf = rules.vep_annotate.output,
        hla = HLA
    output: 
        dir_calling = directory("neopip_output/neoantigen_calling/{sample}")
    message: "> Predict neoantigens with pvacseq..."
    threads: config['threads']
    params:
        activate = activate_exe,
        env_name = env_name,
        methods = predict_args['methods'] ,
        epitope_len = predict_args['epitope_len'],
        dir_iedb = predict_args['iedb']
    shell:
        """
        echo ">>> processing {wildcards.sample}"
        set +u; source {params.activate} {params.env_name}; set -u
        pvacseq run \
        {input.vcf} \
        {wildcards.sample} \
        $(grep {wildcards.sample} {input.hla} | awk '{{print $2}}') \
        {params.methods} {output} \
        -e {params.epitope_len} \
        -a sample_name \
        -d 500 \
        --iedb-install-directory {params.dir_iedb} 
        echo ">>> done"
        """

def get_final_tsv(wildcards):
    if wildcards.method == "MHC_Class_I":
        return("neopip_output/neoantigen_calling/{wildcards.sample}/MHC_Class_I/{wildcards.sample}.final.tsv")
    elif wildcards.method == "MHC_Class_II":
        return("neopip_output/neoantigen_calling/{wildcards.sample}/MHC_Class_II/{wildcards.sample}.final.tsv")
    else:
        raise(ValueError("Unrecognized wildcard value for 'method': %s" % wildcards.method))

rule summary_neoantigen:
    input: get_final_tsv
    output: "neopip_output/neoantigen_list/{method}_{sample}.tsv"
    message: "> Copy neoantigen list to neopip_output/neoantigen_list"
    wildcard_constraints:
        method="(MHC_Class_I|MHC_Class_II)"
    shell:
        """
        echo ">>> processing {wildcards.sample}"
        cp {input} {output}
        echo ">>> done"
        """
