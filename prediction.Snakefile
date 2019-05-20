configfile: "config.yaml"


import os
import sys
import glob
import re
import csv

from os.path import join, expanduser
from subprocess import run, PIPE
from utils import create_dir
from prepare import neopip_loc, vep_loc


# Global definition
if (config['input']['variants']['type']) == 'MAF':
    MAF = expanduser(config['input']['variants']['path'])
else:
    VCF = expanduser(config['input']['variants']['path'])
    VCF = glob.glob(VCF)

HLA = config['input']['hla']['path']

predict_methods = config['prediction_args']['argorithms']
predict_epitope_len = config['prediction_args']['epitope_len']

IEDB_PATH         = join(neopip_loc, 'iedb') 
VEP_PATH          = config['vep']['vep_path'] if config['vep']['vep_path'] is not None else 'vep'
VEP_PLUGIN_PATH   = config['vep']['plugin_path'] if config['vep']['plugin_path'] is not None else join(vep_loc, 'VEP_plugins') 
VEP_DATA_PATH     = config['vep']['cache_path'] if config['vep']['cache_path'] is not None else join(neopip_loc, 'vep')
VEP_CACHE_VERSION = config['vep']['cache_version']
VEP_ASSEMBLY_VERSION = config['vep']['assembly_version']

reference_fasta   = config['reference']['fasta']

# Output directories
dir_annotated = create_dir(config['output']['path'], 'neoantigen_calling', "vep_annotated_vcfs")


# Conda
conda_exe = os.environ['CONDA_EXE']
activate_exe = join(os.path.dirname(conda_exe), 'activate')
env_name = config['prepare']['conda']['env_name']

# If input variant file format is MAF
# extra steps are needed.
# rule maf2vcf:
#     input:
#         maf = MAF
#     output:
#         glob.glob(join(config['output']['path'], 'tumor_single_vcfs', "*.vcf"))
#     log: '/tmp/neopip_log/maf2vcf.log'
#     threads: config['threads']
#     run:
#         if not os.path.isfile(input.maf):
#             print("> Cannot find Maf file. Exiting...")
#             sys.exit(1)
#         print("> Maf file detected")
#         dir_pair_vcf = create_dir(config['output']['path'], 'tumor_normal_vcf_pair')
#         print("> Run maf2vcf.pl...")
#         cmds = """{maf2vcf} --input-maf {maffile} \
#                             --output-dir {output} \
#                             --ref-fasta {fasta}   \
#                             --per-tn-vcfs
#                """.format(maf2vcf=config['vcf2maf']['maf2vcf'], 
#                         maffile=input.maf,
#                         output=dir_pair_vcf, 
#                         fasta=reference_fasta)
#         run("source {0} {1} && {2}".format(activate_exe, env_name, cmds), check=True, shell=True)
#         #print(cmds)
#         print("> Output paired vcf files to %s" %dir_pair_vcf)
#         print("> Done.")
        
#         print("> Delete VCF column of normal sample...")
#         dir_tumor_vcf = create_dir(config['output']['path'], 'tumor_single_vcfs')
#         vcfs = glob.glob("%s/*_vs_*.vcf"%dir_pair_vcf)
#         # process vcf
#         for vcf in vcfs:
#             sample = re.sub(r'(.*)_vs.*', r'\1',os.path.basename(vcf))
#             print(">>> processing %s"%sample)
#             cmds = r"""cat {vcf} | \
#                       awk 'BEGIN{{FS="\t";OFS="\t"}}{{if($1 ~ /^##]/){{print $0}}else{{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}}}}' \
#                        > {dir}/{sample}.vcf
#                     """.format(vcf=vcf, dir=dir_tumor_vcf, sample=sample)
#             run(cmds, check=True, shell=True)
#         print("> Output tumor vcf files to %s" %dir_tumor_vcf)
#         print("> Done.")

