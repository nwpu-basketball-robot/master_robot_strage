#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author rescuer xu
#传球项目所需的状态类

import rospy
import smach
import math
import smach_ros
from robot_move_pkg import move_a_distance
from robot_move_pkg import turn_an_angular
from robot_move_pkg import linear_move
from robot_shovel_srv import control_srv
from robot_find_pkg import findball
from robot_move_pkg import low_speed_linear_move
from robot_move_pkg import move_in_robot
from robot_state_pkg import get_robot_position
from robot_move_pkg import go_close_line

#先回到边线附近，然后执行回家的步骤（具体过程见go_close_line.py文件中）
class Return(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.cmd_position = get_robot_position.robot_position_state()
        self.cmd_turn = turn_an_angular.turn_an_angular()
        self.cmd_move = linear_move.linear_move()
        self.cmd_return = go_close_line.move_to_home()
        rospy.loginfo('The Return is initial ok!!!!')
        # self.cmd_move_robot = move_in_robot.linear_move()

    def execute(self, ud):
        rospy.loginfo('Start Return to home!!')
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.cmd_move.move_to(x = 2.5-current_x,y = -2-current_y)
        # self.cmd_move.move_to(y =  -current_y)
        self.cmd_turn.turn_to(math.pi)
        self.cmd_return.go_close_line()
        # self.cmd_move.move_to(x = -2.6)

        return 'successed'

#铲球后调整机器姿态，使其正对传球目标区域中心
class Shoot_Adjust(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('The Shoot_Adjust is initial ok!!!!')

    def execute(self, ud):
        rospy.loginfo('Start Shoot Adjust')
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 6.3 - current_x,y = -0.65 - current_y)
        angular = math.atan2((-6.7 - current_y),(8.5 - current_x))
        self.turn_cmd.turn_to(angular)
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


    def execute(self, ud):
        rospy.loginfo('Start search the ball!!')
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (ud.ball_x,ud.ball_y,ud.ball_theta,has_ball) = findball.findBall().find_ball_turn_cw(math.pi)
        if has_ball == True:
            return 'successed'
        else:
            return 'failed'

#顺时针旋转检测球（函数命名有误）
class Search_Ball_CW(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['ball_x', 'ball_y', 'ball_theta'])


    def execute(self, ud):
        rospy.loginfo('Start search the ball!!')
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (ud.ball_x,ud.ball_y,ud.ball_theta) = findball.findBall().find_ball_turn(math.pi/1.5)
        return 'successed'

#直接获取球的位置
class Find_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed']
                             , output_keys=['ball_x', 'ball_y', 'ball_theta'])


    def execute(self, ud):
        rospy.loginfo('Start Find the ball!!')
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (ud.ball_x,ud.ball_y,ud.ball_theta) = findball.findBall().find_ball()
        return 'successed'

