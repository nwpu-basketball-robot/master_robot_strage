#!/usr/bin/env python
#coding:utf-8

import ros
import tf
import actionlib
import math
import rospy
import roslib
from lineing.srv import *
import geometry_msgs.msg as g_msgs

#检测边线的接口

class find_line(object):
    def __init__(self):
        self.find_line_client = rospy.ServiceProxy('line_data',CatchOneLine)
        rospy.loginfo('waiting for the line..')
        self.find_line_client.wait_for_service()

    def find_line(self):
        self.find_line_client.wait_for_service()
        res = self.find_line_client()
        x = res.distance
        theta = res.theta
        if_go_home = res.ArriveAtHome
        return (x,theta,if_go_home)

if __name__ == '__main__'   :
    rospy.init_node('find_line')
    move_cmd = find_line()
    (x,theta,if_go_home) = move_cmd.find_line()
    rospy.loginfo("x = %s",x)
