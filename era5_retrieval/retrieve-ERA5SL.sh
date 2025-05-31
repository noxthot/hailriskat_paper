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
INPATH="data/ERA5-EU/single-level"  				# path to single level data
OUTPATH="data/raw_data/ERA5"						# path to output data
TMPPATH="tmp"									    # path to temporary data

for YEAR in {2009..2022}
do
	for MON in {1..12}
	do
		MONTH=`printf "%02d" $MON`

		## select domain sl
		echo " * Run cdo to select domain"
		IFILE=ERA5_sfc_${YEAR}_convective_available_potential_energy.nc
		OFILE=ERA5_sfc_${YEAR}-${MONTH}_convective_available_potential_energy.nc
		echo " * Processing ${OFILE}"
		cdo sellonlatbox,8.25,16.75,45.25,49.75 \
			-selmon,${MON} ${INPATH}/convective_available_potential_energy/${IFILE} \
			${TMPPATH}/${OFILE}
		echo " --- "

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