#在机器找到球后，运动并接近球（球附近1m左右）
class Move_Point(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'], input_keys=['ball_x', 'ball_y', 'ball_theta'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Move Point is initial OK!")

    def execute(self, ud):
        rospy.loginfo('Start Move_Point!!!!!')
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.loginfo("x = %s"%ud.ball_x)
        rospy.loginfo("y = %s"%ud.ball_y)
        self.move_cmd.move_to(y = ud.ball_y - 0.3)
        self.move_cmd.move_to(x=ud.ball_x-1)
        return 'successed'

#在接近球后（球附近1米左右），调整机器的姿态，使铲子正对球，然后机器运动到球所在位置
class Move_Adjust(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.move_cmd = move_in_robot.linear_move()
        rospy.loginfo("the Move Adjust is initial OK!")

    def execute(self, ud):
        rospy.loginfo("Start Move Adjust to close ball!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (x,y,theta) = findball.findBall().find_ball()
        rospy.loginfo("x = %s,y = %s ",x,y)
        self.move_cmd.turn_to(theta)
        self.move_cmd.move_to(x = math.sqrt(x*x+y*y) - 0.22)
        # self.move_cmd.move_to(y = y)
        # self.move_cmd.move_to(x = x - 0.2 )
        return 'successed'


############################################
################Control#####################
############################################

#将铲子放下（用于出发时）
class Shovel_Control_Down(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo("the Shovel_Control_Down is initial OK!")

    def execute(self, ud):
        rospy.loginfo("Start Shovel Down!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_shovel.control_shovel(control_type= 3)
        return 'successed'

#将铲子升起(用于回家时)
class Shovel_Control_Up(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo("the Shovel_Control_Up is initial OK!")

    def execute(self, ud):
        rospy.loginfo("Start Shovel Up!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        rospy.sleep(1)
        self.cmd_shovel.control_shovel(control_type= 4)
        # rospy.sleep(0.5)
        return 'successed'

#投篮
class Shoot(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.cmd_shoot = control_srv.shootControlSrv()
        rospy.loginfo('the shoot is initial ok!')

    def execute(self, ud):
        rospy.loginfo("Start Shoot!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        # rospy.sleep(0.5)
        self.cmd_shoot.shoot_ball()
        rospy.sleep(1)
        return 'successed'

#将球铲起
class Shovel(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo('the first shovel is initial ok!')

    def execute(self, ud):
        rospy.loginfo("Start Shovel ball!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_shovel.control_shovel(control_type=0)
        rospy.sleep(0.5)
        return 'successed'



############################################
###########pass_ball_first##################
############################################

#出发时直接前进到传球区域内准备接下来的传球
class Move_Point_To_Shoot(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['successed', 'failed'])
        self.move_cmd = linear_move.linear_move()
        # self.move_cmd = move_in_robot.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo("the Move Point_Pro is initial OK!")

    def execute(self, ud):
        rospy.loginfo("Start Move_Point_To_Shoot!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        # 根据实际情况修改
        self.move_cmd.move_to(x = 6.3,y = -0.65)
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        angular = math.atan2( -6.7 - current_y,8.5 - current_x) #需要修改
        self.turn_cmd.turn_to(angular)
        # self.move_cmd.turn_to( 3 * math.pi / 4)
        return 'successed'

#在第一次传球结束后，移动到合适位置，以准备检测另一个球
class Move_To_Find_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_shovel = control_srv.shovelControlSrv()
        rospy.loginfo("the Move To Find BAll is initial Ok!")

    def execute(self, ud):
        rospy.loginfo("Start Move_To_Find_Ball!!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.move_cmd.move_to(x = -1.2)
        self.turn_cmd.turn_to(-math.pi/6)
        return 'successed'



############################################
#######pass_ball_second and third###########
############################################

#移动到三分线附近
class Move_To_Three_Point_Line(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        rospy.loginfo("the Move_To_Three_Point_Line is initial OK!")

    def execute(self, ud):
        rospy.loginfo("Start Move_To_Three_Point_Line!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.move_cmd.move_to(x = 2.6)
        self.move_cmd.move_to(y = -4.8,yaw = -math.pi/1.8)
        return 'successed'

############################################
###########pass_ball_third##################
############################################

#第一个球传球结束后，移动到底脚置球区附近
class Move_To_Another_Ball(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('the Move To Another Ball is initial OK!')

    def execute(self, ud):
        rospy.loginfo("Start Move_To_Another_Ball!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 1.5 - current_x,y = -8.7 - current_y)
        self.turn_cmd.turn_to(- math.pi /2.5)
        return 'successed'

#移动到合适的位置准备传球
class Shoot_Adjust_Third(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.move_cmd = linear_move.linear_move()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('the Shoot_Adjust_Second is initial OK!')

    def execute(self, ud):
        rospy.loginfo("Start hoot_Adjust_Second!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(yaw = math.pi/3)
        self.move_cmd.move_to(x = 3.25 - current_x,y = -4.7 - current_y)
        angular = -math.atan2((-6.7 - current_y),(8 - current_x))
        self.turn_cmd.turn_to(angular)
        return 'successed'

############################################
###########pass_ball_second#################
############################################

#第一个球传球结束后移动到中心置球区域
class Move_To_Another_Ball_1(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('the Move To Another Ball 1 is initial OK!')

    def execute(self, ud):
        rospy.loginfo("Start Move To Another Ball 1!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'

        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 6.2-current_x,y = -0.6-current_y)
        self.turn_cmd.turn_to(-math.pi/6)
        return 'successed'

#在第一次移动检测后没有检测到球的情况下移动到另一个个点，再进行一次检测
class Move_To_Another_Ball_2(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = linear_move.linear_move()
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        rospy.loginfo('the Move To Another Ball 2 is initial OK!')

    def execute(self, ud):
        rospy.loginfo("Start Move To Another Ball 2!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'

        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        self.move_cmd.move_to(x = 5.5-current_x,y = 0.3-current_y)
        self.turn_cmd.turn_to(0)
        return 'successed'

#调整传球角度
class Shoot_Adjust_Second(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.turn_cmd = turn_an_angular.turn_an_angular()
        self.cmd_position = get_robot_position.robot_position_state()
        self.cmd_move_robot = move_in_robot.linear_move()
        rospy.loginfo('the Shoot_Adjust_Third is initial OK!')

    def execute(self, ud):
        rospy.loginfo("Start Shoot_Adjust_Third!!!!")
        if self.preempt_requested():
            self.service_preempt()
            return 'failed'
        self.cmd_move_robot.move_to(x = -0.5)
        (current_x,current_y) = self.cmd_position.get_robot_current_x_y()
        angular = math.atan2((-6.7 - current_y),(8 - current_x))
        self.turn_cmd.turn_to(angular)
        return 'successed'
