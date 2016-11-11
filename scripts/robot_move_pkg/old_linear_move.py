#!/usr/bin/env python
#coding:utf-8

#Team unware basketball robot nwpu
#在X和Y轴上设置一段距离，同时设置一定的角度值，机器人移动相应的距离以及转相应角度
# 2016-7-18
# 将直线移动速度和角速度进行了关联
# 2016-9-4
# 单方向距离判断取代欧拉距离;单一方向下移动进行另一方向修正
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
        self.cmd_move_pub = rospy.Publisher('/cmd_move', g_msgs.Twist, queue_size = 100)
        self.rate = rospy.Rate(150)
        #设置机器人直线移动阈值
        self.stop_tolerance = config.high_speed_stop_tolerance
        self.angular_tolerance = config.high_turn_angular_stop_tolerance
        #通过这个模块修正最终姿态角
        self.accurate_turn_an_angular = turn_an_angular.turn_an_angular()
        self.x_speed = 0.0
        self.y_speed = 0.0
        self.w_speed = config.high_turn_angular_speed
        #进行线速度插值
        self.linear_sp = spline_func.growth_curve()
        self.amend_speed = 0.12

    def brake(self):#停止时的回调函数
        rospy.loginfo('The robot is stopping...')
        move_velocity = g_msgs.Twist()
        move_velocity.linear.x = 0
        move_velocity.linear.y = 0
        move_velocity.angular.z = 0
        self.cmd_move_pub.publish(move_velocity)

    def start_run(self,x = 0.0, y = 0.0, yaw = 0.0):#开始移动
        #设置停止回调函数
        rospy.on_shutdown(self.brake)
        move_velocity = g_msgs.Twist()
        # 计算目标移动欧拉距离
        goal_distance = math.sqrt(math.pow(x, 2)+math.pow(y, 2))
        # 算出方向角,便于接下来的分解
        direction_angle = math.atan2(y , x)
        # 获取启动前的x，y，yaw
        start_x, start_y, start_w = self.robot_state.get_robot_current_x_y_w()
        # 设置目标插值距离，确定最终插值曲线
        self.linear_sp.set_goal_distance(abs(goal_distance))
        angular_has_moved = 0.0
        y_has_moved = 0.0
        x_has_moved =0.0
        x_arrive_goal = False
        y_arrive_goal = False
        is_in_x = False
        is_in_y = False
        if y == 0.0:
            is_in_x = True
        if x == 0.0:
            is_in_y = True
        # 构建goal_angular 和 goal_distance 的函数关系后等式两边对dt取微分可得
        # w = df(goal_distance)/dgoal_distance * v
        # 因为我们简单的将goal_angular 和 goal_distance 构建为线性关系,所以最终角速度和线速度的关系为
        # w = goal_angular/goal_distance * v
        # 在这里,因为线速度不是完美连续的,所以为了让角度移动和直线移动尽量保持同步,所以加上了一个系数0.02
        # 0.02只是目前的一个补偿系数,可以进行大量的调试来精准的确定
        cov_func =lambda x: x*abs(yaw)/ goal_distance
        while not rospy.is_shutdown() and goal_distance != 0:
            current_x, current_y, current_w = self.robot_state.get_robot_current_x_y_w()
            #x 方向已经移动的距离
            x_has_moved = current_x - start_x
            #有方向已经移动的距离
            y_has_moved = current_y - start_y
            dis_has_moved = math.sqrt(x_has_moved**2 + y_has_moved**2)
            angular_has_moved += abs(abs(current_w) - abs(start_w))
            start_yaw = current_w
            #计算速度
            #如果只走x
            if is_in_x == True:
                if abs(abs(x_has_moved) - abs(x)) < self.stop_tolerance:
                    break
                #x方向速度赋值
                self.x_speed = math.copysign(self.linear_sp.cal(abs(x_has_moved)),x)
                # 角度在阈值之外就计算角速度,反之赋零
                if yaw != 0.0 and abs(angular_has_moved - abs(yaw)) < self.angular_tolerance:
                    self.w_speed=0.0
                else:
                    self.w_speed = math.copysign(cov_func(self.x_speed), yaw)
                #如果y方向位移超出阈值，则加上修正速度修正，反之为零
                if abs(abs(y_has_moved) - abs(y)) < self.stop_tolerance:
                    self.y_speed = 0.0
                else:
                    self.y_speed = math.copysign(self.amend_speed,-1*(y_has_moved-y))
            #只走y方向
            elif is_in_y == True:
                if abs(abs(y_has_moved) - abs(y)) < self.stop_tolerance:
                    break
                self.y_speed = math.copysign(self.linear_sp.cal(abs(y_has_moved)),y)
                # 角度在阈值之外就计算角速度,反之赋零
                if yaw != 0.0 and abs(angular_has_moved - abs(yaw)) < self.angular_tolerance:
                    self.w_speed = 0.0
                else:
                    self.w_speed = math.copysign(cov_func(self.y_speed), yaw)
                #如果x方向超出阈值，则加上修正速度修正，反之赋零
                if abs(abs(x_has_moved) - abs(x)) < self.stop_tolerance:
                    self.x_speed = 0.0
                else:
                    self.x_speed = math.copysign(self.amend_speed,-1*(x_has_moved-x))
            else :
                if x_arrive_goal == True and y_arrive_goal == True:
                    break
                else:
                    linear_speed = self.linear_sp.cal(dis_has_moved)
                    # 角度在阈值之外就计算角速度,反之赋零
                    if yaw != 0.0 and abs(angular_has_moved - abs(yaw)) < self.angular_tolerance:
                        self.w_speed = 0.0
                    else:
                        self.w_speed = math.copysign(cov_func(linear_speed), yaw)
                    #9-4现在里程还算是比较准，所以进行停止判断时不参考欧拉距离，对单一方向进行判断
                    #判断x方向是否到目标距离
                    if abs(abs(x_has_moved) - abs(x)) <= self.stop_tolerance:
                        x_arrive_goal = True
                        self.x_speed = 0.0
                        #x=0.0
                        #is_in_y = True
                        #self.linear_sp.set_goal_distance(y)
                    else:
                        self.x_speed = math.copysign((linear_speed)*math.cos(direction_angle), x)
                    #判断y方向是否到目标距离
                    if abs(abs(y_has_moved) - abs(y)) <= self.stop_tolerance:
                        y_arrive_goal = True
                        self.y_speed = 0.0
                        #print "y is end"
                        #is_in_x = True
                        #self.linear_sp.set_goal_distance(x)
                    else:
                        self.y_speed = math.copysign((linear_speed)*math.sin(direction_angle), y)
            #将计算好的速度赋值并发下去
            move_velocity.linear.x = self.x_speed
            move_velocity.linear.y = self.y_speed
            move_velocity.angular.z = self.w_speed
            self.cmd_move_pub.publish(move_velocity)
            self.rate.sleep()
        print x_has_moved,y_has_moved,angular_has_moved
        self.brake()

    def move_to(self, x= 0.0, y= 0.0, yaw= 0.0):
        if x == 0.0 and y == 0:
            self.accurate_turn_an_angular.turn(self.normalize_angle(yaw))
        else:
            self.start_run(x, y, yaw)

    def move_to_pose(self, x = 0.0, y = 0.0, yaw = 0.0):
        '''提供给外部的接口，移动到某一姿态'''
        rospy.loginfo('[robot_move_pkg]->linear_move will move to x_distance = %s y_distance = %s, angular = %s'%(x,y,yaw))
        if x == 0.0 and y == 0:
            self.accurate_turn_an_angular.turn(self.cal_now_pose_to_pose(yaw))
        else:
            self.start_run(x, y,self.cal_now_pose_to_pose(yaw))

    def cal_now_pose_to_pose(self,goal_pose_yaw):
        current_yaw = self.robot_state.get_robot_current_w()
        return self.normalize_angle(current_yaw - goal_pose_yaw)

    def normalize_angle(self, angle):
    # 将目标角度转换成-pi到pi之间
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        print('current angular is %s'%angle)
        return  angle

if __name__ == '__main__'   :
    rospy.init_node('linear_move')
    move_cmd = linear_move()
   # move_cmd.move_to( x = 5.4 ,y=-9.6 ,yaw =-math.pi/4.0)
    move_cmd.move_to(9.6,-1.2,math.pi/4.0)
#   move_cmd.move_to( x = 2.6 )

sys.path.remove(config.robot_state_pkg_path)
