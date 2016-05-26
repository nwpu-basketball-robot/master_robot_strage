#!/usr/bin/python
#coding=utf-8
#为状态机模块提供找定位柱的接口
#kinect的坐标系与机器人坐标系不同！
import rospy
import cylinder_detector.srv as cylinder

class find_cylinder_state(object):
    def __init__(self):
        self.cylinder_detector_client = rospy.ServiceProxy('cylinderdata',cylinder.cylinderdata)
        rospy.loginfo('[cylinder_state_pkg]->waiting cylinderdata service')
        self.cylinder_detector_client.wait_for_service()
        rospy.loginfo('[cylinder_state_pkg] -> connected to cylinder service')
	#返回定位柱的信息：是否找到定位柱，x上的距离，角度差值
    def get_cylinder_status(self):
        self.cylinder_detector_client.wait_for_service()
        req = self.cylinder_detector_client()
        return req.iscylinder, req.x, req.theta
if __name__ == '__main__':
    test = find_cylinder_state()
    print test.get_cylinder_status()
