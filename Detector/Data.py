from __future__ import print_function, division, absolute_import
from sadit.util import abstract_method
from sadit.util import Find, DataEndException
class Data(object):
    """abstract base class for data. Data class deals with any implementation
    details of the data. it can be a file, a sql data base, and so on, as long
    as it supports the pure virtual methods defined here.
    """
    def get_rows(self, rg=None, rg_type=None):
        """ get a slice of feature

        Parameters
        ---------------
        rg : list of two floats
            is the range for the slice
        rg_type : str,  {'flow', 'time'}
            type for range

        Returns
        --------------
        list of list

        """
        abstract_method()

    def get_where(self, rg=None, rg_type=None):
        """ get the absolute position of flows records that within the range.

        Find all flows such that its belong to [rg[0], rg[1]). The interval
        is closed in the starting point and open in the ending pont.

        Parameters
        ------------------
        rg : list or tuple or None
            range of the the data. If rg == None, simply return position
            (0, row_num])
        rg_type : {'flow', 'time'}
            specify the type of the range.

        Returns
        -------------------
        sp, ep : ints
            flows with index such that sp <= idx < ed belongs to the range

        """
        abstract_method()


from sadit.util import np
from sadit.util import argsort
import re
def parse_records(f_name, FORMAT, regular_expression):
    flow = []
    with open(f_name, 'r') as fid:
        while True:
            line = fid.readline()
            if not line:
                break
            if line == '\n': # Ignore Blank Line
                continue
            item = re.split(regular_expression, line)
            # import ipdb;ipdb.set_trace()
            f = tuple(h(item[pos]) for k, pos, h in FORMAT)
            flow.append(f)
    return flow

IP = lambda x:tuple(int(v) for v in x.rsplit('.'))
class PreloadHardDiskFile(Data):
    """ for hard Disk File Generated by fs-simulator"""
    RE = None
    FORMAT = None
    DT = None
    fields = zip(*FORMAT)[0] if FORMAT is not None else None

    def __init__(self, f_name):
        """ data_order can be flow_first | feature_first
        """
        self.f_name = f_name
        # self.fields = zip(*self.DT)[0]
        self._init()

    @staticmethod
    def parse(*argv, **kwargv):
        return parse_records(*argv, **kwargv)

    def _init(self):
        # self.fea_vec = ParseRecords(self.f_name, self.FORMAT, self.RE)
        self.fea_vec = self.parse(self.f_name, self.FORMAT, self.RE)
        # import ipdb;ipdb.set_trace()
        self.table = np.array(self.fea_vec, dtype=self.DT)
        self.row_num = self.table.shape[0]

        self.t = np.array([t for t in self.get_rows('start_time')])
        t_idx = np.argsort(self.t)
        self.table = self.table[t_idx]
        self.t = self.t[t_idx]

        self.min_time = min(self.t)
        self.max_time = max(self.t)

    def get_where(self, rg=None, rg_type=None):
        if not rg:
            return 0, self.row_num
        if rg_type == 'flow':
            sp, ep = rg
            if sp >= self.row_num: raise DataEndException()
        elif rg_type == 'time':
            sp = Find(self.t, rg[0]+self.min_time)
            ep = Find(self.t, rg[1]+self.min_time)
            # if rg[1] + self.min_time > self.max_time :
                # import pdb;pdb.set_trace()
                # raise Exception('Probably you set wrong range for normal flows? Go to check DETECTOR_DESC')

            assert(sp != -1 and ep != -1)
            if (sp == len(self.t)-1 or ep == len(self.t)-1):
                # import pdb;pdb.set_trace()
                raise DataEndException()
        else:
            raise ValueError('unknow window type')
        return sp, ep

    def get_rows(self, fields=None, rg=None, rg_type=None):
        if fields is None:
            fields = list(self.fields)
            print('fields', fields)
        sp, ep = self.get_where(rg, rg_type)
        return self.table[sp:ep][fields]

class HDF_FS(PreloadHardDiskFile):
    """  For Hard Disk File Generated by fs-simulator
    """

    RE = '[\[\] :\->]'
    FORMAT = [
            ('start_time', 3, np.float64),
            ('end_time', 4, np.float64),
            ('src_ip', 5, IP),
            ('src_port', 6, np.int16),
            ('dst_ip', 8, IP),
            ('dst_port', 9, np.int16),
            ('protocol', 10, np.str_),
            ('node', 12, np.str_),
            ('duration', 13, np.float64),
            ('flow_size', 14, np.float64),
            ]
    DT = np.dtype([
        ('start_time', np.float64, 1),
        ('end_time', np.float64, 1),
        ('src_ip', np.int8, (4,)),
        ('src_port', np.int16, 1),
        ('dst_ip', np.int16, (4,)),
        ('dst_port', np.int16, 1),
        ('protocol', np.str_, 5),
        ('node', np.str_ , 5),
        ('duration', np.float64, 1),
        ('flow_size', np.float64, 1),
        ])


