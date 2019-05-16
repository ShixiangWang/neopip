# neopip - a neoantigen prediction workflow

Tools: snakemake + docker + singularity + conda

reference: https://github.com/ShixiangWang/Variants2Neoantigen

## Dependencies

Following tools are needed before using **neopip**:

- Python 3
- tcsh 
- gawk
- wget

```
"This package installs only the variant effect predictor (VEP) library\ncode. To install data libraries, you can use the 'vep_install' command\ninstalled along with it. For example, to install the VEP library for human\nGRCh38 to a directory\n\nvep_install -a cf -s homo_sapiens -y GRCh38 -c /output/path/to/GRCh38/vep --CONVERT\n\n(note that vep_install is renamed from INSTALL.pl\n to avoid having generic script names in the PATH)\n\nThe --CONVERT flag is not required but improves lookup speeds during\nruns. See the VEP documentation for more details\n\nhttp://www.ensembl.org/info/docs/tools/vep/script/vep_cache.html\n"                                                                                                                         | b"This package installs only the variant effect predictor (VEP) library\ncode. To install data libraries, you can use the 'vep_install.pl' command\ninstalled along with it. For example, to install the VEP library for human\nhg19/GRCh37 to a directory:\n\nvep_install.pl -a cf -s homo_sapiens -y GRCh37 -c /output/path/to/hg19/vep\nvep_convert_cache.pl -species homo_sapiens -version 86_GRCh37 -d /output/path/to/hg19/vep\n\n(note that vep_install.pl is renamed from INSTALL.pl\n and vep_convert_cache.pl from covert_cache.pl\n to avoid having generic script names in the PATH)\n\nThe convert cache step is not required but improves lookup speeds during\nruns. See the VEP documentation for more details:\n\nhttp://useast.ensembl.org/info/docs/tools/vep/script/vep_cache.html\n"                                                                                                                                                       done

```