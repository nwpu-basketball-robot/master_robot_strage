#!/usr/bin/env python

# author = hao , rescuer liao
#send a distance to move

#append the robot state pkg to the python path
import math
import rospy
import config
import sys
sys.path.append(config.robot_state_pkg_path)
import robot_state_pkg.get_robot_position as robot_state
import geometry_msgs.msg as g_msgs

class move_a_distance(object):
    def __init__(self):
        rospy.loginfo('[robot_move_pkg]->move_a_distance is initial')
        self.robot_state = robot_state.robot_position_state()
        self.speed = config.linear_move_speed
        self.stop_tolerance = config.linear_move_stop_tolerance
        self.cmd_move_pub = rospy.Publisher('/cmd_move',g_msgs.Twist , queue_size=100)

    def brake(self):
        move_velocity = g_msgs.Twist()
        move_velocity.linear.x = 0.0
        move_velocity.linear.y = 0.0
        self.cmd_move_pub.publish(move_velocity)

    def move_to(self , x = 0 , y = 0):
        try:
            if x!=0 and y!=0:
                raise Exception('[robot_move_pkg]->move_a_distance can not send the '
                                'distance x and y at the same time, use move_to_point instead!')
        except Exception,e:
            print e

        if x==0:
            rospy.loginfo('[robot_move_pkg]->move_a_distance will move to y = %s'%y)
            self.start_move(y = y)
        else:
            rospy.loginfo('[robot_move_pkg]->move_a_distance will move to x = %s'%x)
            self.start_move(x = x)

    def start_move(self,x = 0 , y = 0):
        rospy.on_shutdown(self.brake) #set callback function
        r = rospy.Rate(100)
        move_on_x = (y==0)
        start_x,start_y = self.robot_state.get_robot_x_y()
        current_x , current_y = start_x , start_y

        move_velocity = g_msgs.Twist()
        is_arrive_goal = False
        while not rospy.is_shutdown() and is_arrive_goal is not True:
            if not is_arrive_goal:
                current_x,current_y = self.robot_state.get_robot_current_x_y()
                distance_has_moved =  math.sqrt(pow(current_x - start_x,2) + pow(current_y - start_y,2))
                if move_on_x:
                    distance_to_arrive_goal_x = abs(x) - distance_has_moved
                    if abs(distance_to_arrive_goal_x) <= self.stop_tolerance:
                        is_arrive_goal = True
                        break
                    if x > 0:
                        move_velocity.linear.x = math.copysign(self.speed , distance_to_arrive_goal_x)
                    else:
                        move_velocity.linear.x = math.copysign(self.speed ,-distance_to_arrive_goal_x)
                    move_velocity.linear.y = 0.0

                else :
                    distance_to_arrive_goal_y = abs(y) - distance_has_moved
                    if distance_to_arrive_goal_y <= self.stop_tolerance:
                        is_arrive_goal = True
                        break
                    move_velocity.linear.x = 0.0
                    if y > 0:
                        move_velocity.linear.y = math.copysign(self.speed , distance_to_arrive_goal_y)
                    else:
                        move_velocity.linear.y = math.copysign(self.speed ,-distance_to_arrive_goal_y)
                self.cmd_move_pub.publish(move_velocity)

            r.sleep()
        self.brake()



if __name__ == '__main__':
    rospy.init_node('move_cmd')
    move_cmd = move_a_distance()
    move_cmd.move_to(x = 1.2)
    sys.path.remove(config.robot_state_pkg_path)
