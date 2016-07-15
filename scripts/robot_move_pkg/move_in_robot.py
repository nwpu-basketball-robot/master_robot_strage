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
import turn_an_angular
import interpolation_function.growth_curve as spline_func

class linear_move(object):
    def __init__(self):
        rospy.loginfo('[robot_move_pkg]->linear_move is initial')
        #通过这个模块获取机器人当前姿态
        self.robot_state = robot_state.robot_position_state()
        self.cmd_move_pub = rospy.Publisher('/cmd_move_robot', g_msgs.Twist, queue_size = 100)
        self.rate = rospy.Rate(100)
        #设置机器人移动阈值
        self.stop_tolerance = config.linear_move_stop_tolerance
        #通过这个模块修正最终姿态角
        self.accurate_turn_an_angular = turn_an_angular.turn_an_angular()
        self.x_speed = 0.0
        self.y_speed = 0.0
        self.w_speed = 0.0
        #设置移动过程中的速度
        self.speed = config.linear_move_speed
        #进行线速度插值
        self.linear_sp = spline_func.growth_curve()
        #进行角速度插值
        self.angular_sp = spline_func.growth_curve()

    def brake(self):#停止时的回调函数
        rospy.loginfo('The robot is stopping...')
        move_velocity = g_msgs.Twist()
        move_velocity.linear.x = 0
        move_velocity.linear.y = 0
        move_velocity.angular.z = 0
        self.cmd_move_pub.publish(move_velocity)


    def start_run(self,x = 0.0, y = 0.0):#开始移动
        #设置停止回调函数
        rospy.on_shutdown(self.brake)
        move_velocity = g_msgs.Twist()
        #计算目标移动欧拉距离
        goal_distance = math.sqrt(math.pow(x, 2)+math.pow(y, 2))
        #算出方向角,便于接下来的分解
        direction_angle = math.atan2(y , x)
        #获取启动前的x，y，yaw
        start_x, start_y, start_yaw = self.robot_state.get_robot_current_x_y_w()
        #设置目标插值距离，确定最终插值曲线
        self.linear_sp.set_goal_distance(abs(goal_distance))
#        self.angular_sp.set_goal_distance(abs(yaw))
        is_arrive_goal = False
        while not rospy.is_shutdown() and goal_distance != 0:
            if is_arrive_goal == False:
                current_x, current_y, current_yaw = self.robot_state.get_robot_current_x_y_w()
                distance_has_moved = math.sqrt(math.pow(current_x - start_x, 2) +
                                               math.pow(current_y - start_y, 2))
                # 此速度是插值算出的线速度
                linear_speed = self.linear_sp.cal(distance_has_moved)
                move_velocity.angular.z = 0.0
                # 将插值算出来的速度进行分解
                self.x_speed = linear_speed * math.cos(direction_angle)
                self.y_speed = linear_speed * math.sin(direction_angle)
                # 这个直线移动距离是为了与接下来的阈值比较
                distance_to_arrive_goal = distance_has_moved - goal_distance
                move_velocity.linear.x = math.copysign(self.x_speed, x)
                move_velocity.linear.y = math.copysign(self.y_speed, y)
                if abs(distance_to_arrive_goal) <= self.stop_tolerance:
                    self.is_arrive_goal = True
                    break
            self.cmd_move_pub.publish(move_velocity)
            self.rate.sleep()
        self.brake()

    def move_to(self, x = 0.0, y = 0.0, yaw = 0.0):
    #提供给外部的接口
        rospy.loginfo('[robot_move_pkg]->linear_move will move to x_distance = %s y_distance = %s, angular = %s'%(x,y,yaw))
        self.accurate_turn_an_angular.turn(self.normalize_angle(yaw))
        self.start_run(x, y)

    def normalize_angle(self, angle):
    #将目标角度转换成-2pi到2pi之间
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < math.pi:
            angle += 2.0 * math.pi
        print('current angular is %s'%angle)
        return  angle

if __name__ == '__main__':
    rospy.init_node('linear_move')
    move_cmd = linear_move()
    move_cmd.move_to( x =  2.5,yaw = 0.5)
   
sys.path.remove(config.robot_state_pkg_path)
