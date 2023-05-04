
class Person():
    def __init__(self, box, label, start_time):
        """Initialize Person class.
        Args:
            box (list): bounding box.
            label (list): label.
            score (list): score.
        """
        self.box=box
        self.label=label
        self.start_time = start_time
        # self.__has_uniform = None

    def get_dwell(self,chunker_time):
        val=int(((chunker_time-self.start_time).total_seconds()*10))
        return val

# people count
class People():
    def __init__(self, box, id_):
        """Initialize Person class.
        Args:
            box (list): bounding box.
            id_ (list): id_.
            score (list): score.
        """
        self.box=box
        self.id_=id_
        self.previous_centroid=None
        self.current_centroid = self.box[0]+self.box[2]*0.5,self.box[1]+self.box[3]*0.5

        self.box_color = (255,255,255)
        self.crossed = False

    def update_box_color(self,color):
        if(color == "GREEN"):
            self.box_color = (0, 255, 0)
        elif(color == "RED"):
            self.box_color = (0, 0, 255)
        elif(color == "WHITE" and not self.crossed):
            self.box_color = (255,255,255)

    def update_position(self,new_box):
        """update position of object

        Args:
            new_box (list): coordinates of new box
        """
        self.previous_centroid = self.current_centroid
        self.current_centroid = new_box[0]+new_box[2]*0.5,new_box[1]+new_box[3]*0.5
      
        return

    def get_direction(self):
        """get direction of moving object by using previous known point

        Returns:
            int: 0 indicates exit 1 indicates entry given that upwards is entry -1 indicates no direction
        """

        if(self.previous_centroid is None):
            return -1
        
        val=self.current_centroid[1]-self.previous_centroid[1]

        if(val>0):
            return 0 # exit
        else:
            return 1 # entry

    def check_position(self,y_line,y):
        """check position of object based on its centroid

        Args:
            y_line (float): y coordinate of horizontal line of reference
            y (float): y coordinate of point under consideration

        Returns:
            int: 0 means under the lin, 1 means over the line
        """
        
        if(y>y_line):
            return 0 # under
        else:
            return 1

    def check_line_cross(self,y_line):
        """check if the line has been crossed for the object

        Args:
            y_line (float): y coordinate of horizontal line

        Returns:
            bool: whether the object has crossed or not
        """

        if(self.previous_centroid is None):
            return False
            
        pos_current = self.check_position(y_line,self.current_centroid[1])
        pos_previous = self.check_position(y_line,self.previous_centroid[1])
        if(not self.crossed):
            if(pos_previous == pos_current):
                return False
            else:
                self.crossed = True
                return True
        return False
        

