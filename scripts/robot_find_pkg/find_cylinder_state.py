#!/usr/bin/python
#coding=utf-8
#Author: Xu

#为状态机模块提供找定位柱的接口
#kinect的坐标系与机器人坐标系不同！

import rospy
# from cylinder_detector.srv  import *
from object_detect.srv import *
from cylinder_find.srv import *
from robot_move_pkg import turn_an_angular
from robot_state_pkg import get_robot_position

import geometry_msgs.msg as g_msgs
import math

class find_cylinder_state(object):
    def __init__(self):
        self.cylinder_client = rospy.ServiceProxy('cylinder_data',cylinderdata)
        self.cylinder_theta_client = rospy.ServiceProxy('cylinder_data_theta',cylinder_find)
        self.cmd_vel_pub = rospy.Publisher('cmd_move_robot' , g_msgs.Twist , queue_size=100)
        rospy.loginfo('[cylinder_state_pkg]->waiting cylinderdata service')
        self.cylinder_client.wait_for_service()
        self.cylinder_theta_client.wait_for_service()
        rospy.loginfo('[cylinder_state_pkg] -> connected to cylinder service')


    #边转动边检测定位柱，检测到后停止
    def get_cylinder_status(self):
        self.cylinder_client.wait_for_service()
        res = self.cylinder_client(True)
        current_angular = start_angular = get_robot_position.robot_position_state().get_robot_current_w()
        move_velocity = g_msgs.Twist()
        move_velocity.angular.z = -0.13
        x = res.z
        theta = res.theta
        iscylinder = res.has_cylinder
        delta_angular = current_angular - start_angular
        flag = 0
        r = rospy.Rate(50)
        while not rospy.is_shutdown() and not iscylinder:
            current_angular = get_robot_position.robot_position_state().get_robot_current_w()
            delta_angular = current_angular - start_angular
            delta_upper_limit = abs(math.pi * 2 / 3) + 0.04 #误差上限
            delta_lower_limit = abs(math.pi * 2 / 3) - 0.04 #误差下限
            self.cmd_vel_pub.publish(move_velocity)
            res = self.cylinder_client(True)
            x = res.z
            theta = res.theta
            iscylinder = res.has_cylinder
            if (abs(delta_angular)<=delta_upper_limit and abs(delta_angular) >= delta_lower_limit):
                flag = 1
            if iscylinder == 1 or (abs(delta_angular)<=delta_upper_limit and abs(delta_angular) >= delta_lower_limit):
                self.brake()
                break

            r.sleep()
        if flag == 1:
            turn_an_angular.turn_an_angular().turn_to(-math.pi/2)
            x = 2.55
        return (x,theta)

    #直接获取定位柱的位置信息
    def get_cylinder_distance(self):
        # res = self.cylinder_client(True)
        i = 0
        distance = []
        while i < 3:
            res_theta = self.cylinder_client(True)
            x = res_theta.z
            theta = res_theta.theta
            distance.append(x)
            i = i + 1
        sort_distance = sorted(distance)
        x = sort_distance[1]
        rospy.loginfo("!!!!!!!@@@x0 = %s",sort_distance[0])
        rospy.loginfo("!!!!!!!@@@x1 = %s",sort_distance[1])
        rospy.loginfo("!!!!!!!@@@x2 = %s",sort_distance[2])
        return (x,theta)

    def find_cylinder(self):
        res_theta = self.cylinder_theta_client()
        x = 0
        theta = res_theta.theta
        return (x,theta)

    def brake(self):
        self.cmd_vel_pub.publish(g_msgs.Twist())


if __name__ == '__main__':
    rospy.init_node('find_cylinder')
    test = find_cylinder_state()
    print test.find_cylinder()
