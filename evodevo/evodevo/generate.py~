
# ### Code ###
import random


def generate_genome(num_genomes, num_chars):
    """Returns a 'num_genomes' long list of strings of 0s-3s, each with 
       length num_chars.

    """
    germ_genomes = list()
    for i in range(num_genomes):
        germ_genomes.append('')
        for j in range(num_chars):
            germ_genomes[i] = ''.join((germ_genomes[i],
                                       str(random.randrange(0, 4))))
    return germ_genomes
