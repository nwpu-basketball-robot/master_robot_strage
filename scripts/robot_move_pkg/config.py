# -*- coding: utf-8 -*-
#robot_state_pkg_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
#用于加载自己写的模块,请将他改为自己的相应模块
robot_state_pkg_path = '/home/hyx/basketball_ws/src/basketball_strage/scripts'	
#设置直线速度
linear_move_speed = 0.02	
#设置误差值
linear_move_stop_tolerance = 0.01
#设置转弯的速度
turn_angular_speed = 0.02	
#速度比例值  最终速度=turn_angular_speed * turn_angular_scale
turn_angular_scale = 1.0	
#角度值，代表停止的误差值
turn_augular_stop_tolerance = 5.0	
