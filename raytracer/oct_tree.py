from raytracer.cartesian import *
from raytracer.shape import *

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
        if row not in X[i + 1:]:
            unique_X.append(row)
    return unique_X

class BoundingBox:
    def __init__(min_x, max_x, min_y, max_y, min_z, max_z):
        self.min_x = min_x
        self.mid_x = (min_x + max_x) / 2.0
        self.max_x = max_x
        self.min_y = min_y
        self.mid_x = (min_y + max_y) / 2.0
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
        
            
class OctTreeNode(object):
    def __init__(
            self, parent_branch, split_threshold,
            min_x, max_x, min_y, max_y, min_z, max_z):
        self.parent_branch = parent_branch
        self.shapes = []
        self.split_threshold =  split_threshold
        self.bounding_box = BoundingBox(
            min_x, max_x, min_y, max_y, min_z, max_z)   
            
class OctTreeLeaf(OctTreeNode): 
    def add_shape(self, shape):
        self.shapes.append(shape)
        if len(self.shapes)>self.split_threshold:  
            new_branch = OctTreeBranch(
                self.parent_branch, self.split_threshold,
                self.bounding_box.min_x, self.bounding_box.max_x,
                self.bounding_box.min_y, self.bounding_box.max_y,
                self.bounding_box.min_z, self.bounding_box.max_z)
                
            for shape in self.shapes:
                new_branch.add_shape(shape)
            
            del self.shapes[:]
            
            if self.parent_branch is not None:
                self.parent_branch.replace_node(self, new_branch)

            
