#!/usr/bin/env python

"""
A runnable script to launch a single Rocket (a command-line interface to rocket.py)
"""
from argparse import ArgumentParser
import os
from fireworks.core.launchpad import LaunchPad
from fireworks.core.fworker import FWorker
from fireworks.core.rocket_launcher import rapidfire, launch_rocket


__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Feb 7, 2013'

if __name__ == '__main__':
    m_description = 'This program launches one or more Rockets. A Rocket grabs a job from the central database and ' \
                    'runs it. The "single-shot" option launches a single Rocket, ' \
                    'whereas the "rapidfire" option loops until all FireWorks are completed.'

    parser = ArgumentParser(description=m_description)
    subparsers = parser.add_subparsers(help='command', dest='command')
    single_parser = subparsers.add_parser('singleshot', help='launch a single Rocket')
    rapid_parser = subparsers.add_parser('rapidfire',
                                         help='launch multiple Rockets (loop until all FireWorks complete)')

    single_parser.add_argument('-f', '--fw_id', help='specific fw_id to run', default=None, type=int)

    rapid_parser.add_argument('--nlaunches', help='num_launches (int or "infinite")')
    rapid_parser.add_argument('--sleep', help='sleep time between loops (secs)', default=60, type=int)

    parser.add_argument('-l', '--launchpad_file', help='path to launchpad file', default=None)
    parser.add_argument('-w', '--fworker_file', help='path to fworker file', default=None)

    parser.add_argument('--logdir', help='path to a directory for logging', default=None)
    parser.add_argument('--loglvl', help='level to print log messages', default='INFO')
    parser.add_argument('--silencer', help='shortcut to mute log messages', action='store_true')

    args = parser.parse_args()

    if not args.launchpad_file and os.path.exists('my_launchpad.yaml'):
        args.launchpad_file = 'my_launchpad.yaml'

    if not args.fworker_file and os.path.exists('my_fworker.yaml'):
        args.fworker_file = 'my_fworker.yaml'

    args.loglvl = 'CRITICAL' if args.silencer else args.loglvl

    if args.launchpad_file:
        launchpad = LaunchPad.from_file(args.launchpad_file)
    else:
        launchpad = LaunchPad(logdir=args.logdir, strm_lvl=args.loglvl)

    if args.fworker_file:
        fworker = FWorker.from_file(args.fworker_file)
    else:
        fworker = FWorker()

    if args.command == 'rapidfire':
        rapidfire(launchpad, fworker, None, args.logdir, args.loglvl, args.nlaunches, args.sleep)

    else:
        launch_rocket(launchpad, fworker, args.logdir, args.loglvl, args.fw_id)