#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author rescuer xu
#投篮项目所需的状态类

import rospy
import smach
import math
import smach_ros
from robot_move_pkg import move_a_distance
from robot_move_pkg import turn_an_angular
from robot_move_pkg import linear_move
from robot_shovel_srv import control_srv
from robot_find_pkg import findball
from robot_find_pkg import find_cylinder_state
from robot_move_pkg import low_speed_linear_move
from robot_move_pkg import move_in_robot
from robot_state_pkg import get_robot_position
from robot_move_pkg import go_along_circle
from robot_find_pkg import find_volleyball
class Return(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.cmd_position = get_robot_position.robot_position_state()
        self.cmd_turn = turn_an_angular.turn_an_angular()
        self.cmd_move = linear_move.linear_move()

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.cmd_move.move_to(x = 1.5-current_x,y = -1.5-current_y)
        self.cmd_turn.turn_to(math.pi)
        return 'successed'



############################################
##############Find column###################
############################################

#向图像服务发出请求，寻找并得到投篮标识柱的位置
class Find_Column(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['column_x', 'column_theta'])
        rospy.loginfo('Start search the column!!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.sleep(1)
        (ud.column_x,ud.column_theta) = find_cylinder_state.find_cylinder_state().get_cylinder_status()
        (ud.column_x,ud.column_theta) = find_cylinder_state.find_cylinder_state().get_cylinder_distance()
        # (ud.column_x,ud.column_theta) = find_cylinder_state.find_cylinder_state().find_cylinder()
        return 'successed'

#在机器运行到标识柱附近时，根据图像服务得到的标识柱位置，调整机器位置，使其位于合适的投篮位置
class Shoot_Adjust_1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'], input_keys=['column_x', 'column_theta'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Shoot Ajdust is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.loginfo("x = %s"%ud.column_x)
        rospy.loginfo("theta = %s"%ud.column_theta)
        self.move_cmd.move_to( yaw=ud.column_theta)
        self.move_cmd.move_to(x = ud.column_x - 2.305)
        rospy.sleep(1)
        (x,column_theta) = find_cylinder_state.find_cylinder_state().find_cylinder()
        self.move_cmd.move_to( yaw= column_theta)
        return 'successed'


class Shoot_Adjust_2(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'], input_keys=['column_x', 'column_theta'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Shoot Ajdust is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.loginfo("x = %s"%ud.column_x)
        rospy.loginfo("theta = %s"%ud.column_theta)
        self.move_cmd.move_to(x = ud.column_x - 2.3)
        self.move_cmd.move_to( yaw=ud.column_theta)

        rospy.sleep(1)
        (x,column_theta) = find_cylinder_state.find_cylinder_state().find_cylinder()
        # self.move_cmd.move_to(x - 2.3)
        self.move_cmd.move_to( yaw= column_theta)
        return 'successed'


############################################
###############Find Ball####################
############################################

#机器逆时针旋转，并不断检测球，并记录下球的位置
# ball_x  球相对与摄像头的x距离
# ball_y  球相对于摄像头的y距离
# ball_theta 球的位置与x轴的夹角
#注意： 摄像头的坐标系与机器的坐标系在x轴上有一定的误差
class Search_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['ball_x', 'ball_y', 'ball_theta'])
        rospy.loginfo('Start search the ball!!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (ud.ball_x,ud.ball_y,ud.ball_theta) = find_volleyball.find_volleyball().find_ball_turn()
        return 'successed'

#顺时针旋转检测球（函数命名有误）
class Search_Ball_CW(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['ball_x', 'ball_y', 'ball_theta'])
        rospy.loginfo('Start search the ball!!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (ud.ball_x,ud.ball_y,ud.ball_theta) = find_volleyball.find_volleyball().find_ball_turn_cw()

        return 'successed'

class Find_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['ball_x', 'ball_y', 'ball_theta'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo('Start Find the ball!!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (ball_x,ball_y,ball_theta) = find_volleyball.find_volleyball().find_volleyball()
        self.move_cmd.turn_to(ball_theta)
        self.move_cmd.move_to(x = math.sqrt(ball_x * ball_x + ball_y * ball_y) - 1.2)
        return 'successed'

#在与三分线同心的圆弧上行进，并边检测球，并记录下球的位置
# ball_x ： 球的x轴坐标
# ball_y ： 球的y轴坐标
# 世界坐标系！！！！
class Search_Ball_By_Line(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['ball_x', 'ball_y'])
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('Start search the ball!!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (x,y,theta) = find_volleyball.find_volleyball().find_ball_by_line()
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        ud.ball_x = current_x + math.cos(current_w + theta) * math.sqrt(x*x + y*y)
        ud.ball_y = current_y + math.sin(current_w + theta) * math.sqrt(x*x + y*y)
        return 'successed'

#在机器找到球后，运动并接近球（球附近1m左右）
class Move_Point(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'], input_keys=['ball_x', 'ball_y', 'ball_theta'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Move Point is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.loginfo("x = %s"%ud.ball_x)
        rospy.loginfo("y = %s"%ud.ball_y)
        self.move_cmd.move_to(y=ud.ball_y)
        self.move_cmd.move_to(x=ud.ball_x-1.05)
        return 'successed'

#投球第三回合底脚捡球调整
class Move_Point_ST(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'], input_keys=['ball_x', 'ball_y', 'ball_theta'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Move Point is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (x,y,theta) = find_volleyball.find_volleyball().find_volleyball()
        rospy.loginfo("x = %s,y = %s ",x,y)
        self.move_cmd.turn_to(theta*0.95)
        self.move_cmd.move_to(x = math.sqrt(x*x+y*y) - 1)
        return 'successed'


#在接近球后（球附近1米左右），调整机器的姿态，使铲子正对球，然后机器运动到球所在位置
class Move_Adjust(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Move Adjust is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.sleep(0.5)
        (x,y,theta) = find_volleyball.find_volleyball().find_volleyball()
        rospy.loginfo("x = %s,y = %s ",x,y)
        self.move_cmd.turn_to(theta*0.95)
        self.move_cmd.move_to(x = math.sqrt(x*x+y*y) - 0.25)
        # self.move_cmd.move_to(y = y)
        # self.move_cmd.move_to(x = x - 0.2 )
        return 'successed'


############################################
################Control#####################
############################################
class Shovel_Control_Down(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo("the Shovel_Control_Down is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_shovel.control_shovel(control_type= 3)
        return 'successed'

class Shovel_Control_Up(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo("the Shovel_Control_Up is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_shovel.control_shovel(control_type= 4)
        return 'successed'

#投篮
class Shoot(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.cmd_shoot = control_srv.shootControlSrv()
        rospy.loginfo('the first shoot is initial ok!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.sleep(1)
        self.cmd_shoot.shoot_ball()
        return 'successed'

#将球铲起
class Shovel(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo('the first shovel is initial ok!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_shovel.control_shovel(control_type=0)
        rospy.sleep(0.5)
        return 'successed'



############################################
###########shoot_ball_first#################
############################################

#前进到定位柱附近
class Move_Point_To_Shoot(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.move_cmd = linear_move.linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        rospy.loginfo("the Move Point_Pro is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.move_cmd.move_to(x = 2.6)
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 7.85 - current_x,y = -8.5 - current_y)
        self.turn_cmd.turn_to(-math.pi/5)
        return 'successed'

#前进到中圈置球区附近
class Move_To_Find_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo("the Move To Find BAll is initial Ok!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 6.0 - current_x,y = -1.3 - current_y)
        self.turn_cmd.turn_to( -math.pi/8 )
        return 'successed'

#再次移动到定位柱附近，准备投篮
class Adjust_To_Shoot(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        rospy.loginfo('the Adjust is initial OK!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 7.85 - current_x,y = -8.8 - current_y)
        self.turn_cmd.turn_to(-math.pi/4.5)
        return 'successed'

############################################
#######shoot_ball_second and third##########
############################################

#先移动到三分线上的捡球位置，在移动到定位柱附近
class Shoot_Adjust_Second(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'],input_keys=['ball_x', 'ball_y'])
        self.move_cmd = linear_move.linear_move()
        self.move_cmd_low = low_speed_linear_move.low_speed_linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        self.turn_cmd = turn_an_angular.turn_an_angular()

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = ud.ball_x - current_x,y = ud.ball_y - current_y)
        # self.move_cmd.move_to(x = ud.ball_x - current_x - 1,y = ud.ball_y - current_y + 1)
        # self.move_cmd_low.move_to(x = 1, y = -1)
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        self.move_cmd.move_to(x = 7.85 - current_x,y = -8.8 - current_y,yaw= -math.pi/7 -current_w)
        self.turn_cmd.turn_to(-math.pi/4.5)
        return "successed"
        # self.turn_cmd.turn_to(-math.pi / 8)

class Shoot_Adjust_Third(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'],input_keys=['ball_x', 'ball_y'])
        self.move_cmd = linear_move.linear_move()
        self.move_cmd_low = low_speed_linear_move.low_speed_linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        self.turn_cmd = turn_an_angular.turn_an_angular()

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 1.2 - current_x,y = -8.8-current_y)
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        self.move_cmd.move_to(x = 7.85 - current_x,y = -9.0 - current_y,yaw= -math.pi/4.3 -current_w)
        return "successed"

############################################
###########shoot_ball_second################
############################################

#前进到三分线附近（三分置球区的最左端）
class Move_To_Three_Point_Line(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo("the Move_To_Three_Point_Line is initial OK!")

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.move_cmd.move_to(x = 2.6)
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        #定位柱的位置 8, -10.925
        angular = math.atan2( -10.925- (-3.7),8 - 4.25)
        self.move_cmd.move_to(x = 1.75,y = -3.8,yaw = angular - current_w)
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        angular = math.atan2( -10.925- current_y,8 - current_x)
        self.turn_cmd.turn_to(angular)
        return 'successed'

#前进到中圈置球区附近
class Move_To_Another_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.cmd_turn = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('the Move To Another Ball is initial OK!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        self.move_cmd.move_to(x = 5.0-current_x,y = -0.68-current_y,yaw = 0 - current_w)
        # self.cmd_turn.turn_to(0)
        return 'successed'



#回到三分线上捡球的位置（以此避免撞到三分线上的篮球）
# class Three_Line_Out(smach.State):
#     def __init__(self):
#         smach.State.__init__(self,outcomes=['successed','failed'],input_keys=['ball_x', 'ball_y'])
#         self.move_cmd = linear_move.linear_move()
#         self.move_cmd_low = low_speed_linear_move.low_speed_linear_move()
#         self.cmd_position = get_robot_position.robot_position_state()
#
#     def execute(self, ud):
#         if self.preempt_requested():
#             self.service_preempt()
#             return 'failed'
#         (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
#         self.move_cmd.move_to(x = ud.ball_x - current_x,y = ud.ball_y - current_y)
#         self.move_cmd_low.move_to(x = -1 ,y = 1)
#         return 'successed'

class Three_Line_Out_1(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'],output_keys=['ball_x', 'ball_y'])
        self.move_cmd = linear_move.linear_move()
        self.move_cmd_low = low_speed_linear_move.low_speed_linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        self.turn_cmd = turn_an_angular.turn_an_angular()

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        current_w = self.cmd_position.get_robot_current_w()
        self.move_cmd_low.move_to(x = -0.5,y = 2.4,yaw = math.pi/2 - current_w)
        self.turn_cmd.turn_to(math.pi/2)
        (ball_x,ball_y,ball_theta,has_ball) = find_volleyball.find_volleyball().find_ball()
        rospy.loginfo('x = %s,y = %s',ball_x,ball_y)
        if math.fabs(ball_y) < 0.8 and has_ball == True:
            self.move_cmd.move_to(x = - ball_y -0.8)
        (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
        ud.ball_x = current_x + math.cos(current_w + ball_theta) * math.sqrt(ball_x*ball_x + ball_y*ball_y) - 0.5
        ud.ball_y = current_y + math.sin(current_w + ball_theta) * math.sqrt(ball_x*ball_x + ball_y*ball_y)

        return 'successed'


# class Three_Line_Out_2(smach.State):
#     def __init__(self):
#         smach.State.__init__(self,outcomes=['successed','failed'],output_keys=['ball_x', 'ball_y'])
#         self.move_cmd = linear_move.linear_move()
#         self.move_cmd_low = low_speed_linear_move.low_speed_linear_move()
#         self.cmd_position = get_robot_position.robot_position_state()
#         self.turn_cmd = turn_an_angular.turn_an_angular()
#
#     def execute(self, ud):
#         if self.preempt_requested():
#             self.service_preempt()
#             return 'failed'
#         # current_w = self.cmd_position.get_robot_current_w()
#         self.turn_cmd.turn_to(math.pi)
#         (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
#         self.move_cmd_low.move_to(x = 2.7 - current_x,y = -9.3 -current_y)
#         (ball_x,ball_y,ball_theta,has_ball) = find_volleyball.find_volleyball().find_ball()
#         if has_ball == True and math.fabs(ball_y) < 0.8:
#             self.move_cmd.move_to(y =  -ball_y + 0.8)
#         (current_x,current_y,current_w) = self.cmd_position.get_robot_current_x_y_w()
#         ud.ball_x = current_x + math.cos(current_w + ball_theta) * math.sqrt(ball_x*ball_x + ball_y*ball_y)
#         ud.ball_y = current_y + math.sin(current_w + ball_theta) * math.sqrt(ball_x*ball_x + ball_y*ball_y) + 0.8
#
#         return 'successed'

############################################
###########shoot_ball_third#################
############################################


#移动到底脚置球区附近
class Move_To_Another_Ball_Foot(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.cmd_turn = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('the Move To Another Ball Foot is initial OK!')

    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_turn.turn_to(-math.pi)
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 1.4 - current_x,y = -9.6-current_y)
        self.cmd_turn.turn_to(-(5.5/6.0) * math.pi)
        rospy.sleep(1)
        return 'successed'

#移动到定位柱附近
class Move_To_Find_Column(smach.State):

    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        self.turn_cmd = turn_an_angular.turn_an_angular()
    def execute(self, ud):
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 7.85 - current_x,y = -8.8 - current_y)
        # self.turn_cmd.turn_to(-math.pi / 8)
        return 'successed'
