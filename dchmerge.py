#!usr/bin/env python3
# MIT License
#
# Copyright (c) 2021 Lukas Cone
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from deb import Changelog
from argparse import ArgumentParser
from subprocess import run, CalledProcessError
from sys import exit

parser = ArgumentParser()
parser.add_argument('base', help='Filename for base changelog')
parser.add_argument('current', help='Filename for current changelog')
parser.add_argument('new', help='Filename for new changelog')
args = parser.parse_args()

try:
    current_changelog = Changelog()
    current_changelog.from_file(args.current)

    new_changelog = Changelog()
    new_changelog.from_file(args.new)

    current_changelog.merge(new_changelog)
    current_changelog.to_file(args.current)
except:
    # fallback to default git merge
    status = run(
        args=['git', 'merge-file', args.current, args.base, args.new])
    if status.returncode > 0:
        raise CalledProcessError(status.returncode, status.args, status.stdout,
                                 status.stderr)
    exit(1)
