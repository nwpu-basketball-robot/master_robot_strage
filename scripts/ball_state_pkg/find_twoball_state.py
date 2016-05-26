#!/usr/bin/python
#!coding=utf-8
#为状态机模块提供找两个球的接口
#kinect的坐标系与机器人坐标系不同！
import rospy
import two_ball_srv.srv as two_ball
class find_twoball_state(object):
    def __init__(self):
        self.two_ball_client = rospy.ServiceProxy('twoball',two_ball.twoball)
        rospy.loginfo('[ball_state_pkg]->find_twoball waiting twoball service')
        self.two_ball_client.wait_for_service()
        rospy.loginfo('[ball_state_pkg]-> connected to two_ball data service')
    #返回左球的当前信息：是否有球，x上距离，y上距离，相差角度
    def get_left_ball_current_status(self):
        self.two_ball_client.wait_for_service()
        req = self.two_ball_client()
        has_left_ball = req.left_has_ball
        left_x = req.left_z
        left_y = -req.left_x
        left_theta = -req.left_theta
        return  has_left_ball, left_x, left_y, left_theta
        
	#返回右球的当前信息：是否有球，x上距离，y上距离，相差角度
    def get_right_ball_current_status(self):
        self.two_ball_client.wait_for_service()
        req = self.two_ball_client()
        has_right_ball = req.right_has_ball
        right_x = req.right_z
        right_y = -req.right_x
        right_theta = -req.right_theta
        return  has_right_ball, right_x, right_y, right_theta
	#返回两个球的信息，先是左球，然后右球
    def get_two_ball_current_status(self):
        self.two_ball_client.wait_for_service()
        req = self.two_ball_client()
        has_left_ball = req.left_has_ball
        left_x = req.left_z
        left_y = -req.left_x
        left_theta = -req.left_theta
        has_right_ball = req.right_has_ball
        right_x = req.right_z
        right_y = -req.right_x
        right_theta = -req.right_theta
        return has_left_ball, left_x, left_y, left_theta, has_right_ball, right_x, right_y, right_theta

	#返回是否有球
    def get_has_two_ball(self):
        self.two_ball_client.wait_for_service()
        req = self.two_ball_client()
        has_left_ball = req.left_has_ball
        has_right_ball = req.right_has_ball
        return  has_left_ball, has_right_ball
if __name__ == '__main__':
    test = find_twoball_state()
    print test.get_left_ball_current_status()
    print test.get_right_ball_current_status()
    print test.get_two_ball_current_status()
    print test.get_has_two_ball()
