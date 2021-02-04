#!/usr/bin/env python
# Potential field to navigate the robot

import rospy
import math
import numpy as np
import tf
import sys

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped

from std_msgs.msg import ColorRGBA


class RandomWalk(object):
    def __init__(self):
        self.namespace = str(sys.argv[1])
        # self.odom = Odometry()
        self.laser = LaserScan()
        self.cmd_vel = Twist()
        self.color = ColorRGBA()
        self.color.g = 1.0
        self.color.a = 1.0
        # self.goal = PoseStamped()
        # self.att_gain = 1.2
        # self.rep_gain = 0.4
        self.p0 = 50.0  # in meters
        # self.kTheta = 1.4
        # self.threshold = 0.10
        self.max_speed = 0.15
        # self.STATUS = 0
        self.laser_start = False

    def odom_cb(self, msg):
        self.odom = msg

    def laser_cb(self, msg):
        self.laser = msg
        self.laser_start = True

    def goal_cb(self, msg):
        self.goal = msg

    def run(self):
        rospy.init_node("random_walk", anonymous=True)

        self.pub = rospy.Publisher(
            self.namespace + "/cmd_vel", Twist, queue_size=1)

        self.pub_color = rospy.Publisher(
            self.namespace + "/led", ColorRGBA, queue_size=1)

        rospy.Subscriber(self.namespace + "/laser",
                         LaserScan, self.laser_cb)
        
        self.rate = rospy.Rate(10)  # 20 hz
        self.cmd_vel.linear.x = 0.08
        self.cmd_vel.angular.z = 0.0

        self.state_blocked = True
        self.sent_led = False
        rospy.loginfo("Starting Random Walk Controller for %s", self.namespace)
        self.scale = 2.0
        while not rospy.is_shutdown():
            if not self.laser_start:
                rospy.loginfo("[%s] Laser is not working yet!", self.namespace)
                self.rate.sleep()
                continue

            self.color.g = 0.0
            self.color.r = 0.0

            self.cmd_vel.linear.x = 0.06

            
            #rospy.loginfo(self.laser.ranges)
            rospy.loginfo(self.laser.ranges[3:6])

            if (self.laser.ranges[3] > self.p0) and (self.laser.ranges[4] > self.p0) and (self.laser.ranges[5] > self.p0):
                self.cmd_vel.angular.z = 0.05 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0
            if (self.laser.ranges[3] > self.p0) and (self.laser.ranges[4] > self.p0) and (self.laser.ranges[5] <= self.p0):
                self.cmd_vel.angular.z = 0.03 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0
            if (self.laser.ranges[3] > self.p0) and (self.laser.ranges[4] <= self.p0) and (self.laser.ranges[5] > self.p0):
                self.cmd_vel.angular.z = 0.05 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0
            if (self.laser.ranges[3] <= self.p0) and (self.laser.ranges[4] > self.p0) and (self.laser.ranges[5] <= self.p0):
                self.cmd_vel.angular.z = -0.03 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0

            if (self.laser.ranges[3] <= self.p0) and (self.laser.ranges[4] <= self.p0) and (self.laser.ranges[5] <= self.p0):
                self.cmd_vel.angular.z = 0.0 * self.scale
                self.color.g = 1.0

            if self.laser.ranges[3] > self.p0 and self.laser.ranges[4] <= self.p0 and self.laser.ranges[5] <= self.p0:
                self.cmd_vel.angular.z = 0.01 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0
            if self.laser.ranges[3] <= self.p0 and self.laser.ranges[4] > self.p0 and self.laser.ranges[5] <= self.p0:
                self.cmd_vel.angular.z = 0.01 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0
            if self.laser.ranges[3] <= self.p0 and self.laser.ranges[4] <= self.p0 and self.laser.ranges[5] > self.p0:
                self.cmd_vel.angular.z = -0.01 * self.scale
                self.cmd_vel.linear.x = 0.0
                self.color.r = 1.0

            if (self.color.r == 1 and self.state_blocked) or (self.color.g == 1 and not self.state_blocked):
                self.state_blocked = not self.state_blocked
                self.pub_color.publish(self.color)
            # if not self.sent_led:
            
                # self.sent_led = True
                self.pub.publish(self.cmd_vel)
            self.rate.sleep()

        self.cmd_vel.linear.x = 0.00
        self.cmd_vel.angular.z = 0.0
        self.pub.publish(self.cmd_vel)


# Main function
if __name__ == '__main__':
    try:
        rw = RandomWalk()
        rw.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("[Potential Field Controller]: Closed!")
