#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from datetime import datetime, timezone
from functools import partial
from threading import Thread
from time import sleep


class Metric(dict):

    def __init__(self, instance_id, start):
        super().__init__()
        self.instance_id = instance_id
        self.start = start
        self['Namespace']  = 'AWS/EC2'
        self['Unit']      = 'Bytes'
        self['Statistics'] = ['Sum']
        self['Dimensions'] = [{'Name':'InstanceId', 
                               'Value':self.instance_id}]
        self['StartTime']  = self.start
        self['EndTime']    = None 
        self['Period']     = None
        self['MetricName'] = None

    @property
    def set_period(self):
        now = datetime.now(tz=timezone.utc)
        self['EndTime'] = now
        period = (now - self.start).seconds
        period -= (period % 60)
        self['Period'] = period

class NetworkIn(Metric):

    def __init__(self, cloud_watch, instance_id, start, unit='Bytes'):
        super().__init__(instance_id, start)
        self.cloud_watch = cloud_watch
        self['MetricName'] = 'NetworkIn'
        self['Unit'] = unit
        self.get_metrics = partial(self.cloud_watch.get_metric_statistics,
                                   Namespace=self['Namespace'],
                                   MetricName=self['MetricName'],
                                   Dimensions=self['Dimensions'],
                                   StartTime=self['StartTime'],
                                   Statistics=self['Statistics'],
                                   Unit=self['Unit'])
        
    def request_statistics(self):
        self.set_period
        self.metric_statistics = self.get_metrics(EndTime=self['EndTime'], 
                                                  Period=self['Period'])

    def __str__(self):
        return str(self.metric_statistics)

class MetricMonitor(Thread):

    def __init__(self, instance_id):
        super().__init__()
        self.interval = 300 # 5-min intervals
        self.instance_up = True
        self.instance_id = instance_id
        self.cloud_watch = boto3.client('cloudwatch')
        self.ec2_client = boto3.client('ec2')
        self.metrics = [NetworkIn]

    def run(self):
        instance_description = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        start = instance_description['Reservations'][0]['Instances'][0]['LaunchTime']
        self.metrics = [metric(self.cloud_watch, self.instance_id, start) for metric in self.metrics]
        while self.instance_up:
            sleep(self.interval)
            for metric in self.metrics:
                metric.request_statistics()
                print(metric)
