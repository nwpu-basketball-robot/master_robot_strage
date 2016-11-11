#! /usr/bin/env python
# -*- coding:utf-8 -*-
#Time : 2016/7/23
#Author : Xu
#机器检测边线回家的方法
#流程：1.首先边检测边线边接近边线，当看到边线处于视野中间时停止向前
#     2.根据图像返回数据开始修正角度，当正对边线时停止。
#     3.让机器以机器坐标系下向接近起始点的y轴方向移动，直到检测到竖线，视为检测到起始框，然后移动进入初始点
#使用时直接调用go_close_line方法即可


#测试BUG: 在go_to_home（）的方法执行时,本应该发出去y = -0.15的直线速度，但是该服务却接收到了y = 0.15的速度。原因不明，只在某一晚上出现过三次
#        之后测试又正常。
import rospy
import  math
import config
import move_in_robot
import  geometry_msgs.msg as g_msgs
import  sys
sys.path.append(config.robot_state_pkg_path)
import robot_find_pkg.find_line as findline
from robot_state_pkg import get_robot_position

class move_to_home(object):
    def __init__(self):
        self.robot_move = move_in_robot.linear_move()
        self.last_move_goal = config.last_distance
        self.close_line_cmd = findline.find_line()
        self.cmd_move_pub = rospy.Publisher("/cmd_move_robot", g_msgs.Twist, queue_size= 100)

    #即流程1：接近边线
    def go_close_line(self):
        (x,theta,if_close_line) = self.close_line_cmd.find_line()
        flag = 0;
        r = rospy.Rate(50)
        move_velocity = g_msgs.Twist()

        move_velocity.linear.x = 0.3

        while not rospy.is_shutdown():
            (x,theta,if_close_line) = self.close_line_cmd.find_line()
            self.cmd_move_pub.publish(move_velocity)
            if x != 0:
                flag = flag + 1;
            if flag >= 3:
                self.brake()
                break
            r.sleep()
        self.correct_angle()
        self.go_to_home()
        #机器检测完回家框后停下来的位置和场地条件关系很大，一下所走的x,y值根据具体场地进行修改
        self.robot_move.move_to(y = -0.50)
        self.robot_move.move_to(x = 0.85)


    #流程2：修正角度
    #备注：修正角度中需考虑图像数据获取延时的问题
    def correct_angle(self):
        # rospy.loginfo("sadasdafasf")
        (x,theta,if_close_line) = self.close_line_cmd.find_line()
        r = rospy.Rate(50)
        move_velocity = g_msgs.Twist()
        if theta > 0:
            move_velocity.angular.z = -0.10
        else:
            move_velocity.angular.z = 0.10
        while not rospy.is_shutdown():
            (x,theta,if_close_line) = self.close_line_cmd.find_line()
            self.cmd_move_pub.publish(move_velocity)
            #修正角度的范围可根据实际情况调整

            if theta < 0.02 and theta > -0.02:
                rospy.loginfo("will Stop!!!!!!!!!!")
                self.brake()
                break
            r.sleep()


    #流程3：返回起始点
    def go_to_home(self):
        (x,theta,if_close_line) = self.close_line_cmd.find_line()
        r = rospy.Rate(50)
        move_velocity = g_msgs.Twist()
        while not rospy.is_shutdown():
            (x,theta,if_close_line) = self.close_line_cmd.find_line()
            move_velocity.linear.y = -0.3
            self.cmd_move_pub.publish(move_velocity)
            rospy.loginfo("python: y = %s",move_velocity.linear.y)
            if if_close_line != 0:
                rospy.loginfo("will Stop!!!!!!!!!!")
                self.brake()
                break
            r.sleep()

    #使机器停止的方法
    def brake(self):
        self.cmd_move_pub.publish(g_msgs.Twist())

#用来测试该流程的main函数
if __name__ == '__main__'   :
    rospy.init_node('move_close_line')
    move_cmd = move_to_home()
    move_cmd.go_close_line()