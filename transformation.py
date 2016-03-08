import gmpy2
from gmpy2 import *
from matrix import *
from cartesian import *
from copy import *	

def transform_matrix_mul_cartesian(matrix, cartesian):
	return ('cartesian',(matrix[0][0]*cartesian[1])+(matrix[0][1]*cartesian[2])+(matrix[0][2]*cartesian[3]),
						(matrix[1][0]*cartesian[1])+(matrix[1][1]*cartesian[2])+(matrix[1][2]*cartesian[3]),
						(matrix[2][0]*cartesian[1])+(matrix[2][1]*cartesian[2])+(matrix[2][2]*cartesian[3]))
	
class Transform:
	#__matrix = None
	__options = {}
	#__noTransform = True
	#__inverseMatrix = None
	
	def __str__(self):
		return "{noTransform: %s options: %s matrix: %s inverseMatrix: %s}"%(self.__noTransform, self.__options, self.__matrix, self.__inverseMatrix)
	
	def __init__(self, options):
		self.setOptions(options)
	
	def noTransform(self):
		return self.__noTransform
	
	def matrix(self):
		return self.__matrix
	
	def options(self):
		self.__matrix == None
		return self.__options
		
	def setOptions(self, options):
		self.__options = options
		scalematrix = None
		rotatematrix  = None
		translatematrix = None
		__inverseMatrix = None
		if 'translate' in options:
			if not 'cartesian' in options['translate']:
				options['translate'] = cartesian_create(mpfr(options['translate']['x']), mpfr(options['translate']['y']), mpfr(options['translate']['z']))
			

		if  not 'scale' in options and not 'translate' in options and not 'rotate' in options:
			self.__matrix=Matrix()
			self.__noTransform = True
			return
		else:
			self.__noTransform = False
		
		if 'scale' in options:
			scalematrix = ScaleMatrix(1.0/mpfr(options['scale']['x']),mpfr(1.0/options['scale']['y']), 1.0/mpfr(options['scale']['z']))
		if 'rotate' in options:
			vector = cartesian_normalise(options['rotate']['vector'])
			rotatematrix = RotationMatrix(vector, mpfr(options['rotate']['angle']))
					
		

		if rotatematrix!=None and scalematrix==None:
			self.__matrix =  rotatematrix
			self.__inverseMatrix = rotatematrix.inversed()
		elif  scalematrix!=None and rotatematrix!=None:
			self.__matrix =  scalematrix * rotatematrix 
			self.__inverseMatrix = self.__matrix.inversed() #deepcopy(rotatematrix.inversed()) #* deepcopy(scalematrix.inversed())
		elif scalematrix!=None and rotatematrix==None:
			self.__matrix =  scalematrix
			self.__inverseMatrix = scalematrix.inversed()
		else:
			self.__matrix = Matrix()
			self.__inverseMatrix = Matrix()
			
		#if  rotatematrix!=None:
		#	print ("rotatematrix.matrix:")
		#	print (rotatematrix.matrix)
		#if  scalematrix!=None:
		#	print ("scalematrix.matrix:")
		#	print (scalematrix.matrix)
		#print ("self.__matrix.matrix")
		#print (self.__matrix.matrix)
		#print ("self.__inverseMatrix.matrix")
		#print (self.__inverseMatrix.matrix)
		#print()
		#print()
			
			
			
			
	def zztransform(self, ray):

		
		if self.__noTransform: return ray
		ray_dir=ray[RAY_VECTOR]
		if 'translate' in self.__options:					
			ray_point = cartesian_sub (ray[RAY_START],self.__options['translate'])
			ray_dir=ray[RAY_VECTOR]
		else:
			ray_point =ray[RAY_START]
		

		if isinstance(self.__matrix, Matrix) and ('scale' in self.__options or 'rotate' in self.__options):
			return ('ray', transform_matrix_mul_cartesian(self.__matrix.matrix, ray_dir),
					transform_matrix_mul_cartesian(self.__matrix.matrix, ray_point),
					ray[RAY_ISSHADOW])

		return ('ray', ray_point, ray_dir, ray[RAY_ISSHADOW])
	def transform(self, ray):

		if self.__noTransform: return ray
		
		ray_dir = ray[RAY_VECTOR]
		ray_point = ray[RAY_START]

		if 'translate' in self.__options:					
			ray_point = cartesian_sub (ray_point,self.__options['translate'])

		if isinstance(self.__matrix, Matrix):
			ray_dir= transform_matrix_mul_cartesian(self.__matrix.matrix, ray_dir)
			ray_point = transform_matrix_mul_cartesian(self.__matrix.matrix, ray_point)
		return ray_create(ray_point, ray_dir, ray[RAY_ISSHADOW])
	def transformPoint(self, point, inverse=False):
	
		if 'translate' in self.__options:		
			if inverse:	
				return cartesian_add(point,self.__options['translate'])
			else:
				return cartesian_sub(point,self.__options['translate'])
			


	def inverseTransform(self, normal, translate=False):

		if self.__noTransform: return normal

		if self.__inverseMatrix != None:
			normal = (self.__inverseMatrix*(normal))
			#ray_point = transform_matrix_mul_cartesian(self.__inverseMatrix.matrix, n)
			
		if translate and 'translate' in self.__options:	
			return cartesian_add(normal,self.__options['translate'])
			
		#print (result)
		return normal

		



