import sys
import fiona
import rtree
import getopt
from shapely.geometry import shape

def main(argv):
	"""
	Performs a spatial join of ESRI point and polygon shapefiles and writes
	the result to the current working directory. Points are joined to their
	bounding polygon by inspection using a spatial index. The output shapefile
	contains all points that have a bounding polygon with an additional attr-
	ibute column that captures the name of the bounding polygon.

	Options:
		- p <points>    => the name of the ESRI shapefile with the point layer
		- b <polygons>  => the name of the ESRI shapefile with the polygon layer
		- a <attribute> => the name of the polygon attribute to use for the join
		- o <outfile>   => the name of the output shapefile
	"""

	# try locating command line arguments, raise exception if not found
	try:
		opts, args = getopt.getopt(argv, "hp:b:a:o:", ["points=", "polys=", "attr=", "outfile="])
	except getopt.GetoptError:
		print 'join_points_in_poly.py -p <points> -b <polygons> -a <attribute> -o <outfile>'
		sys.exit(2)

	# loop through command line arguments and assign to variables
	for opt, arg in opts:
		if opt == '-h':
			print 'join_points_in_poly.py -p <points> -b <polygons> -a <attribute> -o <outfile>'
			sys.exit()
		elif opt in ("-p", "--points"):
			filename1 = arg
		elif opt in ("-b", "--polys"):
			filename2 = arg
		elif opt in ("-a", "--attr"):
			attr = arg
		elif opt in ("-o", "--outfile"):
			outfile = arg

	# open point and polygon layers
	with fiona.open(filename1, 'r') as layer1:
		with fiona.open(filename2, 'r') as layer2:
			# capture point layer schema and add column for polygon attribute
			schema = layer2.schema
			schema['properties'][attr] = 'str'
			# open the output file
			with fiona.open (outfile, 'w', 'ESRI Shapefile', schema) as shp_out:
				# create a spatial index of the polygons using rtree
				index = rtree.index.Index()
				for feat1 in layer1:
					fid = int(feat1['id'])
					geom1 = shape(feat1['geometry'])
					index.insert(fid, geom1.bounds)

				# loop through features in the point layer
				for feat2 in layer2:
					geom2 = shape(feat2['geometry'])
					for point in geom2:
						# loop through closest polygons
						for fid in index.intersection(point.coords[0]):
							if fid != int(feat2['id']):
								feat1 = layer1[fid]
								geom1 = shape(feat1['geometry'])
								# if point is within polygon add polygon attribute to point layer
								if geom2.within(geom1):
									feat2['properties'][attr] = feat1['properties']['Name']
									shp_out.write(feat2)




if __name__ == '__main__':
   main(sys.argv[1:])