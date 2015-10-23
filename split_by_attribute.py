import os
import sys
import fiona
import getopt

def main(argv):
	"""
	Splits ESRI Shapefile by levels of specified attribute field and
	writes the result to the current working directory.

	Options:
	    - i <inputfile> => the name of the ESRI Shapefile to be split.
	    - a <attribute> => the name of the ESRI Shapefile's attribute field.
	    - s <suffix>    => optional filename suffix to add to the output files.

	"""

	# try locating command line arguments, raise exception if not found
	try:
		opts, args = getopt.getopt(argv, "hi:a:s:", ["ifile=", "attr=", "suffix="])
	except getopt.GetoptError:
		print 'split_by_feature.py -i <inputfile> -a <attribute> -s <file suffix>'
		sys.exit(2)

	# loop through command line arguments and assign to variables
	for opt, arg in opts:
		if opt == '-h':
			print 'split_by_feature.py -i <inputfile> -a <attribute> -s <file suffix>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-a", "--attr"):
			attr = arg
		elif opt in ("-s", "--suffix"):
			suffix = arg

	# open ESRI shapefile with fiona
	with fiona.open(inputfile, 'r') as layer1:
		# copy the input file schema
		schema = layer1.schema
		# loop through features in the input layer
		for feat in layer1:
			# capture current feature's attribute value
			value = feat['properties'][attr]
			# if the value is not none replace whitespace characters with underscores
			value = "_".join(value.split()) if value is not None else value
			# define name of split shapefile by current attribute value
			splitfile = os.path.join(os.getcwd(), "%s_%s.shp" % (value, suffix))
			# if split file exists append the current feature,
			# otherwise open a new file and write the current feature
			if os.path.isfile(splitfile):
				with fiona.open(splitfile, 'a', 'ESRI Shapefile', schema) as layer2:
					layer2.write(feat)
			else:
				with fiona.open(splitfile, 'w', 'ESRI Shapefile', schema) as layer2:
					layer2.write(feat)


# main function call
if __name__ == "__main__":
   main(sys.argv[1:])