rule vep_annotate:
    input:
        #join(os.path.dirname(VCF) if 'VCF' in globals() else join(config['output']['path'], 'tumor_single_vcfs'), "{sample}.vcf")
        "{dir_somatic_vcf}/{sample}.vcf"#join(config['output']['path'], 'tumor_single_vcfs', "{sample}.vcf")
        #"test/output/tumor_single_vcfs/CGLU290.vcf"
    output:
        join(dir_annotated, "{sample}.vcf")
    params:
        activate = activate_exe,
        env_name = env_name,
        vep = VEP_PATH,
        dir_plugin = VEP_PLUGIN_PATH,
        assembly_version = VEP_ASSEMBLY_VERSION, 
        fasta = reference_fasta,
        dir_cache = VEP_DATA_PATH, 
        cache_version = VEP_CACHE_VERSION,
        dir_annotated = dir_annotated,
    log: '/tmp/neopip_log/vep_annotate.log'
    threads: 1
    shell:
        """
        set +u; source {params.activate} {params.env_name}; set -u
        {params.vep} --input_file {input} --format vcf --output_file stdout \
             --vcf --symbol --terms SO --plugin Downstream --plugin Wildtype \
             --dir_plugins {params.dir_plugin} --assembly {params.assembly_version} --fasta {params.fasta} \
             --dir_cache {params.dir_cache} --offline --cache_version {params.cache_version} --pick --force_overwrite \
             > {output}
        """

# # This process samples one by one
# rule predict_neoantigen:
#     input:
#         vcfs = VCF if 'VCF' in globals() else glob.glob(join(config['output']['path'], 'tumor_single_vcfs', "*.vcf")),
#         hla_file = HLA
#     threads: config['threads']
#     run:
#         print("> Prepare annotating vcfs with VEP and predict neoantigens")
#         # process samples one by one
#         dir_annotated = create_dir(config['output']['path'], 'neoantigen_calling', "annotated_vcfs")
#         for vcf in vcfs:
#             sample = re.sub(r'(.*)_vs.*', r'\1',os.path.basename(vcf))
#             print(">>> processing %s"%sample)
#             print(">>> annotating with VEP...")
#             # Step 1: run VEP
#             cmds = """
#             {vep} --input_file {vcf} --format vcf --output_file stdout \
#              --vcf --symbol --terms SO --plugin Downstream --plugin Wildtype \
#              --dir_plugins {dir_plugin} --assembly {assembly_version} --fasta {fasta} \
#              --dir_cache {dir_cache} --offline --cache_version {cache_version} --pick --force_overwrite \
#              > {annotated_dir}/{sample}_annotated_filterd.vcf
#                 """.format(vep = VEP_PATH, vcf = vcf, dir_plugin = VEP_PLUGIN_PATH,
#                 assembly_version = VEP_ASSEMBLY_VERSION, fasta = reference_fasta,
#                 dir_cache = VEP_DATA_PATH, cache_version = VEP_CACHE_VERSION,
#                 dir_annotated = dir_annotated, sample = sample)
#             cmds = exeute([PY3.activate_cmd, cmds, PY3.deactivate_cmd], sep = ' && ')
#             print(">>> predicting neoantigens...")
#             # Step 2: run prediction softwares
#             # a directory can only store one sample result !!!!!!!!
#             dir_calling = create_dir(config['output']['path'], 'neoantigen_calling', sample)
#             #hla
#             with open(hla_file) as fd:
#                 rd = csv.reader(fd, delimiter="\t")
#             for row in rd:
#                 if row[0] == sample:
#                     hla = row[1]
#                     break
                
#             cmds = """
#                     pvacseq run \
#                     {dir_annotated}/{sample}_annotated_filterd.vcf \
#                     {sample} \
#                     {hla} \
#                     {methods} {dir_calling} \
#                     -e {epitope_len} \
#                     -a sample_name \
#                     -d 500 \
#                     --iedb-install-directory {path_iedb} 
#                     """.format(dir_annotated=dir_annotated, sample=sample,
#                     hla=hla,methods=predict_methods, epitope_len=predict_epitope_len, 
#                     path_iedb=IEDB_PATH)
#         print("> Done.")
