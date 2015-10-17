from __future__ import print_function
import evodevo.initiate as edinit


def test_generate_genomes():
    test_input = (60, 18000)
    assert len(edinit.generate_genomes(*test_input)) == 60
    for genome in edinit.generate_genomes(*test_input):
        assert len(genome) == 18000
        assert all((char in ('0', '1', '2', '3')) for char in
                   genome)

