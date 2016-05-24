#!/usr/bin/env python

import rospy
import config
import sys
sys.path.append(config.robot_state_pkg_path)
import robot_state_pkg.get_robot_position as get_state

def main():
    rospy.init_node('print_state')
    get_pos = get_state.robot_position_state()
    rospy.loginfo('begin')
    while raw_input("please input something:\n"):
        a = get_pos.get_robot_current_x_y_w()
        print "x = %s, y = %s, yaw = %s"%(a[0],a[1], a[2])

if __name__ == '__main__':
    main()
sys.path.remove(config.robot_state_pkg_path)
