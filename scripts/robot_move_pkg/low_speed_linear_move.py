#!/usr/bin/env python
#coding:utf-8

#Team unware basketball robot nwpu
#在X和Y轴上设置一段距离，同时设置一定的角度值，机器人移动相应的距离以及转相应角度
#可以设置直线移动速度
import rospy
import geometry_msgs.msg as g_msgs
import  math
import config
import  sys
sys.path.append(config.robot_state_pkg_path)
import robot_state_pkg.get_robot_position as robot_state#注意修改路径
import turn_an_angular
class low_speed_linear_move(object):
    def __init__(self):
        rospy.loginfo('[robot_move_pkg]->linear_move is initial')
        #通过这个模块获取机器人当前姿态
        self.robot_state = robot_state.robot_position_state()
        self.cmd_move_pub = rospy.Publisher('/cmd_move', g_msgs.Twist, queue_size = 100)
        self.rate = rospy.Rate(100)
        #设置机器人移动阈值
        self.stop_tolerance = config.linear_move_stop_tolerance
        #通过这个模块修正最终姿态角
        self.accurate_turn_an_angular = turn_an_angular.turn_an_angular()
        self.x_speed = 0.0
        self.y_speed = 0.0
        self.w_speed = 0.0
        #设置移动过程中的速度
        self.speed = config.low_linear_speed
        
    def brake(self):#停止时的回调函数
        rospy.loginfo('The robot is stopping...')
        move_velocity = g_msgs.Twist()
        move_velocity.linear.x = 0
        move_velocity.linear.y = 0
        move_velocity.angular.z = 0
        self.cmd_move_pub.publish(move_velocity)
        self.is_arrive_goal = False

    def start_run(self,x = 0.0, y = 0.0, yaw = 0.0):#开始移动
        #设置停止回调函数
        rospy.on_shutdown(self.brake)
        move_velocity = g_msgs.Twist()
        #计算移动欧拉距离
        goal_distance = math.sqrt(math.pow(x, 2)+math.pow(y, 2))
        #如果x方向距离为零，则直接设置y方向速度
        if x == 0.0:
            self.y_speed = config.linear_move_speed
        else:
        #如果不为零则根据x、y移动距离将config中的速度分解
            direction_angle = math.atan2(y , x)
            self.x_speed = abs(config.linear_move_speed * math.cos(direction_angle))
            self.y_speed = abs(config.linear_move_speed * math.sin(direction_angle))

        move_speed_value = config.linear_move_speed
        #如果目标距离不为零，则根据目标角度与直线移动的时间计算大概的角速度
        if goal_distance != 0:
            self.w_speed = yaw / goal_distance * move_speed_value
        else:
        #反之则直接利用turn_angular模块移动，这个速度的设置无效果
            self.w_speed = math.copysign(config.turn_angular_speed, yaw)
        move_velocity.angular.z = self.w_speed
        #获取启动前的x，y，yaw
        start_x, start_y, start_yaw = self.robot_state.get_robot_current_x_y_w()
        is_arrive_goal = False
        while not rospy.is_shutdown() and goal_distance != 0:
            if is_arrive_goal == False:
                current_x , current_y = self.robot_state.get_robot_current_x_y()
                distance_has_moved = math.sqrt( math.pow(current_x - start_x, 2)+
                                                math.pow(current_y - start_y, 2))

                distance_has_moved_x = current_x - start_x
                distance_has_moved_y = current_y - start_y
                #这个直线移动距离是为了与接下来的阈值比较
                distance_to_arrive_goal = distance_has_moved - goal_distance
                distance_to_arrive_goal_x = abs(x) - distance_has_moved_x
                distance_to_arrive_goal_y = abs(y) - distance_has_moved_y
                if abs(distance_to_arrive_goal) <= self.stop_tolerance:
                    self.is_arrive_goal = True
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
        current_yaw = self.robot_state.get_robot_current_yaw()
        #修正角度转动偏差，同时如果x，y均为零时转动角度
        self.accurate_turn_an_angular.turn(yaw - current_yaw + start_yaw)

    def move_to(self, x = 0.0, y = 0.0, yaw = 0.0):
    #提供给外部的接口
        rospy.loginfo('[robot_move_pkg]->linear_move will move to x_distance = %s'
                      'y_distance = %s, angular = %s'%(x,y,yaw))
        if x == 0.0 and y == 0:
            self.accurate_turn_an_angular.turn(self.normalize_angle(yaw))
        else:
            self.start_run(x, y,yaw)

    #提供给外部改变直线移动速度的接口
    #def set_linear_speed(self,speed = 0):
    #    self.speed = speed;
		
	
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
    move_cmd.move_to( x = 1,yaw = 1.57)
    move_cmd.move_to(x= -1, yaw= -1.57)
   
sys.path.remove(config.robot_state_pkg_path)
