#!/usr/bin/ppython

from pandac.PandaModules import EggData, Filename, Vec3D
from octree import EggOctree

from sys import argv, exit

if len(argv) < 6:
	print 'Usage: % <input.egg> <x,y,z> <render.egg> <x,y,z> <collision.egg>' % (argv[1],)
	exit(1)
	
print 'Reading input file %s' % (argv[1],)
input = EggData()
input.read(Filename(argv[1]))

try:
	resol = argv[2].split(',')
	resol = Vec3D(float(resol[0]), float(resol[1]), float(resol[2]))

	print 'Building render octree'
	output = EggOctree().build(input, resol, False)

	print 'Writing %s' % (argv[3],)
	output.writeEgg(Filename(argv[3]))
except AssertionError:
	pass

try:
	resol = argv[4].split(',')
	resol = Vec3D(float(resol[0]), float(resol[1]), float(resol[2]))

	print 'Building collision octree'
	output = EggOctree().build(input, resol, True)

	print 'Writing %s' % (argv[5],)
	output.writeEgg(Filename(argv[5]))
except AssertionError:
	pass

print 'Done'
