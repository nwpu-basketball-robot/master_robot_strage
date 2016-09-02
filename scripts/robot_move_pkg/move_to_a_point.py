#!/usr/bin/env python

#append the robot state pkg to the python path
import config
import sys
sys.path.append(config.robot_state_pkg_path)
import robot_state_pkg as robot_state



sys.path.remove(config.robot_state_pkg_path)