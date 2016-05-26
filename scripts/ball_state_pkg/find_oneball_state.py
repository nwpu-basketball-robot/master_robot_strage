#!/usr/bin/env python
#coding=utf-8
#为状态机模块提供找一个球的接口
#kinect的坐标系与机器人坐标系不同！
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
    
    #返回当前一个球与机器人x方向上的距离
    def get_Ball_current_x(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return req.z
        
    #返回当前于机器人y方向上的距离
    def get_Ball_current_y(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return -req.x
    #返回当前与机器人角度差值
    def get_Ball_current_theta(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return -req.theta

    #返回当前球的信息：是否有球，x上距离，y上距离，角度差值
    def get_Ball_current_status(self):
        self.ball_client.wait_for_service()
        req = self.ball_client()
        return req.has_ball, req.z, -req.x, -req.theta
    #是否有球
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