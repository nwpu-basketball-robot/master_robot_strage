#! /usr/bin/env python
# author = rescuer_liao
# get the current position of robot

import rospy
import roslib
import tf
import math
import tf.transformations as tf_transfer
import geometry_msgs.msg as g_msgs


class robot_position_state(object):
    def __init__(self):
        self.base_frame = rospy.get_param("base_frame_name","base_link")
        self.odom_frame = rospy.get_param("odom_frame_name","odom")
        self.tf_listener = tf.TransformListener()

        rospy.loginfo("[robot_state_pkg]->robot_position_state module is waiting for the tf between"
                      " %s and %s "%(self.base_frame , self.odom_frame))

        warn_time = 0
        wait_tf_start_time = rospy.Time.now()
        while not rospy.is_shutdown():
            is_tf_ok = self.tf_listener.canTransform(self.odom_frame,self.base_frame,rospy.Time())
            current_time = rospy.Time.now()
            if is_tf_ok:
                rospy.loginfo('[robot_state_pkg]->robot_position_state module the transform between '
                              '%s and %s is ok!!'%(self.odom_frame , self.base_frame))
                break
            if current_time.to_sec()-wait_tf_start_time.to_sec() >= 10.0 and warn_time == 0:
                warn_time += 1
                rospy.logwarn('[robot_state_pkg]->robot_position_state module the transform between '
                              '%s and %s is time out!!'%(self.odom_frame , self.base_frame))
                rospy.logwarn('[robot_state_pkg]->robot_position_state module this information only '
                              'warn once ,please check the odom !!!')

    def get_robot_current_x_y_w(self):
         t = self.tf_listener.getLatestCommonTime(self.base_frame, self.odom_frame)
         position, quaternion = self.tf_listener.lookupTransform(self.odom_frame , self.base_frame,t)

         roll,pitch,yaw = tf.transformations.euler_from_quaternion(quaternion)
#         print 'x = ' ,position[0] ,'y = ', position[1],'yaw =', yaw
         return position[0],position[1],yaw

    def get_robot_current_x_y(self):
        x , y , yaw = self.get_robot_current_x_y_w()
        return x,y

    def get_robot_current_x(self):
        x , y , yaw = self.get_robot_current_x_y_w()
        return x

    def get_robot_current_y(self):
        x , y , yaw = self.get_robot_current_x_y_w()
        return y

    def get_robot_current_yaw(self):
        x , y , yaw = self.get_robot_current_x_y_w()
        return yaw

if __name__ == '__main__':
    rospy.init_node('test')
    a = robot_position_state()
    s = a.get_robot_current_x()
    print s