##############################################################

##############################################################
import datetime
import time
def str_to_sec(ss, formats):
    """
    >>> str_to_sec('2012-06-17T16:26:18.300868', '%Y-%m-%dT%H:%M:%S.%f')
    14660778.300868
    """
    # x = time.strptime(ss,'%Y-%m-%dT%H:%M:%S.%f')
    x = time.strptime(ss,formats)

    ts = ss.rsplit('.')[1]
    micros = int(ts) if len(ts) == 6 else 0 #FIXME Add microseconds support for xflow
    return datetime.timedelta(
            days = x.tm_yday,
            hours= x.tm_hour,
            minutes= x.tm_min,
            seconds= x.tm_sec,
            microseconds = micros,
            ).total_seconds()


class HDF_Pcap2netflow(PreloadHardDiskFile):
    """data with format of pcap2netflow, (softflowd and flowd-reader)

    See Also
    --------------------
    for more information about pcap2netflow, please visit
        `https://bitbucket.org/hbhzwj/pcap2netflow`_
    """

    def IP2(ss):
        return tuple(int(v) for v in ss.rsplit(':')[0][1:-1].rsplit('.'))

    def PORT2(ss):
        return int(ss.rsplit(':')[1])

    RE = ' '
    FORMAT = [
            ('start_time', 2, lambda x: str_to_sec(x, '%Y-%m-%dT%H:%M:%S.%f')),
            ('src_ip', 12, IP2),
            ('src_port', 12, PORT2),
            ('dst_ip', 14, IP2),
            ('dst_port', 14, PORT2),
            ('packets', 16, np.int32),
            ('octets', 18, np.int32),
            ]
    DT = np.dtype([
            ('start_time', np.float64, 1),
            ('src_ip', np.int8, (4,)),
            ('src_port', np.int16, 1),
            ('dst_ip', np.int8, (4,)),
            ('dst_port', np.int16, 1),
            ('packets', np.int64, 1),
            ('octets', np.int64, 1),
        ])



class HDF_FlowExporter(PreloadHardDiskFile):

    RE = '[ \n]'
    FORMAT = [
            ('start_time', 0, np.float64),
            ('src_ip', 1, IP),
            ('dst_ip', 2, IP),
            ('protocol', 3, np.str_),
            ('flow_size', 4, np.float64),
            ('duration', 5, np.float64),
            ]
    DT = np.dtype([
            ('start_time', np.float64, 1),
            ('src_ip', np.int8, (4,)),
            ('dst_ip', np.int8, (4,)),
            ('protocol', np.str_, 5),
            ('flow_size', np.float64, 1),
            ('duration', np.float64, 1),
        ])


def parse_complex_records(fileName, FORMAT, regular_expression):
    """
    the input is the filename of the flow file that needs to be parsed.
    the ouput is list of dictionary contains the information for each flow in the data. all these information are strings, users need
    to tranform them by themselves
    """
    flow = []
    fid = open(fileName, 'r')
    while True:
        line = fid.readline()
        if not line: break
        item = re.split(regular_expression, line)
        try:
            f = tuple(h(item[v]) for k,v,h in FORMAT[len(item)])
        except KeyError:
            raise Exception('Unexpected Flow Data Format')
        flow.append(f)
    fid.close()

    return flow

class HDF_Xflow(PreloadHardDiskFile):
    RE = ' '
    DT = [
        ('start_time', np.float64, 1),
        ('proto', np.str_, 5),
        ('src_ip', np.int8, (4,)),
        ('direction', np.str_, 5),
        ('server_ip', np.int8, (4,)),
        ('Cb', np.float64, 1),
        ('Cp', np.float64, 1),
        ('Sb', np.float64, 1),
        ('Sp', np.float64, 1),
        ]
    fields = zip(*DT)[0]

    port_str_to_int = lambda x: int(x[1:])
    attr_convert = lambda x: float( x.rsplit('=')[1].rsplit(',')[0] )
    handlers = [
            lambda x: str_to_sec(x, '%Y%m%d.%H:%M:%S'),
            str,
            IP,
            str,
            IP,
            attr_convert,
            attr_convert,
            attr_convert,
            lambda x: float(x.rsplit('=')[1].rsplit('\n')[0]),
            ]
    FORMAT = dict()
    FORMAT[11] = zip(fields, [0, 2, 3, 4, 5, 7, 8, 9, 10], handlers)
    FORMAT[12] = zip(fields, [0, 3, 4, 5, 6, 8, 9, 10, 11], handlers)
    FORMAT[13] = zip(fields, [0, 2, 3, 5, 6, 9, 10, 11, 12], handlers)
    FORMAT[14] = zip(fields, [0, 3, 4, 6, 7, 10, 11, 12, 13], handlers)

    @staticmethod
    def parse(*argv, **kwargv):
        return parse_complex_records(*argv, **kwargv)

