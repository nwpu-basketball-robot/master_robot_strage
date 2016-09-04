#!/usr/bin/env python
# -*- coding: utf-8 -*-
#robot_state_pkg_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
#用于加载自己写的模块,请将它改为自己的相应模块

robot_state_pkg_path = '/home/hyx/basketball_ws/src/basketball_strage/scripts/'
#import sys
#robot_state_pkg_path = sys.path[0][0:sys.path[0].index('/robot')]
# WARNING!!!!!!!!!!!!!!!! 发下去的速度不要超过 0.8右
# WARNING!!!!!!!!!!!!!!!! 发下去的速度不要低于 0.036

#设置直线速度
linear_move_speed = 1.0
#设置靠近球时以及在机器人坐标下的速度
low_linear_speed = 0.15
#设置插值直线移动阈值
high_speed_stop_tolerance = 0.03
# 设置低速以及在机器人坐标系下的移动阈值
low_speed_move_stop_tolerance = 0.04
#设置转弯的速度
high_turn_angular_speed = 0.5
# 低速、在机器人坐标系下转动速度
low_turn_angular_speed = 0.15
#弧度值 代表高速停止的阈值
high_turn_angular_stop_tolerance = 0.04
#弧度值 低速、在机器人坐标系下转动阈值
low_turn_angular_stop_tolerance = 0.05

#    回家时的一些参数
# 1:回家是向机器人的左边跑，
#-1： 回家时向机器人右边pao
go_home_direction = 1
#最后走的距离
last_distance = 0.3
#扫直线时的角度阈值
back_home_angular_tolerance = 0.05
#回家时距白线的距离阈值
line_distance_tolerance = 0.05
#需要与白线保持的距离
line_distance = 0.2
#修正角度时的速度
go_home_w_speed = 0.1
#修正x方向距离时的速度
go_home_x_speed = 0.1
#y方向上的速度
go_home_y_speed = 0.3

#沿圆弧时跑的参数
#绕着圆弧跑时的速度
go_along_circle_speed = 0.21
#角度阈值
go_along_circle_angular_tolerance = 0.02
