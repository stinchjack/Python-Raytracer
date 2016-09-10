import raytracer.shape
from raytracer.cartesian import *
import textwrap
# import raytracer.scene as scene


OCT_BRANCH_MIN_X = 0
OCT_BRANCH_MIN_Y = 0
OCT_BRANCH_MIN_Z = 0

OCT_BRANCH_MAX_X = 1
OCT_BRANCH_MAX_Y = 1
OCT_BRANCH_MAX_Z = 1

def list_add_unique(list, item):
    if item not in list:
        list.append(item)
    
    return list

def list_purge_duplicates(list):
    # http://stackoverflow.com/questions/6764909/python-how-to-remove-all-duplicate-items-from-a-list
    unique_X = []
    for i, row in enumerate(list):
        if row not in list[i + 1:]:
            unique_X.append(row)
    return unique_X

class BoundingBox:
    def __init__(self, min_x, max_x, min_y, max_y, min_z, max_z):
        self.min_x = min_x
        self.mid_x = (min_x + max_x) / 2.0
        self.max_x = max_x
        self.min_y = min_y
        self.mid_y = (min_y + max_y) / 2.0
        self.max_y = max_y
        self.min_z = min_z
        self.mid_z = (min_z + max_z) / 2.0
        self.max_z = max_z
        
        self.centre = ('cartesian', self.mid_x, self.mid_y, self.mid_z)
        
        self.coordinates = [
            ('cartesian', min_x, min_y, min_z),
            ('cartesian', min_x, min_y, max_z),
            ('cartesian', min_x, max_y, min_z),
            ('cartesian', min_x, max_y, max_z),
            ('cartesian', max_x, min_y, min_z),
            ('cartesian', max_x, min_y, max_z),
            ('cartesian', max_x, max_y, min_z),
            ('cartesian', max_x, max_y, max_z)]

    def is_inside(self, cartesian):
        return (cartesian[1]>=self.min_x and cartesian[1]<=self.max_x and
            cartesian[2]>=self.min_y and cartesian[2]<=self.max_y and
            cartesian[3]>=self.min_z and cartesian[3]<=self.max_z)

    def box_overlaps(self, bounding_box):
        for point in bounding_box.coordinates:
            if self.is_inside(point):
                return True
        return False
    
    def __str__(self):
        return ("min_x: %f, mid_x %f, max_x %f, min_y %f, mid_y %f " + 
                "max_y: %f, min_z: %f, mid_z: %f, max_z: %f, co-ords: %s") % (
                self.min_x, self.mid_x, self.max_x, self.min_y, self.mid_y,
                self.max_y, self.min_z, self.mid_z, self.max_z, self.coordinates )
                
            
class OctTreeNode(object):
    def __init__(
            self, parent_branch, split_threshold,
            min_x, max_x, min_y, max_y, min_z, max_z):
        self.margin = mpfr (".0001")
        self.parent_branch = parent_branch
        self.shapes = []
        self.split_threshold =  split_threshold
        self.bounding_box = BoundingBox(
            min_x, max_x, min_y, max_y, min_z, max_z)
        self.shape_count = 0
        self.__added_shapes__ = {}
          
    def can_split (self):   
        
        if hasattr(self.parent_branch, "shape_count"):
            if self.shape_count >= self.parent_branch.shape_count:
                return False
                
        return True 
 
    def __str__(self):
        str = "Count: %d\n", self.shape_count
        for shape in self.__added_shapes__:
            
                for tuple in self.__added_shapes__[shape]:
                    str = "%s id: %d child: (%d, %d, %d) \n" % (      
                        str, shape,
                            tuple[1],
                            tuple[2],
                            tuple[3])

        return str

    def get_shapes_by_ray(self, ray):
      return self.shapes

    def get_leaves_by_ray(self, ray):
      return None            

    def set_margin(self, margin):
        self.margin = mpfr (margin)

class OctTreeLeaf(OctTreeNode):
 
    def add_shape(self, new_shape):
            
        self.__added_shapes__[id(new_shape)] = None
        
        self.shape_count += 1
                
        
        self.shapes.append(new_shape)
        if len(self.shapes) > self.split_threshold and self.can_split():
            new_branch = OctTreeBranch(
                self.parent_branch, self.split_threshold,
                self.bounding_box.min_x, self.bounding_box.max_x,
                self.bounding_box.min_y, self.bounding_box.max_y,
                self.bounding_box.min_z, self.bounding_box.max_z)   
            
            new_branch.set_margin(self.margin)
                      
            for shape in self.shapes:
                new_branch.add_shape(shape)

            self.shapes = []
            
            if self.parent_branch is not None:
                if hasattr (self.parent_branch, 'replace_node'):
                    self.parent_branch.replace_node(self, new_branch)
                elif type(self.parent_branch) is dict and 'poymesh' in shape:

                    shape_polymesh_replace_octtree_node(
                        self.parent_branch, new_branch)

            return True

    def get_shape_dict_by_ray(self, ray):
        
        shapes = self.get_shapes_by_ray(ray)
        shape_dict = {}
        for shape in shapes:
            shape_box = raytracer.shape.shape_bounding_box(shape)
            
            if shape_box is not None:
                dist_sq = pow(ray[RAY_START][1]-shape_box.centre[1], 2) + \
                    pow(ray[RAY_START][2]-shape_box.centre[2], 2) + \
                    pow(ray[RAY_START][3]-shape_box.centre[3], 2)
            else:
                dist_sq = 0
                
            shape_dict[dist_sq] = shape
         
        return shape_dict
            

    def __str__(self):
        str = "OctTreeLeaf ID: %d "%id(self)
        str = str + " Bounding box: %s " % self.bounding_box.__str__()
        str = str + ",   Shapes: "
        if len(self.shapes)>0:
            for s in self.shapes:
                str = "%s%d \n" % (str, id(s) )
        else:
            str = str + "None! "
        
        return str
                

            
