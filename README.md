# neopip - a neoantigen prediction workflow

Tools: snakemake + docker + singularity + conda?

reference: https://github.com/ShixiangWang/Variants2Neoantigen

## Dependencies

Following tools are needed before using **neopip**:

- bash
- git
- Python 3
  -  yaml
  -  csv
  -  snakemake >=5.4
- tcsh 
- gawk
- wget

After prepare neoantigen predicton softwares, download necessary data libraries.

```
This package installs only the variant effect predictor (VEP) library code. 
To install data libraries, you can use the 'vep_install' command installed along with it.

For example, to install the VEP library for human GRCh38 to a directory

    vep_install -a cf -s homo_sapiens -y GRCh38 -c /output/path/to/GRCh38/vep --CONVERT

To install the VEP library for human hg19/GRCh37 to a directory:

    vep_install.pl -a cf -s homo_sapiens -y GRCh37 -c /output/path/to/hg19/vep
    vep_convert_cache.pl -species homo_sapiens -version 86_GRCh37 -d /output/path/to/hg19/vep

(note that vep_install is renamed from INSTALL.pl to avoid having generic script names in the PATH)
The --CONVERT flag is not required but improves lookup speeds during runs. 

See the VEP documentation for more details\n\nhttp://www.ensembl.org/info/docs/tools/vep/script/vep_cache.html\n"                                                                 
```

Use 

```
vep_install -a cf -s homo_sapiens -y GRCh37 -c $HOME/.vep –CONVERT
```

Test vcf2maf and maf2vcf, maf2maf seems has problem

```
perl vcf2maf.pl --input-vcf tests/test.vcf --output-maf tests/test.vep.maf --vep-path /public/data/.neopip/miniconda/share/ensembl-vep-96.0-0/ --vep-data /public/data/.neopip/vep/ --ref-fasta /public/data/.neopip/vep/homo_sapiens/91_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa --filter-vcf 0 --cache-version 91

perl maf2vcf.pl --input-maf tests/test.maf --output-dir test_maf2vcf  --ref-fasta /public/data/.neopip/vep/homo_sapiens/91_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa --per-tn-vcfs
```


conda activate to source activate

```
/public/data/.neopip/miniconda/envs/neopip/lib/python3.7/site-packages/lib/prediction_class.py
/public/data/.neopip/miniconda/envs/neopip/lib/python3.7/site-packages/lib/call_iedb.py
```

run snakemake with `--cores 4`