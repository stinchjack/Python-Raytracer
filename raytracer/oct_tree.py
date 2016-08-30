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
        self.parent_branch = parent_branch
        self.shapes = []
        self.split_threshold =  split_threshold
        self.bounding_box = BoundingBox(
            min_x, max_x, min_y, max_y, min_z, max_z)
        self.shape_count = 0
          
    def can_split (self):   
        
        if hasattr(self.parent_branch, "shape_count"):
            if self.shape_count >= self.parent_branch.shape_count:
                return False
                
        return True 
                 
     
class OctTreeLeaf(OctTreeNode):
 

 
    def add_shape(self, new_shape):
            
            
        self.shape_count += 1
                
        
        self.shapes.append(new_shape)
        if len(self.shapes) > self.split_threshold and self.can_split():
            new_branch = OctTreeBranch(
                self.parent_branch, self.split_threshold,
                self.bounding_box.min_x, self.bounding_box.max_x,
                self.bounding_box.min_y, self.bounding_box.max_y,
                self.bounding_box.min_z, self.bounding_box.max_z)   
                      
            for shape in self.shapes:
                new_branch.add_shape(shape)

            self.shapes = []
            
            if self.parent_branch is not None:
                self.parent_branch.replace_node(self, new_branch)

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
            
          
    def get_shapes_by_ray(self, ray):
      return self.shapes

    def get_nodes_by_ray(self, ray):
      return None
      
    def __str__(self):
        str = "OctTreeLeaf ID: %d "%id(self)
        str = str + " Bounding box: %s " % self.bounding_box.__str__()
        str = str + ",   Shapes: "
        if len(self.shapes)>0:
            for s in self.shapes:
                str = "%s%d, " % (str, id(s) )
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
      

                       
    
    def __str__(self):
        str = "-----------------------------------------------------------------------------------\n"
        for j in range(0,2):
            left = self.str_break(self.children[0][j][0].__str__())
            str = "%s| %s | %s |\n" % (str, self.str_break(self.children[0][j][0].__str__()), self.str_break(self.children[1][j][0].__str__() ))
            str = "%s%s" % (str, "-----------------------------------------------------------------------------------\n")
            
        str = "%s%s" % (str, "\n\n")

        for j in range(0,2):
            str = "%s| %s | %s |\n" % (str, self.str_break(self.children[0][j][1].__str__()), self.str_break(self.children[1][j][1].__str__() ))
            str = "%s%s" % (str, "-----------------------------------------------------------------------------------\n")
            
        str = "%s%s" % (str, "\n\n")
        return str  
    
    def str_break(self, str, width=40):
        list = textwrap.wrap(str, width=width);
        str = ""
        list_p = []
        for line in list:
            list_p.append(line.ljust(width))
            
    def add_shape (self, shape):
        
        stop = False
        if shape[raytracer.shape.SHAPE_TRANSFORM] is not None:
            trans_opt = shape[raytracer.shape.SHAPE_TRANSFORM].__options__
            if 'scale' in trans_opt and \
                trans_opt['scale']['x'] > trans_opt['scale']['y'] and \
                type(self.parent_branch) is not raytracer.scene.Scene:
                stop = True
                import pdb; pdb.set_trace()        
                
        
        stop = False
        
        self.shape_count += 1        
        
        shape_box = raytracer.shape.shape_bounding_box(shape)
        #print ("---- %s" % shape_box.__str__()) 

        #print (self.bounding_box)

        if shape_box is None or not self.can_split():
            self.shapes.append(shape)
            if stop: import pdb; pdb.set_trace()

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
                        self.children[i][j][k].add_shape(shape)
            
            if stop: import pdb; pdb.set_trace()
            
            #if self.shape_count == 3:  import pdb; pdb.set_trace()      
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
        nodes = self.get_nodes_by_ray(ray)

        shapes = []
        for node in nodes:
            shapes = shapes + node.shapes

        shapes += self.shapes
        
        shapes = list_purge_duplicates(shapes)
        
                    
        return shapes
    
    def get_nodes_by_ray(self, ray):

        nodes = []
        
        """
        t_tests = [[None, None] , [None, None] , [None, None]]
        box_bounds = [
            [self.bounding_box.min_x, self.bounding_box.mid_x, self.bounding_box.max_x],
            [self.bounding_box.min_y, self.bounding_box.mid_y, self.bounding_box.max_y],
            [self.bounding_box.min_z, self.bounding_box.mid_z, self.bounding_box.max_z]]
        
        for dimension in range(0,3):
        
            if ray[RAY_DIR][dimension + 1] !=0: # if not paralell to axis
            
                if ray[RAY_START][dimension + 1] <= box_bounds[dimension][1]:
                    incr = 1
                
                else:
                    incr = 0
                
                t_tests [dimension][0] = (box_bounds[dimension][0 + incr] - ray[RAY_START][dimension + 1]) / ray[RAY_DIR][dimension + 1]
                t_tests [dimension][1] = (box_bounds[dimension][1 + incr] - ray[RAY_START][dimension + 1]) / ray[RAY_DIR][dimension + 1]
            else:
                t_tests [dimension][0] = -1
                t_tests [dimension][1] = -1
      
        
        for dimension in range(0, 3):
            test_dim_1 = 0                
            test_dim_2 = 1
            non_test_dim = 2
            if dimension == 0:
               test_dim_1 = 2
               non_test_dim = 0
            elif dimension == 1:
               test_dim_2 = 2
               non_test_dim = 1
            
            for aspect in range(0, 2):
                set_x = None
                set_y = None
                set_z = None
                 
                if (t_tests[dimension][aspect] >= 0):
                    point = ray_calc_pt(ray, t_tests[dimension][aspect])
                    
                    if (point[test_dim_1 + 1] <= box_bounds[test_dim_1][2] and
                        point[test_dim_1 + 1] >= box_bounds[test_dim_1][0] and
                        point[test_dim_2 + 1] >= box_bounds[test_dim_2][2] and
                        point[test_dim_2 + 1] <= box_bounds[test_dim_2][0]):
                        
                                               
                         
                        if point[test_dim_1 + 1] <= box_bounds[test_dim_1][1]:
                            dim_1_idx = 0
                        else:
                            dim_1_idx = 1

                        if point[test_dim_2 + 1] <= box_bounds[test_dim_2][1]:
                            dim_2_idx = 0
                        else:
                            dim_2_idx = 1
                            
                        if non_test_dim == 0:
                            set_x = aspect
                        elif non_test_dim == 1:
                            set_y = aspect
                        elif non_test_dim == 2:
                            set_z = aspect

                        if test_dim_1 == 0:
                            set_x =  dim_1_idx
                        else:
                            set_z =  dim_1_idx
                            
                        if test_dim_2 == 1:
                            set_y =  dim_2_idx
                        else:
                            set_z =  dim_2_idx                            
                            
                        printf ("setx: %d, sety: %d, setz %d\n"% (set_x, set_y, set_z))                            
                        nodes.append (self.children[set_x][set_y][set_z])   
                            


        """                
        
        if ray[RAY_DIR][1] !=0: # if not paralell to X-axis
        
            if ray[RAY_START][1] <= self.bounding_box.mid_x:
                x_test_left = self.bounding_box.mid_x
                x_test_right = self.bounding_box.max_x
            else:
                x_test_left = self.bounding_box.min_x
                x_test_right = self.bounding_box.mid_x 
                
            t_x_left = (x_test_left - ray[RAY_START][1]) / ray[RAY_DIR][1]
            t_x_right = (x_test_right - ray[RAY_START][1]) / ray[RAY_DIR][1]
        else:
            t_x_left = -1
            t_x_right = -1
        
        if ray[RAY_DIR][2] !=0:
            if ray[RAY_START][2] <= self.bounding_box.mid_y:
                y_test_top = self.bounding_box.mid_y
                y_test_bottom = self.bounding_box.max_y
            else:
                y_test_top = self.bounding_box.min_y
                y_test_bottom = self.bounding_box.mid_y
                        
            t_y_top = (y_test_top - ray[RAY_START][2]) / ray[RAY_DIR][2]
            t_y_bottom = (y_test_bottom - ray[RAY_START][2]) / ray[RAY_DIR][2]
        else:
            t_y_top = -1
            t_y_bottom = -1
            
        if ray[RAY_DIR][3] !=0:
            
            if ray[RAY_START][3] <= self.bounding_box.mid_z:
                z_test_front = self.bounding_box.mid_z
                z_test_back = self.bounding_box.max_z
            else:
                z_test_front = self.bounding_box.min_z
                z_test_back = self.bounding_box.mid_z
                
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
        
        # if len(nodes)>0: import pdb;pdb.set_trace();
        nodes = []
        
        for node in my_nodes:
            if isinstance(node, OctTreeBranch):
                nodes = nodes + node.get_nodes_by_ray(ray)
            else:
                nodes.append(node)
        
        return nodes       
                    
                    
