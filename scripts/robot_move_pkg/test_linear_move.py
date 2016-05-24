import rospy
import roslib
import tf
import actionlib
import math
from tf.transformations import *
from geometry_msgs.msg import *
class linearMove(object):
    def __init__(self):
        rospy.loginfo('the linear srv move start!!!')
        self.rate = 100
        self.distance = 0.0
        self.x_start = 0.0
        self.y_start = 0.0
        self.cmd_angle = 0.0
        self.goal_distance = 0.0
        self.y_speed = 0.0
        self.move_cmd = Twist()

        self.x_speed = rospy.get_param('~x_speed',0.40)
        self.tolerance = rospy.get_param('~tolerance',0.1)
        self.cmd_vel = rospy.Publisher('cmd_move',Twist,queue_size=5)
        self.base_frame = rospy.get_param('~base_frame','/base_link')
        self.odom_frame = rospy.get_param('~odom_frame','/odom')
        self.flag = rospy.get_param('~flag', True)
        self.tf_listener = tf.TransformListener()


    def execute(self):
        rospy.on_shutdown(self.shutdown)
        rospy.loginfo("the goal_x you want to move is %s, the goal_y you want to move is %s",self.goal_x,self.goal_y)
        self.tf_listener.waitForTransform(self.odom_frame, self.base_frame, rospy.Time(), rospy.Duration(60))

        r = rospy.Rate(self.rate)
        self.position = Point()
        self.position = self.get_position()
        self.x_start = self.position.x
        self.y_start = self.position.y
        self.goal_distance = math.sqrt(math.pow(self.goal_x, 2) + math.pow(self.goal_y, 2))
        self.cmd_angle = math.atan2(self.goal_y, self.goal_x)

        if self.goal_x == 0:
            self.y_speed = 0.40
        else:
            self.y_speed = abs(self.x_speed * self.goal_y / self.goal_x)

        while not rospy.is_shutdown():
            self.move_cmd = Twist()
            if self.flag==True:
                self.position = self.get_position()
                self.distance = math.sqrt(math.pow((self.position.x - self.x_start), 2) +
                                          math.pow((self.position.y - self.y_start), 2))

                error = self.distance - self.goal_distance
                if abs(error) < self.tolerance:
                    self.flag = False
                else:
                    error_x = self.position.x - self.goal_x
                    error_y = self.position.y - self.goal_y
                    if self.goal_x > 0 and self.goal_y > 0:
                        self.move_cmd.linear.x = math.copysign(self.x_speed, 1 * error_x)
                        self.move_cmd.linear.y = math.copysign(self.y_speed, 1 * error_y)


                    elif self.goal_x > 0 and self.goal_y < 0:
                        self.move_cmd.linear.x = math.copysign(self.x_speed, 1 * error_x)
                        self.move_cmd.linear.y = math.copysign(self.y_speed, -1 * error_y)

                    elif self.goal_x < 0 and self.goal_y > 0:
                        self.move_cmd.linear.x = math.copysign(self.x_speed, -1 * error_x)
                        self.move_cmd.linear.y = math.copysign(self.y_speed, 1 * error_y)

                    elif self.goal_x < 0 and self.goal_y < 0:
                        self.move_cmd.linear.x = math.copysign(self.x_speed, -1 * error_x)
                        self.move_cmd.linear.y = math.copysign(self.y_speed, -1 * error_y)

                    self.cmd_vel.publish(self.move_cmd)

            else:
                self.brake()
                break
            r.sleep()
        self.brake()



    def brake(self):
        self.move_cmd.linear.x = 0
        self.move_cmd.linear.y = 0
        self.cmd_vel.publish(self.move_cmd)

    def shutdown(self):
        rospy.loginfo("Stopping the robot...")
        self.brake()

    def get_position(self):
        try:
            (trans, rot) = self.tf_listener.lookupTransform(self.odom_frame,self.base_frame,rospy.Time(0))
        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            rospy.loginfo("TF EXCEPTION!!!")
            return

        return Point(*trans)

    def move(self, x, y):
        self.goal_x = x
        self.goal_y = y
        self.execute()

if __name__ == '__main__':
    try:
        rospy.init_node("linear_move")
        a = linearMove()
        a.move(1, -1)
    except rospy.ROSInterruptException:
        rospy.loginfo("linear_move node terminated.")
