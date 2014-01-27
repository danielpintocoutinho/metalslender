from pandac.PandaModules import EggData, EggGroup, EggPolygon, EggVertexPool, Point3D, Vec3D

import math

class EggOctree(object):

	def build(self, input, cellSize, collide=False):
		destNode = EggData()
		destNode.setCoordinateSystem(input.getCoordinateSystem())
		
		snode = input.getFirstChild()
		while not isinstance(snode, EggGroup) and snode is not None:
			#destNode.addChild(snode)
			snode = input.getNextChild()
		
		snode.triangulatePolygons(0xff)
		
		# First, extract the <VertexPool>
		vpool = snode.getFirstChild()
		while not isinstance(vpool, EggVertexPool):
			vpool = snode.getNextChild()
		
		# Loop on the vertices determine the bounding box
		minBB = Point3D()
		maxBB = Point3D()
		
		for vertex in vpool:
			vtxPos = vertex.getPos3()
			
			# Sets the X, Y or Z components
			i = 0
			for setter in [Point3D.setX, Point3D.setY, Point3D.setZ]  :
				if vtxPos[i] < minBB[i] :
					setter(minBB, vtxPos[i])
				
				if vtxPos[i] > maxBB[i] :
					setter(maxBB, vtxPos[i])
				i += 1
		
		minBB -= Vec3D(0.001, 0.001, 0.001)
		maxBB += Vec3D(0.001, 0.001, 0.001)
		
		# Number of leaves x,y,z
		bboxSize = maxBB - minBB
		self.ncx = int(math.ceil(bboxSize.getX() / cellSize.getX()))
		self.ncy = int(math.ceil(bboxSize.getY() / cellSize.getY()))
		self.ncz = int(math.ceil(bboxSize.getZ() / cellSize.getZ()))
		
		# Depth of the tree x,y,z
		self.depthX = math.ceil(math.log(self.ncx) / math.log(2))
		self.depthY = math.ceil(math.log(self.ncy) / math.log(2))
		self.depthZ = math.ceil(math.log(self.ncz) / math.log(2))
		self.depth = max(self.depthX, self.depthY, self.depthZ)
		
		self.cells = [[[
				{'min':
					Point3D(minBB.getX() + x * cellSize.getX(),
							minBB.getY() + y * cellSize.getY(),
							minBB.getZ() + z * cellSize.getZ()),
				'max':
					Point3D(minBB.getX() + (x+1) * cellSize.getX(),
							minBB.getY() + (y+1) * cellSize.getY(),
							minBB.getZ() + (z+1) * cellSize.getZ()),
				'group':EggGroup('leaf_%d_%d_%d' % (x,y,z)) }
				
				for z in range(self.ncz)]
				for y in range(self.ncy)]
				for x in range(self.ncx)]
		
		print 'Cell grid is %dx%dx%d' % (len(self.cells), len(self.cells[0]), len(self.cells[0][0]))
		
		if collide :
			for x in range(self.ncx) :
				for y in range(self.ncy) :
					for z in range(self.ncz) :
						self.cells[x][y][z]['group'].addObjectType('barrier')
		
		# Iterate on the <Polygon>s (should be triangles)
		poly = snode.getNextChild()
		while poly != None :
			if isinstance(poly, EggPolygon) :
				
				# Get the triangle center
				polyCenter = Point3D(0,0,0)
				for i in range(3) :
					polyCenter += poly.getVertex(i).getPos3()
				polyCenter /= 3.0
				
				# Add the triangle to the corresponding cell group
				cx = int(math.floor((polyCenter.getX()-minBB.getX()) / cellSize.getX()))
				cy = int(math.floor((polyCenter.getY()-minBB.getY()) / cellSize.getY()))
				cz = int(math.floor((polyCenter.getZ()-minBB.getZ()) / cellSize.getZ()))
				
				self.cells[cx][cy][cz]['group'].addChild(poly)
				
			poly = snode.getNextChild()
		
		# Add the vertex data
		destNode.addChild(vpool)
		
		self.nleaves = self.recur(destNode, 0, 0,0,0)
		
		print self.nleaves, 'leaves added'
		
		return destNode

	def recur(self, node, depth, x, y, z) :
		
		if depth < self.depth :
			nnode = EggGroup('')
			delt = int(math.pow(2, self.depth - depth - 1))
			
			nchilds = 0
			
			nchilds += self.recur(nnode, depth+1, x, y, z)
			nchilds += self.recur(nnode, depth+1, x + delt, y, z)
			nchilds += self.recur(nnode, depth+1, x, y + delt, z)		  
			nchilds += self.recur(nnode, depth+1, x + delt, y + delt, z)
			
			nchilds += self.recur(nnode, depth+1, x, y, z + delt)
			nchilds += self.recur(nnode, depth+1, x + delt, y, z + delt)
			nchilds += self.recur(nnode, depth+1, x, y + delt, z + delt)
			nchilds += self.recur(nnode, depth+1, x + delt, y + delt, z + delt)
			
			if nchilds > 0 :
				node.addChild(nnode)
			
			return nchilds
		
		else :
			
			# We are in a leaf
			if x < self.ncx and y < self.ncy and z < self.ncz :
				node.addChild(self.cells[x][y][z]['group'])
				return 1
			else :
				return 0
