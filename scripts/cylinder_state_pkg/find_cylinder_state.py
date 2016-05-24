#!/usr/bin/python
import rospy
import cylinder_detector.srv as cylinder

class find_cylinder_state(object):
    def __init__(self):
        self.cylinder_detector_client = rospy.ServiceProxy('cylinderdata',cylinder.cylinderdata)
        rospy.loginfo('[cylinder_state_pkg]->waiting cylinderdata service')
        self.cylinder_detector_client.wait_for_service()
        rospy.loginfo('[cylinder_state_pkg] -> connected to cylinder service')

    def get_cylinder_status(self):
        self.cylinder_detector_client.wait_for_service()
        req = self.cylinder_detector_client()
        return req.iscylinder, req.x, req.theta
if __name__ == '__main__':
    test = find_cylinder_state()
    print test.get_cylinder_status()