# Copyright (c) 2017 Wladimir J. van der Laan
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

class ProcedureMetaData:
    '''
    Known information about a procedure.
    '''
    def __init__(self, key):
        self.key = key
        self.name = None       # (putative) name
        self.delta = None      # stack: pushes-pops, sometimes known even though ins and outs is not known
        self.ins = None        # stack: word pops
        self.outs = None       # stack: word pushes
        self.num_locals = None # stack: number of locals
        self.parent = None     # lexical parent if known else None
        self.num_retvals = None # stack: number of return values
    def __repr__(self):
        return '(%s,%s,%s,%s,%s,%s)' % (self.key, self.name, self.delta, self.ins, self.outs, self.parent)
    @property
    def num_params(self):
        '''Number of parameters of this procedure'''
        if self.delta is not None:
            return -self.delta
        else:
            return None
    @property
    def rv_offset(self):
        '''Offset of return value in locals'''
        return self.num_locals + self.num_params + 1

class ProcedureList:
    '''
    Store known metadata about procedures in a format accessible
    by analysis tools.
    '''
    def __init__(self):
        self._map = {}
        self.dummy = ProcedureMetaData(None)

    def ref(self, key):
        '''Create a record for key if it doesn't exist yet'''
        if not key in self._map:
            self._map[key] = ProcedureMetaData(key)
        return self._map[key]

    def load_proclist(self, calls):
        for (segname, segcalls) in calls.items():
            for (procidx, procname) in segcalls.items():
                meta = self.ref((segname, procidx))
                if isinstance(procname, tuple):
                    (meta.name,meta.ins,meta.outs) = procname
                    if meta.ins is not None and meta.outs is not None:
                        meta.delta = meta.outs - meta.ins
                        meta.num_retvals = meta.outs
                else:
                    meta.name = procname

    def load_deltas(self, deltas):
        '''Load stack deltas'''
        for (key, data) in deltas.items():
            meta = self.ref(key)
            (meta.delta, meta.ins, meta.outs, meta.num_locals, meta.num_retvals) = data

    def load_hierarchy(self, hierarchy):
        '''Load lexical hierarchy'''
        for (key, data) in hierarchy.items():
            meta = self.ref(key)
            (meta.parent) = self.ref(data)

    def __getitem__(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return self.dummy


