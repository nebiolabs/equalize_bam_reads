__author__ = 'langhorst'

#determine snumber of reads in each file (using pysam to extract from idxstats)
#calculates ratios relative to smallest file
#calls sambamba to downsample

import sys
import pysam
import os
from subprocess import call
from distutils.spawn import find_executable


def get_num_reads(filename):
   reduce(lambda x, y: x + y, [ eval('+'.join(l.rstrip('\n').split('\t')[2:]) ) for l in pysam.idxstats(filename) ])

if not find_executable('sabamba'):
    sys.stederr.write("sambamba must be available on the path.")
    exit(1)


files_by_size = {file:get_num_reads(file) for file in sys.argv[1:] }

min_read_count = files_by_size.values().min()

smallest_file = (file for file,size in files_by_size.items() if size == min_read_count )[0]

files_by_frac = { file:(min_read_count/size) for file,size in files_by_size.items() if file != smallest_file }

for file, frac in files_by_frac.items:
    output_file = os.path.splitext(file)[0]  + ".even_cov.bam"
    call("sambamba view -t 8 -p -f bam -s %s %s -o %s" % frac, file, output_file)

os.symlink(smallest_file,os.path.splitext(smallest_file)[0]  + ".even_cov.bam") #smallest file needs no downsampling