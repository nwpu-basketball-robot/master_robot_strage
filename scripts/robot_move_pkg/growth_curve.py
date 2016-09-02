#!/usr/bin/env python
# -*- coding:utf-8 -*-

#基于细菌生长曲线差值
#自变量为 位移
import  spline_config
from math import *
class growth_curve(object):
    def __init__(self):
        # gamma 影响插值曲线上的最大速度
        self.gamma = spline_config.GAMMA
        # 插值起始速度等于 gamma/(1+beta）
        self.start_beta  = spline_config.START_BETA
        # alpha 影响达到最大速度的自变量的值 alpha越大,越快达到最大速度
        self.start_alpha = spline_config.START_ALPHA
        self.end_beta = spline_config.END_BETA
        self.end_alpha = spline_config.END_ALPHA

    def set_goal_distance(self,goal_distance):
        self.goal = goal_distance
    def cal(self,dis):
        f1 = lambda x: self.gamma / (1.0 + self.start_beta*exp(-self.start_alpha * x))
        f2 = lambda x: self.gamma / (1.0 + self.end_beta*exp(-self.end_alpha *(self.goal -  x)))
        if dis <= self.goal/2.0 :
            return f1(dis)
        else:
#        elif dis < self.goal:
            return f2(dis)
#        else:
#            return 0.0
