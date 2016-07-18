#!/usr/bin/env python
#coding:utf-8
#Team unware basketball robot nwpu
#在X和Y轴上设置一段距离，同时设置一定的角度值，机器人移动相应的距离以及转相应角度
#基于机器人坐标系下的移动
#主要更改：  cmd_move --> cmd_move_robot
# 先转角度，再进行直线移动
import rospy
import geometry_msgs.msg as g_msgs
import  math
import config
import  sys
sys.path.append(config.robot_state_pkg_path)
import robot_state_pkg.get_robot_position as robot_state#注意修改路径

class linear_move(object):
    def __init__(self):
        rospy.loginfo('[robot_move_pkg]->move_in_robot is initial')
        # 通过这个模块获取机器人当前姿态
        self.robot_state = robot_state.robot_position_state()
        self.cmd_move_pub = rospy.Publisher('/cmd_move_robot', g_msgs.Twist, queue_size = 100)
        self.rate = rospy.Rate(100)
        # 设置机器人直线移动阈值
        self.linear_move_stop_tolerance = config.low_speed_move_stop_tolerance
        self.turn_move_stop_tolerance = config.low_turn_angular_stop_tolerance
        self.x_speed = 0.0
        self.y_speed = 0.0
        self.w_speed = config.low_turn_angular_speed
        # 设置移动过程中的速度
        self.speed = config.low_linear_speed

    def turn(self, goal_angular):
        # 为了在机器人坐标系能转更加精准,所以在此定义了一个旋转的函数
        # 速度更低,阈值更小
        rospy.loginfo('[robot_move_pkg]->move_in_robot.turn will turn %s'%goal_angular)
        current_angular = start_angular = self.robot_state.get_robot_current_w()#获取当前机器人的角度

        r = rospy.Rate(100)
        delta_angular = current_angular - start_angular
        move_velocity = g_msgs.Twist()
        while not rospy.is_shutdown() :
            if abs(delta_angular - abs(goal_angular)) < self.turn_move_stop_tolerance:
                break
            current_angular = self.robot_state.get_robot_current_w()
            move_velocity.angular.z = math.copysign(self.w_speed, goal_angular)
            delta_angular += abs(abs(current_angular) - abs(start_angular) )
            start_angular = current_angular
            self.cmd_move_pub.publish(move_velocity) #发送速度，使机器人旋转
            r.sleep()
        self.brake()


    def brake(self):
        '''停止时的回调函数'''
        rospy.loginfo('The robot is stopping...')
        move_velocity = g_msgs.Twist()
        move_velocity.linear.x = 0
        move_velocity.linear.y = 0
        move_velocity.angular.z = 0
        self.cmd_move_pub.publish(move_velocity)
        self.is_arrive_goal = False

    def start_run(self, x = 0.0, y = 0.0):# 开始移动
        # 设置停止回调函数
        move_velocity = g_msgs.Twist()
        # 计算移动欧拉距离
        goal_distance = math.sqrt(math.pow(x, 2)+math.pow(y, 2))
        # 如果x方向距离为零，则直接设置y方向速度
        if x == 0.0:
            self.y_speed = self.speed
        else:
        # 如果不为零则根据x、y移动距离将config中的速度分解
            direction_angle = math.atan2(y , x)
            self.x_speed = abs(self.speed * math.cos(direction_angle))
            self.y_speed = abs(self.speed * math.sin(direction_angle))
        # 获取启动前的x，y，yaw
        start_x, start_y = self.robot_state.get_robot_current_x_y()
        while not rospy.is_shutdown() :
            current_x , current_y = self.robot_state.get_robot_current_x_y()
            distance_has_moved = math.sqrt( math.pow(current_x - start_x, 2)+
                                                math.pow(current_y - start_y, 2))
            distance_has_moved_x = current_x - start_x
            distance_has_moved_y = current_y - start_y
            # 这个直线移动距离是为了与接下来的阈值比较
            distance_to_arrive_goal = distance_has_moved - goal_distance
            distance_to_arrive_goal_x = abs(x) - distance_has_moved_x
            distance_to_arrive_goal_y = abs(y) - distance_has_moved_y
            if abs(distance_to_arrive_goal) <= self.linear_move_stop_tolerance:
                break
            if x >= 0 and y >= 0:
                move_velocity.linear.x = math.copysign(self.x_speed, 1 * distance_to_arrive_goal_x)
                move_velocity.linear.y = math.copysign(self.y_speed, 1 * distance_to_arrive_goal_y)
            if x > 0 and y < 0:
                move_velocity.linear.x = math.copysign(self.x_speed, 1 * distance_to_arrive_goal_x)
                move_velocity.linear.y = math.copysign(self.y_speed,-1 * distance_to_arrive_goal_y)
            if x < 0 and y > 0:
                move_velocity.linear.x = math.copysign(self.x_speed,-1 * distance_to_arrive_goal_x)
                move_velocity.linear.y = math.copysign(self.y_speed, 1 * distance_to_arrive_goal_y)
            if x <= 0 and y <= 0:
                move_velocity.linear.x = math.copysign(self.x_speed,-1 * distance_to_arrive_goal_x)
                move_velocity.linear.y = math.copysign(self.y_speed,-1 * distance_to_arrive_goal_y)
            self.cmd_move_pub.publish(move_velocity)
            self.rate.sleep()
        self.brake()
        # 修正角度转动偏差，同时如果x，y均为零时转动角度

    def move_to(self, x = 0.0, y = 0.0, yaw = 0.0):
        ''' 提供给外部的接口 '''
        rospy.on_shutdown(self.brake) #系统停止时，机器人急停
        rospy.loginfo('[robot_move_pkg]->move_in_robot will move to x_distance = %s'
                      'y_distance = %s, angular = %s'%(x, y, yaw))
        if x == 0.0 and y == 0:
            self.turn(self.normalize_angle(yaw))
        else:
            self.turn(self.normalize_angle(yaw))
            self.start_run(x, y)

    def normalize_angle(self, angle):
        ''' 将目标角度转换成-2pi到2pi之间 '''
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle <-math.pi:
            angle += 2.0 * math.pi
        print('current angular is %s'%angle)
        return  angle

if __name__ == '__main__':
    rospy.init_node('linear_move')
    move_cmd = linear_move()
    move_cmd.move_to(x= 0.5,y =-0.5 , yaw = 0.)
#    move_cmd.move_to(x= -1, yaw= -1.57)
   
sys.path.remove(config.robot_state_pkg_path)