TRANSFORM_OPTIONS=1
TRANSFORM_MATRIX=2
TRANSFORM_INVERSEMATRIX=3
TRANSFORM_NOTRANSFORM=4
		
def transform_setOptions(transform, options):
	transform[1] = options
	scalematrix = None
	rotatematrix  = None
	translatematrix = None
	__inverseMatrix = None
	
	#one= mpfr(1.0)
	if 'translate' in options:
		if not 'cartesian' in options['translate']:
			options['translate'] = cartesian_create(options['translate']['x'], options['translate']['y'], options['translate']['z'])
		
	if 'scale' in options:
		scalematrix = ScaleMatrix(1.0/options['scale']['x'], 1.0/options['scale']['y'], 1.0/options['scale']['z'])
	if 'rotate' in options:
		vector = cartesian_normalise(options['rotate']['vector'])
		rotatematrix = RotationMatrix(vector, options['rotate']['angle'])
		
	if scalematrix ==None and not 'translate' in options and rotatematrix==None:
		transform[TRANSFORM_MATRIX]=Matrix()
		transform[TRANSFORM_NOTRANSFORM] = True
		return
	else:
		transform[TRANSFORM_NOTRANSFORM] = False

	transform[TRANSFORM_MATRIX] = Matrix()
	transform[TRANSFORM_INVERSEMATRIX] = Matrix()
	if rotatematrix!=None and scalematrix==None:
		transform[TRANSFORM_MATRIX] =  rotatematrix
		transform[TRANSFORM_INVERSEMATRIX] = rotatematrix.inversed()
	elif  scalematrix!=None and rotatematrix!=None:
		transform[TRANSFORM_MATRIX] =  scalematrix * rotatematrix 
		transform[TRANSFORM_INVERSEMATRIX] = transform[TRANSFORM_MATRIX].inversed() #deepcopy(rotatematrix.inversed()) #* deepcopy(scalematrix.inversed())
	elif scalematrix!=None and rotatematrix==None:
		transform[TRANSFORM_MATRIX] =  scalematrix
		transform[TRANSFORM_INVERSEMATRIX] = scalematrix.inversed()
	

	#if  rotatematrix!=None:
	#	print ("rotatematrix.matrix:")
	#	print (rotatematrix.matrix)
	#if  scalematrix!=None:
	#	print ("scalematrix.matrix:")
	#	print (scalematrix.matrix)
	#print ("self.__matrix.matrix")
	#print (self.__matrix.matrix)
	#print ("self.__inverseMatrix.matrix")
	#print (self.__inverseMatrix.matrix)
	#print()
	#print()


TRANSFORM_OPTIONS=1
TRANSFORM_MATRIX=2
TRANSFORM_INVERSEMATRIX=3
TRANSFORM_NOTRANSFORM=4
		
