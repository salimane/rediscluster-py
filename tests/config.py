cluster = {
            # node names
            'nodes' : {
              'node_1' : {'host' : '127.0.0.1', 'port' : 63791},
              'node_2' : {'host' : '127.0.0.1', 'port' : 63792},

              'node_5' : {'host' : '127.0.0.1', 'port' : 63795},
              'node_6' : {'host' : '127.0.0.1', 'port' : 63796},
            },
            # replication information
            'master_of' : {
                            'node_1' : 'node_6', #node_6 slaveof node_1 in redis6.conf
                            'node_2' : 'node_5', #node_5 slaveof node_2 in redis5.conf
                            },
            
            'default_node' : 'node_1'
          }