cmake_minimum_required(VERSION 2.8.3)
project(basketball_strage)

find_package(catkin REQUIRED COMPONENTS
  basketball_msgs
  #  ros_smach
  smach_ros
  roscpp
  rospy
)

#catkin_package(
#  INCLUDE_DIRS include
#  LIBRARIES basketball_strage
#  CATKIN_DEPENDS basketball_msgs ros_smach roscpp rospy std_msgs
#  DEPENDS system_lib
#)



## Specify additional locations of header files
## Your package locations should be listed before other locations
# include_directories(include)
include_directories(
  ${catkin_INCLUDE_DIRS}
)

