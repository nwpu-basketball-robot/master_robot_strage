#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author rescuer xu
#投篮项目3的状态机
#流程： 前进到三分线附近 -> 自转并检测篮球 -> 检测到球后接近球 -> 二次检测球并调整角度（记录球所在位置，世界坐标系）-> 铲球 -> 前进到定位柱附近 -> 检测定位柱 -> 调整角度对准定位柱  -> 投篮
#      前进到三分线捡球处（防止撞到排球）-> 移动到底脚置球区附近 ->在自转并检测球 -> 检测到球后接近球 -> 二次检测并调整 -> 铲球 -> 前进到三分线捡球处（防止撞到排球） -> 前进到定位柱附近
#      -> 检测定位柱 -> 调整角度对准定位柱  -> 投篮

import rospy
import smach
import math
import smach_ros
from std_msgs.msg import Empty
from robot_state_class.second_project_state import *

def monitor_cb(ud, msg):
    return False

def out_cb(outcome_map):
    if outcome_map['STOP'] == 'invalid':
        rospy.loginfo("invalid !!!!!!!!!")
        return 'failed'
    else:
        rospy.loginfo("asdqewqeweqrq")
        return 'successed'

def child_term_cb(outcome_map):
    if outcome_map['STOP'] == 'invalid':
        return True
    if outcome_map['RUN']:
        return True
    return False

def shoot_third():

    preemt = smach.Concurrence(outcomes=['successed','failed'],
                                   default_outcome='failed',child_termination_cb=child_term_cb,
                                   outcome_cb=out_cb)
    with preemt:
        sm_top = smach.StateMachine(outcomes=['successed', 'failed'])
        sm_top.userdata.ball_location_x = 0
        sm_top.userdata.ball_location_y = 0
        sm_top.userdata.ball_theta = 0
        sm_top.userdata.column_x = 0
        sm_top.userdata.column_theta = 0
        sm_top.userdata.enter_location_x = 0
        sm_top.userdata.enter_location_y = 0
        with sm_top:

            start = smach.Concurrence(outcomes=['successed','failed'],
                                   default_outcome='failed',
                                   outcome_map={'successed':
                                       { 'SHOVEL_CONTROL_DOWN':'successed',
                                         'MOVE_TO_THREE_POINT_LINE':'successed'}})

            smach.StateMachine.add("START",start,
                               transitions={"successed":"FindBall1",
                                            "failed":"failed"})
            with start:
                smach.Concurrence.add("SHOVEL_CONTROL_DOWN",Shovel_Control_Down())

                smach.Concurrence.add('MOVE_TO_THREE_POINT_LINE',Move_To_Three_Point_Line())


            smach.StateMachine.add("FindBall1", Search_Ball_By_Line(),
                               transitions={"successed": "MOVE_ADJUST1",
                                            "failed": "failed"},
                               remapping={'ball_x': 'enter_location_x',
                                          'ball_y': 'enter_location_y'})


            smach.StateMachine.add("MOVE_ADJUST1",Move_Adjust(),
                               transitions={"successed":"SHOVEL1",
                                            "failed":"failed"})

            smach.StateMachine.add('SHOVEL1',Shovel(),
                                       transitions={'successed': 'MOVE_TO_FIND_COLUMN_1',
                                                    'failed': 'failed'})

            smach.StateMachine.add("MOVE_TO_FIND_COLUMN_1",Move_To_Find_Column(),
                               transitions={'successed':'FIND_COLUMN1',
                                            'failed':'failed'})


            smach.StateMachine.add('FIND_COLUMN1',Find_Column(),
                               transitions={'successed':'SHOOT_ADJUST1',
                                            'failed':'failed'},
                                        remapping={'column_x': 'column_x',
                                                  'column_theta': 'column_theta'})

            smach.StateMachine.add('SHOOT_ADJUST1',Shoot_Adjust_1(),
                               transitions={'successed':'SHOOT1',
                                            'failed':'failed'},
                                        remapping={'column_x': 'column_x',
                                                  'column_theta': 'column_theta'})


            smach.StateMachine.add('SHOOT1',Shoot(),
                               transitions={'successed':'MOVE_POINT_PRO',
                                            'failed':'failed'})
            #
            # smach.StateMachine.add('THREE_LINE_OUT',Three_Line_Out_2(),
            #                    transitions={'successed':'MOVE_POINT_PRO',
            #                                 'failed':'failed'},
            #                    remapping={'ball_x': 'enter_location_x',
            #                               'ball_y': 'enter_location_y'})

            smach.StateMachine.add('MOVE_POINT_PRO',Move_To_Another_Ball_Foot(),
                               transitions={'successed':'FindBall2',
                                            'failed':'failed'})

            smach.StateMachine.add("FindBall2", Find_Ball(),
                               transitions={"successed": "MOVE_ADJUST2",
                                            "failed": "failed"},
                               remapping={'ball_x': 'ball_location_x',
                                          'ball_y': 'ball_location_y',
                                          'ball_theta': 'ball_theta'})
            #
            # smach.StateMachine.add('MOVE_POINT2',Move_Point(),
            #                            transitions={'successed': 'MOVE_ADJUST2',
            #                                         'failed': 'failed'},
            #                            remapping={'ball_x': 'ball_location_x',
            #                                       'ball_y': 'ball_location_y',
            #                                       'ball_theta': 'ball_theta'})

            smach.StateMachine.add("MOVE_ADJUST2",Move_Adjust(),
                               transitions={"successed":"SHOVEL2",
                                            "failed":"failed"})

            smach.StateMachine.add('SHOVEL2',Shovel(),
                                       transitions={'successed': 'ADJUST2',
                                                    'failed': 'failed'})

            smach.StateMachine.add('ADJUST2',Shoot_Adjust_Third(),
                               transitions={'successed':'FIND_COLUMN2',
                                            'failed':'failed'})

            smach.StateMachine.add('FIND_COLUMN2',Find_Column(),
                               transitions={'successed':'SHOOT_ADJUST2',
                                            'failed':'failed'},
                                        remapping={'column_x': 'column_x',
                                                  'column_theta': 'column_theta'})

            smach.StateMachine.add('SHOOT_ADJUST2',Shoot_Adjust_2(),
                               transitions={'successed':'SHOOT2',
                                            'failed':'failed'},
                                        remapping={'column_x': 'column_x',
                                                  'column_theta': 'column_theta'})

            smach.StateMachine.add('SHOOT2',Shoot(),
                               transitions={'successed':'successed',
                                            'failed':'failed'})


        smach.Concurrence.add('RUN',sm_top)
        smach.Concurrence.add('STOP', smach_ros.MonitorState("/sm_reset", Empty, monitor_cb))

    preemt.execute()

if __name__ == '__main__':
    rospy.init_node('shootBall_third')
    shoot_third()