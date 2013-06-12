sh -c "`which redis-server` $CI_HOME/bin/redis/redis-node-1.conf --dir ${CI_HOME}/bin/redis --include ${CI_HOME}/bin/redis/redis-common.conf"
sh -c "`which redis-server` $CI_HOME/bin/redis/redis-node-2.conf --dir ${CI_HOME}/bin/redis --include ${CI_HOME}/bin/redis/redis-common.conf"
sh -c "`which redis-server` $CI_HOME/bin/redis/redis-node-5.conf --dir ${CI_HOME}/bin/redis --include ${CI_HOME}/bin/redis/redis-common.conf"
sh -c "`which redis-server` $CI_HOME/bin/redis/redis-node-6.conf --dir ${CI_HOME}/bin/redis --include ${CI_HOME}/bin/redis/redis-common.conf"
