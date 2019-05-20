# Use for simple test
import os
import glob

rule wilds:
    input: 
        #glob.glob("test/snakemake/*.txt")#expand("test/snakemake/{sample}", sample=os.path.base)
        expand("test/snakemake/{file}", file="test1.txt")
    shell:
        "echo yes {wildcards.file}"