class OctTreeBranch(OctTreeNode):
    
    def __init__(
        self, parent_branch, split_threshold,
        min_x, max_x, min_y, max_y, min_z, max_z):
        super(OctTreeBranch, self).__init__(
            parent_branch, split_threshold,
            min_x, max_x, min_y, max_y, min_z, max_z)
        self.children = [
            [[None,None], [None, None]],
            [[None, None], [None, None]] ]
            
        x = [min_x, self.bounding_box.mid_x, max_x]
        y = [min_y, self.bounding_box.mid_y, max_y]
        z = [min_z, self.bounding_box.mid_z, max_z]
        
        for i in range(0,2):
            for j in range(0,2):
                for k in range(0,2):
                    self.children[i][j][k] = \
                        OctTreeLeaf(
                            self, split_threshold,
                            x[i], x[i + 1], 
                            y[j], y[j + 1],
                            z[k], z[k + 1])
        self.shape_count = 0 

    
    def ___str__(self):
        str = "-----------------------------------------------------------------------------------\n"
        for j in range(0,2):
            str = "%s| %s | %s |\n" % (str, self.str_break(self.children[0][j][0].__str__()),
                    self.str_break(self.children[1][j][0].__str__() ))
            str = "%s%s" % \
                (str, "-----------------------------------------------------------------------------------\n")
            
        str = "%s%s" % (str, "\n\n")

        for j in range(0,2):
            str = "%s| %s | %s |\n" % (str, self.str_break(self.children[0][j][1].__str__()), self.str_break(self.children[1][j][1].__str__() ))
            str = "%s%s" % (str, "-----------------------------------------------------------------------------------\n")
        
        str = "%sShapes added: %d %s" % (str, self.shape_count, "\n\n")    
            
        str = "%s%s" % (str, "\n\n")
        return str  

    def str_break(self, str, width=40):
        list = textwrap.wrap(str, width=width);
        str = ""
        list_p = []
        for line in list:
            list_p.append(line.ljust(width))

    def set_margin (self, margin):
        self.margin = mpfr(margin)
        for i in range(0,2):
            for j in range(0,2):
                for k in range(0,2):
                    self.children[i][j][k].set_margin(margin)        
            
    def add_shape (self, shape):
          
        self.__added_shapes__[id(shape)] = []  


        self.shape_count += 1        
        
        shape_box = raytracer.shape.shape_bounding_box(shape)

        if shape_box is None or not self.can_split():
            self.shapes.append(shape)
            # if stop: import pdb; pdb.set_trace()

        else:
            # if not shape_box.box_overlaps(self.bounding_box):
            #    
            #    print ("shape_box does not overlap")
            #    return False
            
            if shape_box.min_x <= self.bounding_box.mid_x:
                x_left = 0
            else:
                x_left = 1
            if shape_box.max_x <= self.bounding_box.mid_x:
                x_right = 0
            else:
                x_right = 1            
        
            if shape_box.min_y <= self.bounding_box.mid_y:
                y_top = 0
            else:
                y_top = 1
            if shape_box.max_y <= self.bounding_box.mid_y:
                y_bottom= 0
            else:
                y_bottom = 1
            
            if shape_box.min_z <= self.bounding_box.mid_z:
                z_front = 0
            else:
                z_front = 1
            if shape_box.max_z <= self.bounding_box.mid_z:
                z_back= 0
            else:
                z_back = 1 
            
            # if stop: import pdb; pdb.set_trace()
            for i in range(x_left, x_right + 1):
                for j in range(y_top, y_bottom + 1):
                    for k in range(z_front, z_back + 1):
                        
                        self.__added_shapes__[id(shape)].append (
                            (self.children[i][j][k], i, j, k))
                        
                        self.children[i][j][k].add_shape(shape)
                 
            return True
                 
            
    def replace_node(self, old_node, new_node):
        for i in range(0,2):
            for j in range(0,2):
                for k in range(0,2):                    
                    if self.children[i][j][k] == old_node:                        
                        self.children[i][j][k] = new_node
                        return True
        
        return False
    
    
    def get_shape_dict_by_ray(self, ray):
        shapes = self.get_shapes_by_ray(ray)
        shape_dict = {}
        
        if ray[RAY_ISSHADOW]:
            for shape in shapes:
                shape_box = raytracer.shape.shape_bounding_box(shape)
                
                if shape_box is not None:
                    dist_sq = pow(ray[RAY_START][1]-shape_box.centre[1], 2) + \
                        pow(ray[RAY_START][2]-shape_box.centre[2], 2) + \
                        pow(ray[RAY_START][3]-shape_box.centre[3], 2)
                else:
                    dist_sq = 0
                
                while dist_sq in shape_dict: #fixes keys being overwritten if distances are identical
                    dist_sq = dist_sq + .001 
                    
                shape_dict[dist_sq] = shape
             
            return shape_dict
        
        else:
            i = 0
            for shape in shapes:
                i = i + 1
                    
                shape_dict[i] = shape
             
        return shape_dict            
            
    
    def get_shapes_by_ray(self, ray):
        leaves = self.get_leaves_by_ray(ray)

        shapes = []
        for leaf in leaves:
            shapes += leaf.shapes

        shapes += self.shapes
        
        shapes = list_purge_duplicates(shapes)
                    
        return shapes

    def get_leaves_by_ray(self, ray):
        
        if ((ray[RAY_START][1]<self.bounding_box.min_x and ray[RAY_DIR][1]<0)
            or (ray[RAY_START][2]<self.bounding_box.min_y and ray[RAY_DIR][2]<0)
            or (ray[RAY_START][3]<self.bounding_box.min_z and ray[RAY_DIR][3]<0)            
            or (ray[RAY_START][1]>self.bounding_box.max_x and ray[RAY_DIR][1]>0)
            or (ray[RAY_START][2]>self.bounding_box.max_y and ray[RAY_DIR][2]>0)
            or (ray[RAY_START][3]>self.bounding_box.max_z and ray[RAY_DIR][3]>0)):
            
            return []
        
        t=[{}, {}, {}, {}]
        nodes = []
        if ray[RAY_DIR][1] !=0: # if not paralell to X-axis
            t[1]['min'] = (self.bounding_box.min_x - ray[RAY_START][1]) / ray[RAY_DIR][1]
            t[1]['mid'] = (self.bounding_box.mid_x - ray[RAY_START][1]) / ray[RAY_DIR][1]
            t[1]['max'] = (self.bounding_box.max_x - ray[RAY_START][1]) / ray[RAY_DIR][1]

        if ray[RAY_DIR][2] !=0: # if not paralell to Y-axis

            t[2]['min'] = (self.bounding_box.min_y - ray[RAY_START][2]) / ray[RAY_DIR][2]
            t[2]['mid'] = (self.bounding_box.mid_y - ray[RAY_START][2]) / ray[RAY_DIR][2]
            t[2]['max'] = (self.bounding_box.max_y - ray[RAY_START][2]) / ray[RAY_DIR][2]

        if ray[RAY_DIR][3] !=0: # if not paralell to Z-axis
            t[3]['min'] = (self.bounding_box.min_z - ray[RAY_START][3]) / ray[RAY_DIR][3]
            t[3]['mid'] = (self.bounding_box.mid_z - ray[RAY_START][3]) / ray[RAY_DIR][3]
            t[3]['max'] = (self.bounding_box.max_z - ray[RAY_START][3]) / ray[RAY_DIR][3]
        
        for dim in range (1, 4):
                
            for aspect in t[dim]:
                if (t[dim][aspect] < 0):
                    continue
                
                margin = self.margin
                    
                point = ray_calc_pt(ray, t[dim][aspect])
                
                if (point[1] - margin > self.bounding_box.max_x or
                    point[1] + margin < self.bounding_box.min_x or
                    point[2] - margin > self.bounding_box.max_y or
                    point[2] + margin < self.bounding_box.min_y or
                    point[3] - margin > self.bounding_box.max_z or
                    point[3] + margin < self.bounding_box.min_z):
                    continue
                
                
                if abs (point[1] - self.bounding_box.mid_x) < margin:
                    x = [0, 1]
                else:
                    if point[1] < self.bounding_box.mid_x:
                        x = [0]
                    else:
                        x = [1]
                        
                if abs (point[2] - self.bounding_box.mid_y) < margin:
                    y = [0, 1]
                else:
                    if point[2]<self.bounding_box.mid_y:
                        y = [0]
                    else:
                        y = [1]
                        
                if abs (point[3] - self.bounding_box.mid_z) < margin:
                    z = [0, 1]
                else:
                    if point[3]<self.bounding_box.mid_z:
                        z = [0]
                    else:
                        z = [1]                        
                
                for i in x:
                    for j in y:
                        for k in z:
                            
                            node = self.children[i][j][k]
                
                            if not node in nodes:
                                nodes.append(node)
    
        if len(nodes) == 0:
            return []
        
        leaves = []
        
        for node in nodes:
            if isinstance(node, OctTreeBranch):
                leaves += (node.get_leaves_by_ray(ray))
            else:
                leaves.append(node)
        
        return leaves
    