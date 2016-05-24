#!/usr/bin/env python
#author rescuer liao
#get the current position of robot

import rospy
import smach
import math
import smach_ros
from robot_move_pkg import move_a_distance
from robot_move_pkg import turn_an_angular

class first_step(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.move_cmd = move_a_distance.move_a_distance()
        rospy.loginfo('the first step is initial ok!')

    def execute(self, ud):
        self.move_cmd.move_to(x = 2.0)
        return 'successed'


class second_step(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['successed','failed'])
        self.turn_cmd = move_a_distance.move_a_distance()
        rospy.loginfo('the second step is initial ok!')

    def execute(self, ud):
        self.turn_cmd.move_to(y = 0.3)
        return 'successed'

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

