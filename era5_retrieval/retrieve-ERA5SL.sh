#!/bin/bash
#SBATCH --job-name=vl_sl
#SBATCH --mail-type=NONE
#SBATCH --mail-user=Thorsten.Simon@uibk.ac.at
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --time=08:00:00
#SBATCH --output=__vlsl_%j.log

## ----------------------------------------------------------------------
## DESCRIPTION: * takes a ERA5 EU single level netcdf file and
##              * selects the Eastern Alps domain
## ----------------------------------------------------------------------

echo " ------------------------- "
date
hostname
pwd
whoami
echo " ------------------------- "

## inputs
## path and files
INPATH="/media/data/winter_lightning/ERA5-EU/single-level"
INPATHDV="/media/data/winter_lightning/ERA5-EU/derived-variables/annually"
OUTPATH="data/raw_data/ERA5"
TMPPATH="tmp-data-era"

for YEAR in {2009..2022}
do

	for MON in {1..12}
	do
	MONTH=`printf "%02d" $MON`

		while read line
		do

			## select domain sl
			echo " * Run cdo to select domain"
			IFILE=ERA5_sfc_${YEAR}_${line}.nc
			OFILE=ERA5_sfc_${YEAR}-${MONTH}_${line}.nc
			echo " * Processing ${OFILE}"
			cdo sellonlatbox,8.25,16.75,45.25,49.75 \
				-selmon,${MON} ${INPATH}/${line}/${IFILE} \
				${TMPPATH}/${OFILE}
			echo " --- "
		done < single_level_vars.txt

	cdo merge `ls ${TMPPATH}/ERA5_sfc_${YEAR}-${MONTH}_*nc` \
		${OUTPATH}/ERA5_sfc_${YEAR}-${MONTH}.nc
	done
done


echo " ------------------------- "
date
hostname
pwd
whoami
echo " ------------------------- "


