
# synapses conductances
mc_exc_gmax = 3.25 # nS
mc_inh_gmax = 0.3 # uS

mt_exc_gmax = 3.25 # nS
mt_inh_gmax = 0.3 # uS

# stream sniff
# you must change this to change the stimulation sequence
# of tuft weights or sniffs activation times
stream_ods_shift = 1

# odorsequence
# for each odor you must add a tuple in this manner
# the possible odors name are
# 'Apple', 'Banana', 'Basil', 'Black_Pepper',
# 'Cheese', 'Chocolate', 'Cinnamon',
# 'Cloves', 'Coffee', 'Garlic', 'Ginger',
# 'Lemongrass', 'Kiwi', 'Mint', 'Onion',
# 'Oregano', 'Pear', 'Pineapple'

# ('Mint', t init, t duration, rel. conc.), (...), (...)
odor_sequence = [ ]

# segments to records
# (cell gid, section index, arc, output filename)
sec2rec = [ (x, None, None) for x in range(1005, 1015) ]

# sim. duration
tstop = 5050

initial_weights = '' 

# dummy syns parameters
dummy_syn_conn = ''#dummysyns.txt'
ndummy_syn = 46

# sniff interval
# None is random
# the number was constant
sniff_invl_min = 350
sniff_invl_max = 350

init_exc_weight = 0.
init_inh_weight = 0.

training_exc = False
training_inh = False
