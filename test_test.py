from deb import Changelog
from subprocess import run
import os
from filecmp import cmp
from shutil import copyfile


def assert_changelogs(name):
    ch = Changelog()
    ch.from_file('test/{}_0'.format(name))

    ch1 = Changelog()
    ch1.from_file('test/{}_1'.format(name))

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/{}_result'.format(name))

    assert(result == ch)

def test_unreleased():
    assert_changelogs('unreleased')


def test_flags():
    assert_changelogs('flags')


def test_empty():
    assert_changelogs('empty')


def test_release():
    assert_changelogs('release')


def test_multiple_release_():
    assert_changelogs('multiple_release')


def test_version():
    assert_changelogs('version')

def test_fallback():
    os.makedirs('build/test', exist_ok=True)
    copyfile('test/fallback_1', 'build/test/fallback_1')
    status = run(cwd=os.getcwd(), args=['python3', 'dchmerge.py', 'test/fallback_0', 'build/test/fallback_1', 'test/fallback_2'])
    assert(status.returncode == 1)
    assert(cmp('build/test/fallback_1', 'test/fallback_result'))