##############################################################
####  For simpleweb.org labled dataset, it is stored in ######
####  mysql server.                                     ######
####  visit http://www.simpleweb.org/wiki/Traces for    ######
####  more information (trace 8)                        ######
##############################################################

from sadit.util import mysql
get_sec_msec = lambda x: [int(x), int( (x-int(x)) * 1e3)]

class SQLFile_SperottoIPOM2009(Data):
    """Data File wrapper for SperottoIPOM2009 format. it is store in mysql server, visit
     http://traces.simpleweb.org/traces/netflow/netflow2/dataset_description.txt
    """
    def __init__(self, spec):
        # self.db = _mysql.connect(**spec)
        self.db = mysql.connect(**spec)
        self._init()

    def _init(self):
        # select minimum time
        self.db.query("""SELECT start_time, start_msec FROM flows WHERE (id = 1);""")
        r = self.db.store_result()
        self.min_time_tuple = r.fetch_row()[0]
        self.min_time = float("%s.%s"%self.min_time_tuple)

        self.db.query("""SELECT MAX(id) FROM flows;""")
        r = self.db.store_result()
        self.flow_num = int(r.fetch_row()[0][0])

        self.db.query("""SELECT end_time, end_msec FROM flows WHERE (id = %d);"""%(self.flow_num))
        r = self.db.store_result()

        self.max_time_tuple = r.fetch_row()[0]
        self.max_time = float("%s.%s"%self.max_time_tuple)

    def _get_sql_where(self, rg=None, rg_type=None):
        if rg:
            if rg_type == 'flow':
                SQL_SEN_WHERE = """ WHERE ( (id >= %f) AND (id < %f) )""" %tuple(rg)
                if rg[0] > self.flow_num:
                    raise DataEndException("reach data end")

            elif rg_type == 'time':
                st = get_sec_msec (rg[0] + self.min_time)
                ed = get_sec_msec (rg[1] + self.min_time)
                SQL_SEN_WHERE = """ WHERE ( (start_time > %d) OR ( (start_time = %d) AND (start_msec >= %d)) ) AND
                             ( (end_time < %d) OR ( (end_time = %d) and (end_msec < %d) ) )""" %(st[0], st[0], st[1], ed[0], ed[0], ed[1])

                # print 'rg[0]', rg[0]
                # print 'self.min_time', self.min_time
                # print 'current time, ', rg[0] + self.min_time
                # print 'self.maxtime', self.max_time
                if rg[0] + self.min_time > self.max_time:
                    raise DataEndException("reach data end")
            else:
                print('rg_type', rg_type)
                raise ValueError('unknow window type')
        else:
            SQL_SEN_WHERE = ""
        return SQL_SEN_WHERE

    def get_max(self, fea, rg=None, rg_type=None):
        fea_str = ['MAX(%s)'%(f) for f in fea]
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea_str)) + self._get_sql_where(rg, rg_type) + ";"
        self.db.query(SQL_SEN)
        r = self.db.store_result().fetch_row(0)
        return r[0]

    def get_min(self, fea, rg=None, rg_type=None):
        fea_str = ['MIN(%s)'%(f) for f in fea]
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea_str)) + self._get_sql_where(rg, rg_type) + ";"
        self.db.query(SQL_SEN)
        r = self.db.store_result().fetch_row(0)
        return r[0]

    def get_fea_slice(self, fea, rg=None, rg_type=None):
        """this function is to get a chunk of feature vector.
        The feature belongs flows within the range specified by **rg**
        **rg_type** can be ['flow' | 'time' ].
        """
        SQL_SEN = """SELECT %s FROM flows"""%(",".join(fea)) + self._get_sql_where(rg, rg_type) + ";"
        # print SQL_SEN
        self.db.query(SQL_SEN)
        result = self.db.store_result().fetch_row(0)
        # return [line[0] for line in result] if len(fea) == 1 else result
        return result


#######################################################
## Flow Records Generated by xflow tools            ###
#######################################################
from time import strptime, mktime
# def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    # return sorted(range(len(seq)), key=seq.__getitem__)

# from sadit.util import argsort



if __name__ == "__main__":
    import doctest
    doctest.testmod()

