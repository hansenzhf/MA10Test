# -*- coding: utf-8 -*-
__author__ = "hank"

import unittest
import sys
import os
import time
import csv
sys.path.append("../")
from lib.get_data import GetData
from lib.deal_with_ma10_ma60 import DealWithMA10MA60


class TestWeekTask(unittest.TestCase):

    def test_weak_task(self):
        #GetData().get_stock_list()
        #GetData().get_data_together()
        #DealWithMA10MA60().deal_with_ma120()
        #DealWithMA10MA60().deal_with_ma120_ma240()
        #DealWithMA10MA60().deal_with_ma240()
        #DealWithMA10MA60().deal_with_ma240_down()
        #DealWithMA10MA60().two_eight_turn()
        DealWithMA10MA60().two_eight_turn_v2()

if __name__ == "__main__":
    TestWeekTask().test_weak_task()

