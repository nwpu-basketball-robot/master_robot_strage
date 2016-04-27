#!/usr/bin/env python
#coding:utf-8



#Team Unware Basketball Robot NWPU
#状态机测试代码

#author=liao-zhihan
#first_debug_date=2016-03
#第一次测试通过


import rospy
import smach
import math
import smach_ros
from robot_move_pkg import move_a_distance
from robot_move_pkg import turn_an_angular


#朝正前方移动一段距离
class first_step(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = move_a_distance.move_a_distance()
        rospy.loginfo('the first step is initial ok!')

    def execute(self, ud):
        self.move_cmd.move_to(x = 2.0)
        return 'successed'

#朝右边移动一段距离
class second_step(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.turn_cmd = move_a_distance.move_a_distance()
        rospy.loginfo('the second step is initial ok!')

    def execute(self, ud):
        self.turn_cmd.move_to(y = 0.3)
        return 'successed'

#后退一段距离
class third_step(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = move_a_distance.move_a_distance()
        rospy.loginfo('the third step is initial ok!')

    def execute(self, ud):
        self.move_cmd.move_to(x = -0.8)
        return 'successed'

if __name__ == '__main__':
    rospy.init_node('test')
    test = smach.StateMachine(outcomes=['successed','failed'])
    with test:
        smach.StateMachine.add('FIRST_STEP',
                           first_step(),
                           transitions={'successed':'SECOND_STEP',
                                        'failed':'failed'})
        smach.StateMachine.add('SECOND_STEP',
                           second_step(),
                           transitions={'successed':'THIRD_STEP',
                                        'failed':'failed'})
        smach.StateMachine.add('THIRD_STEP',
                           third_step(),
                           transitions={'successed':'successed',
                                        'failed':'failed'})
    test.execute()

