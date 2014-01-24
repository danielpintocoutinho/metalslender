#!/usr/bin/ppython

from pandac.PandaModules import EggData, Filename, Vec3D
from octree import EggOctree

from sys import argv, exit

if len(argv) < 4:
	print 'Usage: %s <input.input> <x,y,z> <output.input>' % (argv[1],)
	exit(1)
	
print 'Reading input file %s' % (argv[1],)
input = EggData()
input.read(Filename(argv[1]))
# sourceNode = toplevel.getFirstChild()
# print type(toplevel)
# print type(sourceNode)

output = EggData()
output.setCoordinateSystem(input.getCoordinateSystem())

resol = argv[2].split(',')
resol = Vec3D(float(resol[0]), float(resol[1]), float(resol[2]))

print 'Building octree'
EggOctree().build(input, output, resol, True)

print 'Writing output file %s' % (argv[3],)
output.writeEgg(Filename(argv[3]))

print 'Done'