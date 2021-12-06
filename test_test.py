from deb import Changelog
from subprocess import run
import os
from filecmp import cmp
from shutil import copyfile


def test_double_unresolved():
    ch = Changelog()
    ch.from_file('test/000_double_unreleased')

    ch1 = Changelog()
    ch1.from_file('test/001_double_unreleased')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/002_double_unreleased')

    assert(result == ch)


def test_double_unresolved_flags():
    ch = Changelog()
    ch.from_file('test/010_double_unreleased_flags')

    ch1 = Changelog()
    ch1.from_file('test/011_double_unreleased_flags')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/012_double_unreleased_flags')

    assert(result == ch)


def test_double_unresolved_empty():
    ch = Changelog()
    ch.from_file('test/020_double_unreleased_empty')

    ch1 = Changelog()
    ch1.from_file('test/021_double_unreleased_empty')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/022_double_unreleased_empty')

    assert(result == ch)


def test_release_conflict():
    ch = Changelog()
    ch.from_file('test/030_release_conflict')

    ch1 = Changelog()
    ch1.from_file('test/031_release_conflict')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/032_release_conflict')

    assert(result == ch)


def test_release_conflict_more():
    ch = Changelog()
    ch.from_file('test/040_release_conflict_more')

    ch1 = Changelog()
    ch1.from_file('test/041_release_conflict_more')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/042_release_conflict_more')

    assert(result == ch)


def test_conflict_same_version():
    ch = Changelog()
    ch.from_file('test/050_conflict_same_version')

    ch1 = Changelog()
    ch1.from_file('test/051_conflict_same_version')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('test/052_conflict_same_version')

    assert(result == ch)

def test_fallback():
    copyfile('test/061_fallback', 'test/064_fallback')
    status = run(cwd=os.getcwd(), args=['python3', 'dchmerge.py', 'test/060_fallback', 'test/064_fallback', 'test/062_fallback'])
    assert(status.returncode == 1)
    assert(cmp('test/064_fallback', 'test/063_fallback'))
