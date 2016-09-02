#!/usr/bin/env python
#coding:utf-8
#Author : Xu
#Time :2016/7/23
# 检测篮球的相关接口

#可考虑将find_ball_turn（goal_angular）和find_ball_turn_cw（goal_angular）合为一个方法

import ros
import tf
import actionlib
import math
import rospy
import roslib
from basketball_catchone_srv.srv import *
import geometry_msgs.msg as g_msgs
import geometry_msgs.msg as msgs
from robot_move_pkg import  go_along_circle
from robot_state_pkg import get_robot_position
class findBall(object):
    def __init__(self):
        self.find_ball_client = rospy.ServiceProxy('oneball_data',CatchOneBall)
        self.cmd_vel_pub = rospy.Publisher('/cmd_move' , g_msgs.Twist , queue_size=100)
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('waiting for the find ball..')
        self.find_ball_client.wait_for_service()
        rospy.loginfo('connect to the find ball!!!')

    #逆时针旋转并不断检测球，当获取到球的数据后停止，并获取当前球的信息.如果未检测到球则转一定角度后停止
    def find_ball_turn_cw(self,goal_angular):
        current_angular = start_angular = self.cmd_position.get_robot_current_w()
        self.find_ball_client.wait_for_service()
        move_velocity = g_msgs.Twist()
        move_velocity.angular.z = 0.15
        res = self.find_ball_client()
        x = res.z
        y = -res.x
        theta = -res.theta
        has_ball = res.has_ball
        delta_angular = current_angular - start_angular
        r = rospy.Rate(30)
        flag = 0 #标记检测到球的次数
        while not rospy.is_shutdown() and not has_ball:
            current_angular = self.cmd_position.get_robot_current_w()
            delta_angular = current_angular - start_angular
            delta_upper_limit = abs(goal_angular) + 0.04 #误差上限
            delta_lower_limit = abs(goal_angular) - 0.04 #误差下限
            self.cmd_vel_pub.publish(move_velocity)

            res = self.find_ball_client()
            x = res.z
            y = -res.x
            theta = -res.theta
            has_ball = res.has_ball
            if has_ball == True:
                flag += 1
            #当检测到10次球后再停止，以保证确实获取到球的数据.  注意：需考虑数据延时问题
            if flag == 10 or (abs(delta_angular)<=delta_upper_limit and abs(delta_angular) >= delta_lower_limit):
                self.brake()
                break
            r.sleep()
        return (x,y,theta,has_ball)

    #顺时针旋转并不断检测球，当获取到球的数据后停止，并获取当前球的信息。如果未检测到球则转一定角度后停止
    def find_ball_turn(self,goal_angular):
        current_angular = start_angular = self.cmd_position.get_robot_current_w()
        self.find_ball_client.wait_for_service()
        move_velocity = g_msgs.Twist()
        move_velocity.angular.z = -0.15
        res = self.find_ball_client()
        x = res.z
        y = -res.x
        theta = -res.theta
        has_ball = res.has_ball
        delta_angular = current_angular - start_angular
        r = rospy.Rate(30)
        flag = 0
        while not rospy.is_shutdown() and not has_ball:
            current_angular = self.cmd_position.get_robot_current_w()
            delta_angular = current_angular - start_angular
            delta_upper_limit = abs(goal_angular) + 0.04 #误差上限
            delta_lower_limit = abs(goal_angular) - 0.04 #误差下限
            self.cmd_vel_pub.publish(move_velocity)

            res = self.find_ball_client()
            x = res.z
            y = -res.x
            theta = -res.theta
            has_ball = res.has_ball
            if has_ball == True:
                flag += 1
            if flag == 10 or (abs(delta_angular)<=delta_upper_limit and abs(delta_angular) >= delta_lower_limit):
                self.brake()
                break
            r.sleep()
        #由于实际使用情况，加了一个修正值。为了防止机器在底脚捡球时走到界外
        return (x,y + 0.4,theta)

    #直接获取当前检测到的球的数据
    def find_ball(self):
        self.find_ball_client.wait_for_service()
        res = self.find_ball_client()
        x = res.z
        y = -res.x
        theta = -res.theta*0.95
        return (x,y,theta)

    def brake(self):
        self.cmd_vel_pub.publish(g_msgs.Twist())