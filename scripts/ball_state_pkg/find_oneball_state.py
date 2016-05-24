#!/usr/bin/env python
#coding=utf-8

import rospy
import roslib 
import tf
import math
from basketball_catch_one_srv.srv import *

class find_oneball_state(object):
    def __init__(self):
        self.ball_client = rospy.ServiceProxy('oneball_data', CatchOneBall)
        rospy.loginfo('[find_oneball_state_pkg]->waiting oneball_data service ...')
        self.ball_client.wait_for_service()
        rospy.loginfo('[find_oneball_state_pkg]->connected to oneball_data service ...')
    
    def get_Ball_current_x(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return req.z

    def get_Ball_current_y(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return -req.x
    
    def get_Ball_current_theta(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return -req.theta

    def get_Ball_current_status(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return req.has_ball, req.z, -req.x, -req.theta

    def get_Ball_hasball(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return req.has_ball
if __name__ == '__main__':
   a = find_oneball_state()
   a.get_Ball_current_x()
   a.get_Ball_current_y()
   a.get_Ball_current_theta()
   a.get_Ball_current_status()
   a.get_Ball_hasball()