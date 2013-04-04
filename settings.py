"""
This is a sample setting file for ARO(Army Research Office) demo.
The topology is proposed by Dan and try to simulation the typical
traffic condition of the ARO Network.
"""
#################################################################
### ROOT is the root directory for you directory, be aware to ###
### change this before you try to run the code                ###
#################################################################
# ROOT = '/home/wangjing/Dropbox/Research/sadit-experimental'
# ROOT = '/home/wangjing/Dropbox/Research/sadit'
# ROOT = '/Users/wangjing/Dropbox/Research/sadit-experimental'
# ROOT = '/home/wangjing/Documents/CyberSecurity/sadit'
# ROOT = '/home/wangjing/Documents/CyberSecurity/sadit'
ROOT = '/home/wangjing/Dropbox/Research/sadit'
# ROOT = '/Users/wangjing/Dropbox/Research/sadit'


#################################
##   Network Topology ##
#################################
zeros = lambda s:[[0 for i in xrange(s[1])] for j in xrange(s[0])]
# from numpy import zeros

# g_size = 8
# g_size = 4
g_size = 10
# srv_node_list = [0, 1]
srv_node_list = [0]
topo = zeros([g_size, g_size])
for i in xrange(g_size):
    if i in srv_node_list:
        continue
    # topo[i, srv_node_list] = 1
    for srv_node in srv_node_list:
        topo[i][srv_node] = 1


#################################
##   Parameter For Normal Case ##
#################################
sim_t = 8000
start = 0
DEFAULT_PROFILE = ((sim_t,),(1,))

# gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e5', 'flow_size_var':'100', 'flow_arrival_rate':'0.5'}
gen_desc = {'TYPE':'harpoon', 'flow_size_mean':'4e3', 'flow_size_var':'100', 'flow_arrival_rate':'1'}
NORM_DESC = dict(
        TYPE = 'NORMAl',
        start = '0',
        node_para = {'states':[gen_desc]},
        profile = DEFAULT_PROFILE,
        # start topology
        src_nodes = range(g_size),
        dst_nodes = srv_node_list,
        )

# ANOMALY_TIME = (1200, 1400)
# ANO_DESC = {'anoType':'TARGET_ONE_SERVER',
ANO_DESC = {
        # 'anoType':'flow_arrival_rate',
        # 'anoType':'flow_size_mean',
        'anoType':'anomaly',
        # 'anoType':'atypical_user',
        # 'ATIP':['8.8.8.8'],
        # 'anoType':'flow_size_mean_arrival_rate',
        'ano_node_seq':2,
        # 'T':(2000, 3000),
        'T':(5000, 5500),
        # 'T':(1200, 1400),
        # 'change':{'flow_arrival_rate':6},
        # 'change':{'flow_arrival_rate':4},
        # 'change':{'flow_arrival_rate':2},
        'change':{'flow_size_mean':2},
        # 'change':{'flow_size_mean':6},
        # 'change':{'flow_size_mean':0.5, 'flow_arrival_rate':3},
        # 'change':{'flow_size_var':6},
        'srv_id':0,
        }

ANO_LIST = [ANO_DESC]
# ANO_LIST = []


link_attr_default = {'weight':'10', 'capacity':'10000000', 'delay':'0.01'} # link Attribute
NET_DESC = dict(
        topo=topo,
        # size=topo.shape[0],
        size=len(topo),
        srv_list=srv_node_list,
        link_attr_default=link_attr_default,
        node_type='NNode',
        node_para={},
        )


IPS_FILE = ROOT + '/Configure/ips.txt'


EXPORT_ABNORMAL_FLOW = True
# EXPORT_ABNORMAL_FLOW = False
EXPORT_ABNORMAL_FLOW_PARA_FILE = ROOT + '/Share/ano_flow_para.txt'
# EXPORT_ABNORMAL_FLOW_FILE = ROOT + '/Simulator/abnormal_flow.txt'
EXPORT_ABNORMAL_FLOW_FILE = ROOT + '/Simulator/abnormal_n0_flow.txt'


# The path for output of configure
OUTPUT_DOT_FILE = ROOT + '/Share/conf.dot'

# THe path for flow data
OUTPUT_FLOW_FILE = ROOT + '/Simulator/n0_flow.txt'
IPS_FILE = ROOT + '/Configure/ips.txt'

#############################
##   Parameters For Detector ##
#############################
ANO_ANA_DATA_FILE = ROOT + '/Share/AnoAna.txt'
DETECTOR_DESC = dict(
        # file_type = 'SQL',
        # interval=30,
        # interval=50,
        # win_size = 50,
        # interval=20,
        # interval=4,
        interval=10,
        # interval=30,
        # interval=100,
        # interval=2000,
        # win_size = 10,
        # win_size=100,
        win_size=100,
        # win_size=20000,
        # win_size=200,
        win_type='time', # 'time'|'flow'
        # win_type='flow', # 'time'|'flow'
        fr_win_size=100, # window size for estimation of flow rate
        false_alarm_rate = 0.001,
        unified_nominal_pdf = False, # used in sensitivities analysis
        # discrete_level = DISCRETE_LEVEL,
        # cluster_number = CLUSTER_NUMBER,
        # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':3},
        fea_option = {'dist_to_center':3, 'flow_size':2, 'cluster':3},
        # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':2},
        # fea_option = {'dist_to_center':1, 'flow_size':3, 'cluster':1},
        # fea_option = {'dist_to_center':2, 'octets':2, 'cluster':2},
        # fea_option = {'dist_to_center':2, 'flow_size':2, 'cluster':1},
        ano_ana_data_file = ANO_ANA_DATA_FILE,
        # normal_rg = [0, 1000],
        # normal_rg = [0, 1000],
        normal_rg = None,
        # normal_rg = [0, 4000],
        # normal_rg = [0, float('inf')],
        detector_type = 'mfmb',
        max_detect_num = None,
        # max_detect_num = 10,
        # max_detect_num = 20,
        # max_detect_num = 100,
        # data_handler = 'fs',
        data_type = 'fs',
        # data_handler = 'fs_deprec',

        #### only for SVM approach #####
        # gamma = 0.01,

        #### only for Generalized Emperical Measure #####
        small_win_size = 1,
        # small_win_size = 1000,
        g_quan_N = 3,
        )
# when using different data_hanlder, you will have different set of avaliable options for fea_option.

FLOW_RATE_ESTIMATE_WINDOW = 100 #only for test

FALSE_ALARM_RATE = 0.001 # false alarm rate
NominalPDFFile = ROOT + '/Share/nominal.p'
UNIFIED_NOMINAL_PDF = False


#########################################
### Parameters for Derivative Test  ####
#########################################
DERI_TEST_THRESHOLD = 0.1
# DERI_TEST_THRESHOLD = 1

# ANOMALY_TYPE_DETECT_INDI = 'derivative'
# MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-deri.eps'
# MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-deri.eps'

ANOMALY_TYPE_DETECT_INDI = 'component'
MODEL_FREE_DERI_DESCENDING_FIG = ROOT + '/res/mf-descending-comp.eps'
MODEL_BASE_DERI_DESCENDING_FIG = ROOT + '/res/mb-descending-comp.eps'
