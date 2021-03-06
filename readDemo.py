#!/usr/bin/python

import sys
from random import randint
import time

from dse.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from dse.auth import PlainTextAuthProvider
from dse.policies import DCAwareRoundRobinPolicy,TokenAwarePolicy, ConstantSpeculativeExecutionPolicy
from dse import ConsistencyLevel

#Configuration
contactpoints = ['40.78.69.234', '104.42.194.135']
localDC = "Google"
CL = ConsistencyLevel.ONE
#CL = ConsistencyLevel.ALL
auth_provider = PlainTextAuthProvider (username='user1', password='password1')
profile1 = ExecutionProfile( load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=localDC, used_hosts_per_remote_dc=3),
                            speculative_execution_policy=ConstantSpeculativeExecutionPolicy(.05, 20),
                            consistency_level = CL
                            )

print "Connecting to cluster"

cluster = Cluster( contact_points=contactpoints,
                   auth_provider=auth_provider,
                   execution_profiles={EXEC_PROFILE_DEFAULT: profile1},
                   )

session = cluster.connect()

used_dc = localDC
coordinator = localDC
c = 0
x = 0
while 1:

   current = time.localtime()
   bucket = str(current.tm_year) + str(current.tm_mon) + str(current.tm_mday) + str(current.tm_hour) + str(current.tm_min)

   ts = int(time.time() * 1000)

   query = """ select * from demo.table1 where bucket = '%s' limit 1 """ % (bucket)
   try:
    results = session.execute (query)
   except: 
    error = 1
   for r in results:
    d = r.d
   while ts + 30 > int(time.time() * 1000):
    t1 = 0
   c = c + 1
   x = x + 1
   if(x == 10):
    last_c = coordinator
    future = session.execute_async (query, trace=True )
    result = future.result()
    try:
     trace = future.get_query_trace( 1 )
     coordinator =  trace.coordinator
    except:
     coordinator = last_c
    for h in session.hosts:
     if h.address == coordinator:
      used_dc = h.datacenter
      print(""" Rows Read %s (%s) - %s""" ) % (c, used_dc, d)
    x = 0

cluster.shutdown()
sys.exit(0)
