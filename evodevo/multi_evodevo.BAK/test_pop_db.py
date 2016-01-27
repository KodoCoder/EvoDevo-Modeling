import sqlite3

the_file = './population_genes.db'


def make_db(db=the_file, num=10):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    for i in range(num):
        tab = ''.join(('pop', str(i)))
        # s = 'CREATE TABLE {} (id INT PRIMARY KEY, genome1 INT, genome2 INT)'.format(tab)
        s = 'CREATE TABLE {} (id INT PRIMARY KEY, genome TEXT)'.format(tab)
        c.execute(s)
    conn.commit()
    conn.close()


def fill_table(tab, db=the_file):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    pop = list()
    for i in xrange(60):
        genome = initiate.generate_genome(18000)
        # gene1 = genome[:9000]
        # gene2 = genome[9000:]
        # pop.append((i, gene1, gene2))
        pop.append((i, genome))
    # s = 'INSERT into pop{} VALUES (?, ?, ?)'.format(tab)
    s = 'INSERT into pop{} VALUES (?, ?)'.format(tab)
    c.executemany(s, pop)
    conn.commit()
    conn.close()


def make_filled_db(db=the_file, num=10):
    make_db(db, num)
    for i in xrange(num):
        fill_table(i, db)


def grab_genome(tab, agent, db=the_file):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    t = (agent,)
    # c.execute('SELECT genome1, genome2 FROM pop1 WHERE id=?', t)
    s = 'SELECT genome FROM pop{} WHERE id=?'.format(tab)
    c.execute(s, t)
    genome = c.fetchone()
    print len(genome[0])
