"""
These are not unit-tests per se, as the input of some functions are the
output of other functions.  With this is mind, the tests are ordered to
reflect the order of dependency; that is, tests of dependent function come
after the tests of functions they depend on.
"""

from evodevo.my_table import table
import evodevo.subpart as edspart



