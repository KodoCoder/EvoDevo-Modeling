"""
These are not unit-tests per se, as the input of some functions are the
output of other functions.  With this is mind, the tests are ordered to
reflect the order of dependency; that is, tests of dependent function come
after the tests of functions they depend on.
"""
import evodevo.develop as eddev
from evodevo.part import Part
from evodevo.subpart import (BodyPart, JointPart, NeuronPart, SensorPart,
                             WirePart)


def test_update_cycles():
    pass
