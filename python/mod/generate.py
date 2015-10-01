
# ### Code ###  
import copy
import random


def generate(n, c):
    germ_genomes = []
    for i in range(n):
        germ_genomes.append('')
        for j in range(c):
            germ_genomes[i] = ''.join((germ_genomes[i],
                                       str(random.randrange(0, 4))))
    return germ_genomes


# ### Tests ###
#  
# def length():
#     """Tests that germ_genomes and soma_genomes are the right length."""
#     global germ_genomes, soma_genomes
#     print "___Length Test___"
#     print "NON-ZERO CHECK ",
#     if len(germ_genomes) != 0:
#         print "passed; ",
#     else:
#         print "failed; ",
#     print "POPULATION CHECK ",
#     if len(germ_genomes) == len(soma_genomes):
#         print "passed; ",
#     else:
#         print "failed; ",
#     print "CHARACTER CHECK ",
#     val = True
#     for i in range(len(germ_genomes)):
#         if len(germ_genomes[i]) != 18000:
#             val = False
#         if len(soma_genomes[i]) != 18000:
#             val = False
#     if val:
#         print "passed."
#     else:
#         print "failed."
#    
#    
# def tethered():
#     """Tests that germ_genomes and soma_genomes are equal and independent"""
#     global germ_genomes, soma_genomes
#     print "___Tethered Test___"
#     print "EQUALITY CHECK ",
#     if germ_genomes == soma_genomes:
#         print "passed; ",
#     else:
#         print "failed; ",
#     # for i in range(len(germ_genomes)):
#     #     germ_genomes[i] += 'F'
#     # val = True
#     # for i in range(len(germ_genomes)):
#     #     if germ_genomes[i] == soma_genomes[i]:
#     #         val = False
#     print "INDEPENDENCE CHECK ",
#     if germ_genomes is not soma_genomes:
#         print "passed."
#     else:
#         print "failed."
#
"""
generate(60, 18000)
length()
tethered()
"""
