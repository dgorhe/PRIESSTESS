#!/bin/bash

# -e = exit as soon as there is an error
# -u = exit if a program tries to use a variable that isn't set
# -x = print out each command before it runs, helpful for debugging
# -o pipefail = exit if something fails in a piped operation (i.e. command_1 | command_2 ...)
set -euo pipefail

# Specify the target protein (passed as first argument)
if [ -z "${1:-}" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: $0 <TARGET>"
    echo "Example: $0 RBFOX2"
    [ "$1" = "-h" ] || [ "$1" = "--help" ] && exit 0 || exit 1
fi
TARGET="$1"

# Create directories for data files
mkdir -p bams beds sequences

# Path to BAM file (indexed with samtools index)
# Reads intersecting bed regions (foreground) and flanking regions (background) will be extracted
BAM="bams/${TARGET}.bam"

# Download the BAM file if not already present
if [ ! -f "${BAM}" ]; then
    echo "Downloading ${BAM} ..."
    curl -L -o "${BAM}" "https://spidr-k562-data.s3.amazonaws.com/bams/SPIDR_COMBINED/${TARGET}.bam"
fi

# Length of each contig (i.e. chromosome) in a 2 column tab-delimited table
CONTIG_LENGTHS="all_contigs.lengths"

# Absolute path to the bed file
# RBFOX2 has canonical UGCAUG motif so we can use it as a positive control to determine if we're using PRIESSTESS correctly
BED="beds/${TARGET}.bed"

if [ ! -f "${BED}" ]; then
    echo "Downloading ${BED} ..."
    curl -L -o "${BED}" "https://spidr-submission.s3.us-east-1.amazonaws.com/beds_filtered/SPIDR_COMBINED/${TARGET}.bed"
fi

# Intermediate file which will contain the foreground sequences
FOREGROUND_SEQUENCES="sequences/${TARGET}.foreground.txt"

# Intermediate file which will contain the background sequences
BACKGROUND_SEQUENCES="sequences/${TARGET}.background.txt"

# Index the BAM if the index does not exist
if [ ! -f "${BAM}.bai" ] && [ ! -f "${BAM%.bam}.bai" ]; then
    samtools index ${BAM}
fi

# Foreground: extract reads from BAM that intersect with bed regions
# Each read is one line; deduplicate by read ID since a read may overlap multiple regions
samtools view -L ${BED} ${BAM} | awk 'NF>=10 && !seen[$1]++ {print $10}' | tr '[:lower:]' '[:upper:]' | tr 'T' 'U' >${FOREGROUND_SEQUENCES}

# Background: create flanking regions around each bed interval, then extract reads from BAM
# that intersect with those flanking regions (reads in flanking regions, not reference sequence)
# Exclude reads that also appear in foreground (e.g. reads spanning region boundaries)
FLANKING_BED="beds/${TARGET}.flanking.bed"
# Get all unique read IDs from foreground (overlapping BED), used to avoid selecting same reads for background
samtools view -L "${BED}" "${BAM}" |
    awk 'NF>=10 {print $1}' |
    sort -u \
        >sequences/fg_read_ids.tmp

# Create flanking regions (+/- 500 nt) around each BED interval
bedtools flank \
    -b 500 \
    -i "${BED}" \
    -g "${CONTIG_LENGTHS}" \
    -s \
    >"${FLANKING_BED}"

# Extract background sequences:
#  - Intersect BAM with flanking regions;
#  - For each read, print ID and sequence
#  - Remove any read ID seen in the foreground;
#  - Deduplicate sequences by read ID
#  - Convert to uppercase and replace T with U
samtools view -L "${FLANKING_BED}" "${BAM}" |
    awk 'NF>=10 {print $1"\t"$10}' |
    awk 'NR==FNR{fg[$1]=1;next} !($1 in fg) && !seen[$1]++ {print $2}' sequences/fg_read_ids.tmp - |
    tr '[:lower:]' '[:upper:]' |
    tr 'T' 'U' >"${BACKGROUND_SEQUENCES}"
rm -f ${FLANKING_BED} sequences/fg_read_ids.tmp

# Create outputs directory structure
OUTPUT_DIR="outputs/${TARGET}"
# Not sure if this logic is idempotent
rm -rf "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

# Actual PRIESSTESS command
# Use -alph 1,2,3,4,5,6 to skip struct-7 (slowest alphabet) if it hangs
PRIESSTESS \
    -fg ${FOREGROUND_SEQUENCES} \
    -bg ${BACKGROUND_SEQUENCES} \
    -o ${OUTPUT_DIR}

# Helpful to put a command like this to know if the last program is "hung up" on something
echo "Done!"
