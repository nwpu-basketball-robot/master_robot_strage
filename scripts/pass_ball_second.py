#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author rescuer xu
#传球项目2的状态机
#流程： 前进到三分线附近 -> 自转并检测篮球 -> 检测到球后接近球 -> 二次检测球并调整角度 -> 铲球 -> 调整传球方向 -> 传球
#      -> 移动到中间置球区附近 ->在自转并检测球（为检测到时移动到另一个点并再次执行该步骤） -> 检测到球后接近球 -> 二次检测并调整 -> 铲球 -> 调整传球方向 -> 传球 —> 回家
import rospy
import smach
import math
import smach_ros
from std_msgs.msg import Empty
from robot_state_class.first_project_state import *

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

def pass_second():
    # rospy.loginfo("!!!!!!!!!!!!!!!!!!!!!!!!!")


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
        rospy.loginfo("!!!!!!!!!!!!!!!!!!!!!!!!!")
        with sm_top:

            start = smach.Concurrence(outcomes=['successed','failed'],
                                   default_outcome='failed',
                                   outcome_map={'successed':
                                       { 'SHOVEL_CONTROL_DOWN':'successed',
                                         'MOVE_TO_THREE_POINT_LINE':'successed'}})


            with start:
                smach.Concurrence.add("SHOVEL_CONTROL_DOWN",Shovel_Control_Down())

                smach.Concurrence.add('MOVE_TO_THREE_POINT_LINE',Move_To_Three_Point_Line())

            smach.StateMachine.add("START",start,
                               transitions={"successed":"FindBall1",
                                            "failed":"failed"})

            smach.StateMachine.add("FindBall1", Search_Ball(),
                               transitions={"successed": "MOVE_POINT1",
                                            "failed": "failed"},
                               remapping={'ball_x': 'ball_location_x',
                                          'ball_y': 'ball_location_y',
                                          'ball_theta': 'ball_theta'})

            smach.StateMachine.add('MOVE_POINT1',Move_Point(),
                                       transitions={'successed': 'MOVE_ADJUST1',
                                                    'failed': 'failed'},
                                       remapping={'ball_x': 'ball_location_x',
                                                  'ball_y': 'ball_location_y',
                                                  'ball_theta': 'ball_theta'})

            smach.StateMachine.add("MOVE_ADJUST1",Move_Adjust(),
                               transitions={"successed":"SHOVEL1",
                                            "failed":"failed"})

            smach.StateMachine.add('SHOVEL1',Shovel(),
                               transitions={'successed': 'SHOOT_ADJUST1',
                                            'failed': 'failed'})

            smach.StateMachine.add('SHOOT_ADJUST1',Shoot_Adjust_Second(),
                               transitions={'successed':'SHOOT1',
                                            'failed':'failed'})

            smach.StateMachine.add('SHOOT1',Shoot(),
                               transitions={'successed':'MOVE_POINT_PRO_1',
                                            'failed':'failed'})


            smach.StateMachine.add('MOVE_POINT_PRO_1',Move_To_Another_Ball_1(),
                               transitions={'successed':'FindBall2',
                                            'failed':'failed'})

            smach.StateMachine.add("FindBall2", Search_Ball(),
                               transitions={"successed": "MOVE_POINT2",
                                            "failed": "MOVE_POINT_PRO_2"},
                               remapping={'ball_x': 'ball_location_x',
                                          'ball_y': 'ball_location_y',
                                          'ball_theta': 'ball_theta'})

            smach.StateMachine.add("MOVE_POINT_PRO_2", Move_To_Another_Ball_2(),
                               transitions={"successed": "FindBall3",
                                            "failed": "failed"})

            smach.StateMachine.add("FindBall3", Search_Ball_CW(),
                               transitions={"successed": "MOVE_POINT2",
                                            "failed": "failed"},
                               remapping={'ball_x': 'ball_location_x',
                                          'ball_y': 'ball_location_y',
                                          'ball_theta': 'ball_theta'})

            smach.StateMachine.add('MOVE_POINT2',Move_Point(),
                                       transitions={'successed': 'MOVE_ADJUST2',
                                                    'failed': 'failed'},
                                       remapping={'ball_x': 'ball_location_x',
                                                  'ball_y': 'ball_location_y',
                                                  'ball_theta': 'ball_theta'})

            smach.StateMachine.add("MOVE_ADJUST2",Move_Adjust(),
                               transitions={"successed":"SHOVEL2",
                                            "failed":"failed"})

            smach.StateMachine.add('SHOVEL2',Shovel(),
                                       transitions={'successed': 'SHOOT_ADJUST2',
                                                    'failed': 'failed'})
        
            smach.StateMachine.add('SHOOT_ADJUST2',Shoot_Adjust(),
                               transitions={'successed':'SHOOT2',
                                            'failed':'failed'})
        
            smach.StateMachine.add('SHOOT2',Shoot(),
                               transitions={'successed':'SHOVEL_CONTROL_UP',
                                            'failed':'failed'})

            smach.StateMachine.add("SHOVEL_CONTROL_UP",Shovel_Control_Up(),
                               transitions={"successed":"RETURN",
                                            "failed":"failed"})

            smach.StateMachine.add('RETURN',Return(),transitions={'successed':'successed',
                                                              'failed':'failed'})
        smach.Concurrence.add('RUN',sm_top)
        smach.Concurrence.add('STOP', smach_ros.MonitorState("/sm_reset", Empty, monitor_cb))

    preemt.execute()

if __name__ == '__main__':
    rospy.init_node('passBall_second')
    pass_second()