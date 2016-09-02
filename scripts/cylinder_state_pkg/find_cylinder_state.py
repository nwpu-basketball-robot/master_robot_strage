#!/usr/bin/python
#coding=utf-8
#为状态机模块提供找定位柱的接口
#kinect的坐标系与机器人坐标系不同！
import rospy
# import cylinder_detector.srv as cylinder
import cylinder_find.srv as cylinder_opencv
import leg_detector.srv as cylinder_laser

class find_cylinder_state(object):
    def __init__(self):
        # self.cylinder_detector_client = rospy.ServiceProxy('cylinderdata',cylinder.cylinderdata)
        self.cylinder_opencv_client = rospy.ServiceProxy('cylinder_data',cylinder_opencv.cylinder_find)
        self.cylinder_laser_client = rospy.ServiceProxy('cylinder',cylinder_laser.cylinder)
        rospy.loginfo('[cylinder_state_pkg]->waiting cylinderdata service')
        self.cylinder_laser_client.wait_for_service()
        self.cylinder_opencv_client.wait_for_service()
        rospy.loginfo('[cylinder_state_pkg] -> connected to cylinder service')
	#返回定位柱的信息：是否找到定位柱，x上的距离，角度差值


    def get_cylinder_status(self):
        self.cylinder_laser_client.wait_for_service()
        self.cylinder_opencv_client.wait_for_service()
        flag = 0
        r = rospy.Rate(2)
        while not rospy.is_shutdown() and flag != 1:
            res_opencv = self.cylinder_opencv_client()
            res_laser = self.cylinder_laser_client()
            x_laser = res_laser.x
            theta_laser = res_laser.theta
            theta_opencv = res_opencv.theta
            if abs(theta_laser - theta_opencv) < 0.01:
                flag = 1
                break
            r.sleep()
        return (x_laser,theta_laser)


if __name__ == '__main__':
    test = find_cylinder_state()
    print test.get_cylinder_status()
