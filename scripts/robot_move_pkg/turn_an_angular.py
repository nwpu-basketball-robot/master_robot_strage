#!/usr/bin/env python
# author = hao , rescuer liao
#send a angular to move

#append the robot state pkg to the python path
import config
import math
import sys
sys.path.append(config.robot_state_pkg_path)
import robot_state_pkg.get_robot_position as robot_state
import rospy
import geometry_msgs.msg as g_msgs

class turn_an_angular(object):
    def __init__(self):
        rospy.loginfo('[robot_mo    ve_pkg]->move_an_angular is initial')
        self.robot_state = robot_state.robot_position_state()
        self.speed = config.turn_angular_speed
        self.stop_tolerance = math.radians(config.turn_augular_stop_tolerance)
        self.turn_scale = config.turn_angular_scale
        self.cmd_vel_pub = rospy.Publisher('/cmd_move' , g_msgs.Twist , queue_size=100)

    def brake(self):
        self.cmd_vel_pub.publish(g_msgs.Twist())

    def start_turn(self , goal_angular = 0.0):
        rospy.loginfo('[robot_move_pkg]->move_an_angular will turn %s'%goal_angular)
        rospy.on_shutdown(self.brake) #callback function
        current_angular = start_angular = self.robot_state.get_robot_current_yaw()
        is_arrive_goal = False
        r = rospy.Rate(100)
        delta_angular = current_angular - start_angular

        delta_upper_limit = abs(goal_angular) + self.stop_tolerance
        delta_lower_limit = abs(goal_angular) - self.stop_tolerance

        move_velocity = g_msgs.Twist()
        while not rospy.is_shutdown() and not is_arrive_goal:
            if abs(delta_angular)<=delta_upper_limit and abs(delta_angular) >= delta_lower_limit:
                self.brake()
                is_arrive_goal = True
                break

            if goal_angular > 0:
                move_velocity.angular.z = self.speed
            else:
                move_velocity.angular.z = -self.speed
            self.cmd_vel_pub.publish(move_velocity)
            delta_angular = self.robot_state.get_robot_current_yaw() - start_angular
            r.sleep()


    def turn(self , angular = 0.0):
        self.start_turn(self.normalize_angle(angular))

    def normalize_angle(self,angular):
        while angular > math.pi:
            angular -= 2.0 * math.pi
        while angular < -math.pi:
            angular += 2.0 * math.pi
        print('current angular is %s'%angular)
        return angular


if __name__ == '__main__':
    rospy.init_node('turn_angular')
    a = turn_an_angular()
    a.turn(math.radians(-30.0))

sys.path.remove(config.robot_state_pkg_path)
