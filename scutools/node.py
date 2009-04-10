"""
  Wrapper for node information fetching
          
  @author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""

import os, sys, commands, string, socket
from scutools import config
from scutools.error import NodeStatus

ALIVE = 0x1
ALL = 0x2
ALL_EXC = 0x4

class HostSrc(object) :
    def get_alive(flag) :
        pass

class ScmsHostSrc(HostSrc) :
    def get_alive(self, flag) :
        cmd = None
        opt = ''
        if (flag & ALL) :
            # get only alive node
            opt = opt + ' -a'
        if (flag & ALL_EXC) :
            opt = opt + ' -e'
        cmd = config.sce_host + opt
        status, output = commands.getstatusoutput(cmd)
        if status == 0 :
            return string.split(output)
        else :
            raise NodeStatus, 'sce_host'

class GstatHostSrc(HostSrc) :
    def get_alive(self, flag) :
        gstat_cmd = os.popen(config.gstat + ' -a -m -l', 'r')
        host_list = []
        while True :
            line = gstat_cmd.readline()
            if not line: break
            host, ncpu = line.strip().split(':')
            host_list.append(host)
        exit_stat = gstat_cmd.close()
        if not exit_stat is None :
            raise NodeStatus, 'gstat -a -m -l'

        if (flag & ALL) :
            gstat_cmd = os.popen(config.gstat + ' -d -1 -l', 'r')
            while True :
                line = gstat_cmd.readline()
                if not line: break
                if line.find('There are no hosts down') >= 0 :
                    break
                else :
                    host, time = line.strip().split(' ', 1)
                    host_list.append(host)
            exit_stat = gstat_cmd.close()
            if not exit_stat is None :
                raise NodeStatus, 'gstat -a -m -l'
        if (flag & ALL_EXC) :
            my_hostname = socket.gethostname()
            short_hostname = my_hostname.split('.', 1)[0]
            for i in range(len(host_list)) :
                if (host_list[i] == my_hostname) or (host_list[i].split('.', 1)[0] == short_hostname) :
                    del host_list[i]
                    break
        return host_list

def get_alive(flag = ALIVE) :
    if config.hostlist_src == 'gstat' :
        host_src = GstatHostSrc()
    elif config.hostlist_src == 'sce_host' :
        host_src = ScmsHostSrc()

    return host_src.get_alive(flag)

if __name__ == '__main__' :
    print '*** alive nodes ***'
    print get_alive(ALIVE)
    print '*** all nodes ***'
    print get_alive(ALL)
    print '*** all nodes except self ***'
    print get_alive(ALIVE | ALL_EXC)