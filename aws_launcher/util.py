import os
import sys
import argparse
import subprocess
import importlib
import boto3

def handle_cfg():
    parser = argparse.ArgumentParser()
    parser.add_argument("cfg", help="the configuration file")

    parsed, unknown = parser.parse_known_args()

    for arg in unknown:
        if arg.startswith(("-", "--")):
            parser.add_argument(arg)
            args=parser.parse_args()

    args = parser.parse_args()

    sys.path.insert(0, os.getcwd())
    cfg_module = importlib.import_module(args.cfg)
    for k, v in args._get_kwargs():
        cfg_module.__dict__[k] = v
    return cfg_module

def run(cmd):
    print('running', cmd)
    out = subprocess.run(cmd, shell = True)
    return out.returncode