def transform_setOptions(transform, options):
	transform[1] = options
	scalematrix = None
	rotatematrix  = None
	translatematrix = None
	__inverseMatrix = None
	
	#one= mpfr(1.0)
	if 'translate' in options:
		if not 'cartesian' in options['translate']:
			options['translate'] = cartesian_create(options['translate']['x'], options['translate']['y'], options['translate']['z'])
		
	if 'scale' in options:
		scalematrix = ScaleMatrix(1.0/options['scale']['x'], 1.0/options['scale']['y'], 1.0/options['scale']['z'])
	if 'rotate' in options:
		vector = cartesian_normalise(options['rotate']['vector'])
		rotatematrix = RotationMatrix(vector, options['rotate']['angle'])
		
	if scalematrix ==None and not 'translate' in options and rotatematrix==None:
		transform[TRANSFORM_MATRIX]=Matrix()
		transform[TRANSFORM_NOTRANSFORM] = True
		return
	else:
		transform[TRANSFORM_NOTRANSFORM] = False

	transform[TRANSFORM_MATRIX] = Matrix()
	transform[TRANSFORM_INVERSEMATRIX] = Matrix()
	if rotatematrix!=None and scalematrix==None:
		transform[TRANSFORM_MATRIX] =  rotatematrix
		transform[TRANSFORM_INVERSEMATRIX] = rotatematrix.inversed()
	elif  scalematrix!=None and rotatematrix!=None:
		transform[TRANSFORM_MATRIX] =  scalematrix * rotatematrix 
		transform[TRANSFORM_INVERSEMATRIX] = transform[TRANSFORM_MATRIX].inversed() #deepcopy(rotatematrix.inversed()) #* deepcopy(scalematrix.inversed())
	elif scalematrix!=None and rotatematrix==None:
		transform[TRANSFORM_MATRIX] =  scalematrix
		transform[TRANSFORM_INVERSEMATRIX] = scalematrix.inversed()
	

	#if  rotatematrix!=None:
	#	print ("rotatematrix.matrix:")
	#	print (rotatematrix.matrix)
	#if  scalematrix!=None:
	#	print ("scalematrix.matrix:")
	#	print (scalematrix.matrix)
	#print ("self.__matrix.matrix")
	#print (self.__matrix.matrix)
	#print ("self.__inverseMatrix.matrix")
	#print (self.__inverseMatrix.matrix)
	#print()
	#print()
			

def transform_create(options):
	transform = ['transform', options, None, None, None, None]
	transform_setOptions(transform, options)
	return transform
	
def transform_transform(transform, ray):
	if transform[TRANSFORM_NOTRANSFORM]: return ray
	
	ray_dir = cartesian_copy(ray[RAY_VECTOR])
	ray_point = cartesian_copy(ray[RAY_START])

	if 'translate' in transform[TRANSFORM_OPTIONS]:					
		ray_point = cartesian_sub (ray_point,transform[TRANSFORM_OPTIONS]['translate'])
	if isinstance(transform[TRANSFORM_MATRIX], Matrix):
		ray_dir = transform[TRANSFORM_MATRIX]*ray_dir
		ray_point = transform[TRANSFORM_MATRIX]*ray_point
	return ray_create(ray_dir, ray_point, ray[RAY_ISSHADOW])

def transform_transformPoint(transform, point, inverse=False):
	
	if 'translate' in transform[TRANSFORM_OPTIONS]:		
		if inverse:	
			return cartesian_add(point,transform[TRANSFORM_OPTIONS]['translate'])
		else:
			return cartesian_sub(point,transform[TRANSFORM_OPTIONS]['translate'])
			
def transform_inverseTransform(transform, normal, translate=False):

	if transform[TRANSFORM_NOTRANSFORM]: return normal

	if transform[TRANSFORM_INVERSEMATRIX] != None:
		normal = transform[TRANSFORM_INVERSEMATRIX]*(normal)

	if translate and 'translate' in transform[TRANSFORM_OPTIONS]:	
		return cartesian_add(normal,transform[TRANSFORM_OPTIONS]['translate'])
		
	#print (result)
	return normal