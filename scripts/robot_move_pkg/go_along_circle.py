#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 2016-7-13
# #让机器人沿着一个圆弧跑
# 

import config
import sys
sys.path.append(config.robot_state_pkg_path)
import rospy
import robot_state_pkg.get_robot_position as robot_state
import geometry_msgs.msg as g_msgs
from math import *

class go_along_circle(object):
    def __init__(self):
        #向机器人坐标系发速度 m/s
        self.move_cmd_pub = rospy.Publisher('cmd_move_robot',g_msgs.Twist,queue_size=100)
        self.move_speed = config.go_along_circle_speed
        self.MODE = { 1:(-1, 1),
                      2:( 1,-1),
                      3:( 1, 1),
                      4:(-1,-1)}
    # radius: 回转半径
    # angular: 回转角度
    # mode 1:   向右前方转
    # mode 2:   向左前方转
    # mode 3:   向右后方转
    # mode 4:   向左后方转
    def go(self, radius,mode):
        # 设置机器人运动的方向
        symbol_y,symbol_w = self.MODE[mode]
        ang_has_moved = 0.0
        self.reach_goal = False
        move_vel = g_msgs.Twist()
        move_vel.linear.y = self.move_speed*symbol_y
        # 利用微分的原理, 可以发现 dw*dt = dt*atan2(dv*dt/2.0, radius)
        move_vel.angular.z = self.rate*atan2(self.move_speed/self.rate,radius)*symbol_w
        self.move_cmd_pub.publish(move_vel)

    def move_to(self, radius, angular, mode):
        # 提供给外部的接口
        self.go(radius, angular, mode)

if __name__ == '__main__':
    rospy.init_node('ffffffffffffffff')
    test = go_along_circle()
    test.go(0.5,1)
sys.path.remove(config.robot_state_pkg_path)
