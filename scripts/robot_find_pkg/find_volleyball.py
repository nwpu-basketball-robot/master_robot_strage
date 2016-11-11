#!/usr/bin/env python
# -*- coding:utf-8 -*-
#Author: Xu
#检测排球的相关接口

import ros
import tf
import actionlib
import math
import rospy
import roslib
import sys
sys.path.append('/home/mrxu/basketball/src/basketball_strage/scripts/')
# from volleyball_detect.srv import *
from object_detect.srv import *
import geometry_msgs.msg as g_msgs
from robot_move_pkg import  go_along_circle
from robot_state_pkg import get_robot_position

class find_volleyball(object):
    def __init__(self):
        self.find_ball_client = rospy.ServiceProxy('volleyball_data',volleyballdata)
        self.cmd_vel_pub = rospy.Publisher('cmd_move_robot' , g_msgs.Twist , queue_size=100)
        self.cmd_position = get_robot_position.robot_position_state()
        self.move_speed = 0.21
        #注册停止回调函数
        rospy.on_shutdown(self.brake)
        #用来决定走弧线方向的参数
        self.MODE = { 1:(-1, 1),
                      2:( 1,-1),
                      3:( 1, 1),
                      4:(-1,-1)}
        rospy.loginfo('waiting for the find ball..')
        self.find_ball_client.wait_for_service()
        rospy.loginfo('connect to the find ball!!!')

    #逆时针旋转寻找排球，检测到排球后停止
    def find_ball_turn(self):
        self.find_ball_client.wait_for_service()
        move_velocity = g_msgs.Twist()
        move_velocity.angular.z = 0.42
        res = self.find_ball_client(False)
        x = res.z
        y = -res.x
        theta = -res.theta
        has_ball = res.has_ball
        if_volleyball = res.if_volleyball
        r = rospy.Rate(30)
        flag = 0
        while not rospy.is_shutdown() and not has_ball:
            self.cmd_vel_pub.publish(move_velocity)
            res = self.find_ball_client(False)
            x = res.z
            y = -res.x
            theta = -res.theta
            has_ball = res.has_ball
            if_volleyball = res.if_volleyball
            if has_ball == True and if_volleyball == True:
                flag += 1
            if flag == 2:
                self.brake()
                break
            r.sleep()
        return (x,y,theta)

    #顺时针旋转寻找排球，检测到排球后停止
    def find_ball_turn_cw(self):
        self.find_ball_client.wait_for_service()
        move_velocity = g_msgs.Twist()
        move_velocity.angular.z = -0.38
        res = self.find_ball_client(False)
        x = res.z
        y = -res.x
        theta = -res.theta
        has_ball = res.has_ball
        if_volleyball = res.if_volleyball
        r = rospy.Rate(30)
        flag = 0
        while not rospy.is_shutdown() and not has_ball:
            self.cmd_vel_pub.publish(move_velocity)
            res = self.find_ball_client(False)
            x = res.z
            y = -res.x
            theta = -res.theta
            has_ball = res.has_ball
            if_volleyball = res.if_volleyball
            if has_ball == True and if_volleyball == True:
                flag += 1
            if flag == 3:
                self.brake()
                break
            r.sleep()
        return (x,y,theta)

    #直接获取球位置信息
    def find_ball(self):
        self.find_ball_client.wait_for_service()
        res = self.find_ball_client(False)
        x = res.z
        y = -res.x
        theta = -res.theta
        has_ball = res.has_ball
        return (x,y,theta,has_ball)

    #直接获取排球的位置
    def find_volleyball(self):
        self.find_ball_client.wait_for_service()
        res = self.find_ball_client(False)
        x = res.z
        y = -res.x
        theta = -res.theta
        if_volleyball = res.if_volleyball
        r = rospy.Rate(50)
        while not if_volleyball == True:
            res = self.find_ball_client(False)
            x = res.z
            y = -res.x
            theta = -res.theta
            if_volleyball = res.if_volleyball
        if if_volleyball == True:
            return (x,y,theta)
    #以一定的圆心，半径，以圆弧行进的方式检测排球
    #用于检测边线上的排球
    def find_ball_by_line(self):
        self.find_ball_client.wait_for_service()
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        radius = math.sqrt(current_y * current_y+current_x*current_x) + 6.75
        symbol_y,symbol_w = self.MODE[1]
        move_vel = g_msgs.Twist()
        move_vel.linear.y = self.move_speed*symbol_y
        move_vel.angular.z = 100*math.atan2(self.move_speed/100,radius)*symbol_w

        res = self.find_ball_client(False)
        x = res.z
        y = -res.x
        theta = -res.theta
        has_ball = res.if_volleyball
        r = rospy.Rate(50)
        while not rospy.is_shutdown():
            self.cmd_vel_pub.publish(move_vel)
            res = self.find_ball_client(False)
            x = res.z
            y = -res.x
            theta = -res.theta
            has_ball = res.if_volleyball
            rospy.loginfo("has_ball = %s",has_ball)
            rospy.loginfo("y = %s",abs(y))
            #如果球的y轴数据大于0.1,则判定为不是排球
            #原因：图像部分以球直径来判别排球和篮球，在一定角度下篮球与排球半径相同。当正对球时，可以保证检测的准确性
            if has_ball == True and (abs(y) < 0.1):
                self.brake()
                break
            r.sleep()
        return (x,y,theta)

    def brake(self):
        self.cmd_vel_pub.publish(g_msgs.Twist())

if __name__ == '__main__':
    rospy.init_node('turn_angular')
    find_volleyball().find_ball_by_line()