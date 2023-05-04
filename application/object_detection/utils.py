import math
import cv2

class Utilities():

    min_distance_centroid=0.02
    
    box_color=(0, 0, 255)
    text_color= (0, 255, 255)
    label_color=(0, 255, 0)

    max_disappear = 0
    analytics_color=(255,255,255)

    dev_print_dist = False

    def __init__(self):
        pass

    def distp(self,p1,p2):
        """calc dist between two points

        Args:
            p1 (tuple): point 1
            p2 (tuple): point 2

        Returns:
            float: distance value
        """ 
        x1,y1=p1
        x2,y2=p2
        val=math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )

        return val
    
    def area_triangle(self,pa,pb,pc):
        """area of triangle given three points

        Args:
            pa (tuple): point a
            pb (tuple): point b
            pc (tuple): point c

        Returns:
            float: area of triangle
        """
        val=0.5*(pa[0]*(pb[1]-pc[1])+pb[0]*(pc[1]-pa[1])+pc[0]*(pa[1]-pb[1]))
        if(val<0):
            val=val*(-1)

        return val

        
    def point_in_box(self,pi,bps):
        """check if point pi is in the box defined by points in bps

        Args:
            pi (tuple - x,y): point of interest
            bps (array of tuple of x,y): array of tuple of points of roi in cyclic order

        Returns:
            _type_: _description_
        """
        
        (pa,pb,pc,pd) = bps
        a1=self.area_triangle(pi,pa,pb)
        a2=self.area_triangle(pi,pb,pc)
        a3=self.area_triangle(pi,pc,pd)
        a4=self.area_triangle(pi,pd,pa)

        aq=self.area_triangle(pa,pb,pd)+self.area_triangle(pc,pb,pd)

        # print("a1 "+str(a1+a2+a3+a4)+" aq "+str(aq))
        if(int((a1+a2+a3+a4)*100)==int(aq*100)):
            return True
        else:
            return False
    
    def draw_aoi(self,img2,box_points):
        """utitility function to draw the aoi on the frame given the box_points

        Args:
            img2 (cv2 image): image to draw on
            box_points (array of tuples of x,y): cyclic direction of points
        """
        shp=img2.shape
        for i in range(len(box_points)-1):
            cv2.line(img2, 
                (int(shp[1]*box_points[i][0]),int(shp[0]*box_points[i][1])),
                (int(shp[1]*box_points[i+1][0]),int(shp[0]*box_points[i+1][1])),
                (255, 255,0),
                5)
        cv2.line(img2, 
            (int(shp[1]*box_points[-1][0]),int(shp[0]*box_points[-1][1])),
            (int(shp[1]*box_points[0][0]),int(shp[0]*box_points[0][1])),
            (255, 255,0),
            5)
        return

    def draw_bbox(self,img2,label,startX,startY,endX,endY,dwt,box_color):
        """utitility function to draw bounding boxes of objects with dwell time

        Args:
            img2 (cv2 img): image/frame to draw objects on
            label (string): id/label of the object
            startX (int): -
            startY (int): -
            endX (int): -
            endY (int): -
            dwt (int): dwell time to display
        """
        cv2.rectangle(img2, (startX, startY), (endX, endY), box_color, 2, cv2.LINE_AA)
        cv2.putText(img2, label, (startX, startY - 15),cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.label_color, 2)
        cv2.putText(img2, "class : "+str(dwt), (startX, startY - 35),cv2.FONT_HERSHEY_SIMPLEX, 0.35, self.text_color, 2)
        return 

    def draw_analytics_global(self,img2,cavgt,cmaxt,cmint,gmindt,gmaxdt,gavgdt,count):
        cv2.putText(img2, "curr avg dwell : "+str(cavgt), (20,30),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        cv2.putText(img2, "people : "+str(count), (20,60),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        cv2.putText(img2, "curr max dwell : "+str(cmaxt), (20,90),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        cv2.putText(img2, "curr min dwell : "+str(cmint), (20,120),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        return 

    def draw_analytics(self,img2,cavgt,cmaxt,cmint,count):
        cv2.putText(img2, "curr avg dwell : "+str(cavgt), (20,30),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        cv2.putText(img2, "people : "+str(count), (20,60),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        cv2.putText(img2, "curr max dwell : "+str(cmaxt), (20,90),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        cv2.putText(img2, "curr min dwell : "+str(cmint), (20,120),cv2.FONT_HERSHEY_SIMPLEX, 1, self.analytics_color, 3)
        
        return 

    def draw_analytics_people_count(self,img2,entry_val,exit_val):
        cv2.putText(img2, "Entry : "+str(entry_val), (20,90),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.putText(img2, "Exit : "+str(exit_val), (20,120),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        return 

    def draw_line(self,img2,start,end):
        """draw people count line

        Args:
            img2 (cv2 image): frame/image to draw on
        """
        shp=img2.shape
        x1=int(start[0])
        y1=int(start[1])
        x2=int(end[0])
        y2=int(end[1])
        cv2.line(img2, 
            (x1,y1),
            (x2,y2),
            (255, 255,0),
            5)
        
        return 