class OctTreeBranch(OctTreeNode):
    def __init__(
        self, parent_branch, split_threshold,
        min_x, max_x, min_y, max_y, min_z, max_z):
        super.__init__(
            parent_branch, split_threshold,
            min_x, max_x, min_y, max_y, min_z, max_z)
        self.chlidren = [
            [[None,None], [None, None]],
            [[None, None], [None, None]] ]
        
        self.children[OCT_BRANCH_MIN_X][OCT_BRANCH_MIN_Y][OCT_BRANCH_MIN_Z] = \
            OctTreeLeaf(
                split_threshold, min_x, self.bounding_box.mid_x, 
                min_y, self.bounding_box.mid_y,
                min_z, self.bounding_box.mid_z)
        
        self.children[OCT_BRANCH_MIN_X][OCT_BRANCH_MIN_Y][OCT_BRANCH_MAX_Z] = \
            OctTreeLeaf(
                split_threshold, min_x, self.bounding_box.mid_x, 
                min_y, self.bounding_box.mid_y,
                self.bounding_box.mid_z, max_z)
                
        self.children[OCT_BRANCH_MIN_X][OCT_BRANCH_MIN_Y][OCT_BRANCH_MIN_Z] = \
            OctTreeLeaf(
                split_threshold, min_x, self.bounding_box.mid_x, 
                min_y, self.bounding_box.mid_y,
                min_z, self.bounding_box.mid_z)
        
        self.children[OCT_BRANCH_MIN_X][OCT_BRANCH_MAX_Y][OCT_BRANCH_MAX_Z] = \
            OctTreeLeaf(
                split_threshold, min_x, self.bounding_box.mid_x, 
                self.bounding_box.mid_y, max_y,
                self.bounding_box.mid_z, max_z)

        self.children[OCT_BRANCH_MAX_X][OCT_BRANCH_MIN_Y][OCT_BRANCH_MIN_Z] = \
            OctTreeLeaf(
                split_threshold, min_x, self.bounding_box.mid_x, 
                min_y, self.bounding_box.mid_y,
                min_z, self.bounding_box.mid_z)
        
        self.children[OCT_BRANCH_MAX_X][OCT_BRANCH_MIN_Y][OCT_BRANCH_MAX_Z] = \
            OctTreeLeaf(
                split_threshold, self.bounding_box.mid_x, max_x, 
                min_y, self.bounding_box.mid_y,
                self.bounding_box.mid_z, max_z)
                
        self.children[OCT_BRANCH_MAX_X][OCT_BRANCH_MIN_Y][OCT_BRANCH_MIN_Z] = \
            OctTreeLeaf(
                split_threshold, self.bounding_box.mid_x, max_x,
                min_y, self.bounding_box.mid_y,
                min_z, self.bounding_box.mid_z)
        
        self.children[OCT_BRANCH_MAX_X][OCT_BRANCH_MAX_Y][OCT_BRANCH_MAX_Z] = \
            OctTreeLeaf(
                split_threshold, self.bounding_box.mid_x, max_x,
                self.bounding_box.mid_y, max_y,
                self.bounding_box.mid_z, max_z)                  
    
    def add_shape (self, shape):
        shape_box = shape[SHAPE_BOUNDING_BOX](shape)
        if shape_box is None:
            self.shapes.append(shape)
        
        else:
            
            if shape_box.min_x <= self.bounding_box.mid_x: x_left = 0
            if shape_box.min_x >= self.bounding_box.mid_x: x_left = 1
            if shape_box.max_x <= self.bounding_box.mid_x: x_right = 0
            if shape_box.max_x >= self.bounding_box.mid_x: x_right = 1            
        
            if shape_box.min_y <= self.bounding_boy.mid_y: y_top = 0
            if shape_box.min_y >= self.bounding_boy.mid_y: y_top = 1
            if shape_box.max_y <= self.bounding_boy.mid_y: y_bottom= 0
            if shape_box.may_y >= self.bounding_boy.mid_y: y_bottom = 1
            
            if shape_box.min_z <= self.bounding_boz.mid_z: z_front = 0
            if shape_box.min_z >= self.bounding_boz.mid_z: z_front = 1
            if shape_box.max_z <= self.bounding_boz.mid_z: z_back= 0
            if shape_box.max_z >= self.bounding_boz.mid_z: z_back = 1 
            
            for i in range(x_left, x_right + 1):
                for j in range(y_top, y_bottom + 1):
                    for k in range(z_front, z_bottom + 1):
                        self.children[i][j][k].add_shape(shape)
                
            
    def replace_node(self, old_node, new_node):
        for i in range(0,2):
            for j in range(0,2):
                for k in range(0,2):
                    if self.children[i][j][k] == old_node:
                        self.children[i][j][k] = new_node
                        return True
        
        return False
    
    
    def get_shape_dict_by_ray(self, ray):
        shapes = get_shapes_by_ray(ray)
        shape_dict = {}
        for shape in shapes:
            shape_box = shape[SHAPE_BOUNDING_BOX](shape)
            
            if shape_box is not None:
                dist_sq = pow(ray[RAY_START][1]-shape_box.centre[1], 2) + \
                    pow(ray[RAY_START][2]-shape_box.centre[2], 2) + \
                    pow(ray[RAY_START][3]-shape_box.centre[3], 2)
            else:
                dist_sq = 0
                
            shape_dict[dist_sq] = shape
            
        
    
    def get_shapes_by_ray(self, ray):
        nodes = get_nodes_by_ray(ray)
        shapes = []
        for node in nodes:
            shapes = shapes + node.shapes
        
        shapes = list_purge_duplicates(shapes)
        
    
    def get_nodes_by_ray(self, ray):

        nodes = []
        
        if ray[RAY_DIR][1] !=0:
        
            if ray[RAY_START][1] <= self.bounding_box.mid_x:
                x_test_left = self.bounding_box.x_mid
                x_test_right = self.bounding_box.x_max
            else:
                x_test_left = self.bounding_box.x_min
                x_test_right = self.bounding_box.x_mid 
                
            t_x_left = (x_test_left - ray[RAY_START][1]) / ray[RAY_DIR][1]
            t_x_right = (x_test_right - ray[RAY_START][1]) / ray[RAY_DIR][1]
        else:
            t_x_left = -1
            t_x_right = -1
        
        if ray[RAY_DIR][2] !=0:
            if ray[RAY_START][2] <= self.bounding_box.mid_y:
                y_test_top = self.bounding_box.y_mid
                y_test_bottom = self.bounding_box.y_max
            else:
                y_test_top = self.bounding_box.y_min
                y_test_bottom = self.bounding_box.y_mid
                        
            t_y_top = (y_test_top - ray[RAY_START][2]) / ray[RAY_DIR][2]
            t_y_bottom = (y_test_bottom - ray[RAY_START][2]) / ray[RAY_DIR][2]
        else:
            t_y_top = -1
            t_y_bottom = -1
            
        if ray[RAY_DIR][3] !=0:
            
            if ray[RAY_START][3] <= self.bounding_box.mid_z:
                z_test_front = self.bounding_box.z_mid
                z_test_back = self.bounding_box.z_max
            else:
                z_test_front = self.bounding_box.z_min
                z_test_back = self.bounding_box.z_mid
                
            t_z_front = (z_test_front - ray[RAY_START][3]) / ray[RAY_DIR][3]
            t_z_back = (z_test_back - ray[RAY_START][3]) / ray[RAY_DIR][3]
        
        else:
            t_z_front = -1
            t_z_back = -1
        
        if (t_x_left >= 0):
            point = ray_calc_pt(ray, t_x_left)
            
            if (point[2] <= self.bounding_box.max_y and
                point[2] >= self.bounding_box.min_y and
                point[3] >= self.bounding_box.min_z and
                point[3] <= self.bounding_box.max_z):
                
                if (point[2] <= self.bounding_box.mid_y and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[0][0][0])
                    
                elif (point[2] <= self.bounding_box.mid_y and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[0][0][1])
                    
                elif (point[2] >= self.bounding_box.mid_y and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[0][1][0])
                    
                elif (point[2] >= self.bounding_box.mid_y and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[0][1][1]) 
                    
        if (t_x_right >= 0):
            point = ray_calc_pt(ray, t_x_right)
            
            if (point[2] <= self.bounding_box.max_y and
                point[2] >= self.bounding_box.min_y and
                point[3] >= self.bounding_box.min_z and
                point[3] <= self.bounding_box.max_z):
                
                if (point[2] <= self.bounding_box.mid_y and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[1][0][0])
                    
                elif (point[2] <= self.bounding_box.mid_y and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[1][0][1])
                    
                elif (point[2] >= self.bounding_box.mid_y and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[1][1][0])
                    
                elif (point[2] >= self.bounding_box.mid_y and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[1][1][1])
                    

        if (t_y_top >= 0):
            point = ray_calc_pt(ray, t_y_top)
            
            if (point[1] <= self.bounding_box.max_x and
                point[1] >= self.bounding_box.min_x and
                point[3] >= self.bounding_box.min_z and
                point[3] <= self.bounding_box.max_z):
                
                if (point[1] <= self.bounding_box.mid_x and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[0][0][0])
                    
                elif (point[1] <= self.bounding_box.mid_x and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[0][0][1])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[1][0][0])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[1][0][1])
                    
        if (t_y_bottom >= 0):
            point = ray_calc_pt(ray, t_y_bottom)
            
            if (point[1] <= self.bounding_box.max_x and
                point[1] >= self.bounding_box.min_x and
                point[3] >= self.bounding_box.min_z and
                point[3] <= self.bounding_box.max_z):
                
                if (point[1] <= self.bounding_box.mid_x and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[0][1][0])
                    
                elif (point[1] <= self.bounding_box.mid_x and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[0][1][1])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[3] <= self.bounding_box.mid_z):
                    nodes.append (self.children[1][1][0])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[3] >= self.bounding_box.mid_z):
                    nodes.append (self.children[1][1][1])

                    
        if (t_z_front >= 0):
            point = ray_calc_pt(ray, t_z_front)
            
            if (point[1] <= self.bounding_box.max_x and
                point[1] >= self.bounding_box.min_x and
                point[2] >= self.bounding_box.min_y and
                point[2] <= self.bounding_box.max_y):
                
                if (point[1] <= self.bounding_box.mid_x and
                    point[2] <= self.bounding_box.mid_y):
                    nodes.append (self.children[0][0][0])
                    
                elif (point[1] <= self.bounding_box.mid_x and
                    point[2] >= self.bounding_box.mid_y):
                    nodes.append (self.children[0][1][0])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[2] <= self.bounding_box.mid_y):
                    nodes.append (self.children[1][0][0])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[2] >= self.bounding_box.mid_y):
                    nodes.append (self.children[1][1][0])

        if (t_z_back >= 0):
            point = ray_calc_pt(ray, t_z_back)
            
            if (point[1] <= self.bounding_box.max_x and
                point[1] >= self.bounding_box.min_x and
                point[2] >= self.bounding_box.min_y and
                point[2] <= self.bounding_box.max_y):
                
                if (point[1] <= self.bounding_box.mid_x and
                    point[2] <= self.bounding_box.mid_y):
                    nodes.append (self.children[0][0][1])
                    
                elif (point[1] <= self.bounding_box.mid_x and
                    point[2] >= self.bounding_box.mid_y):
                    nodes.append (self.children[0][1][1])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[2] <= self.bounding_box.mid_y):
                    nodes.append (self.children[1][0][1])
                    
                elif (point[1] >= self.bounding_box.mid_x and
                    point[2] >= self.bounding_box.mid_y):
                    nodes.append (self.children[1][1][1])
                    
        my_nodes = list_purge_duplicates(nodes)
        nodes = []
        for node in nodes:
            if isinstance(node, OctTreeBranch):
                nodes = nodes + node.get_nodes_by_ray(ray)
            else:
                nodes.append(node)
        
        return nodes