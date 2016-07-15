#! /usr/bin/env python
# -*- coding:utf-8 -*-
import rospy
import  math
import config
import move_in_robot
import  geometry_msgs.msg as g_msg
class move_to_home(object):
    def __init__(self):
        self.move_direction = config.go_home_direction
        self.robot_move = move_in_robot.linear_move()
        self.last_move_goal = config.last_distance
        self.angular_tolerance = config.back_home_angular_tolerance
        self.distance_tolerance = config.line_distance_tolerance
        #需要与白线保持的距离
        self.line_distance = config.line_distance

        self.x_speed = config.go_home_x_speed
        self.y_speed = config.go_home_y_speed * self.move_direction
        self.z_speed = config.go_home_w_speed

        self.cmd_move_pub =rospy.Publisher("/cmd_move_robot",g_msg.Twist, queue_size= 100)
        self.vel = g_msg.Twist()
    def start_run(self, at_home_door, distance, angular):
        if at_home_door == True:
            self.brake()
            self.robot_move.move_to(x = self.last_move_goal)
            return  True
        if distance > (self.line_distance + self.distance_tolerance):
            self.vel.linear.x = self.x_speed
            self.vel.linear.y = math.copysign(self.y_speed, self.move_direction)
        elif distance < (self.line_distance - self.distance_tolerance):
            self.vel.linear.x = self.x_speed * -1
            self.vel.linear.y = self.y_speed
        else:
            self.vel.linear.x = 0
            self.vel.linear.y = self.y_speed
        if math.fabs(angular) < self.angular_tolerance:
            self.vel.angular.z = 0
        elif angular > 0:
            self.vel.angular.z = -1 * self.z_speed
        else:
            self.vel.angular.z = self.z_speed
        self.cmd_move_pub.publish(self.vel)


        return False

    def brake(self):
        self.cmd_move_pub.publish(g_msg.Twist())
