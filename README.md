# CS128_HW3
Distributed, Fault Tolerant Key-value Store

In the previous assignments you built a key-value store with forwarding. In this homework, you will extend the key-value store to be fault tolerant, available and eventually consistent.

**Partiton-tolerance, Availability and Consistency**

Your key-value store should be fault tolerant: it will continue functioning in the face of network partitions and node failure. You might look into the following docker commands "docker network disconnect" and "docker network connect" to learn about adding and removing nodes from a network.

Due to the CAP theorem, we know that we cannot have a fault tolerant key-value store that is both available and strongly consistent. In this assignment, we favor availability over strong consistency. Your key-value store should always return responses to requests, even if it cannot guarantee the most recent data.

Even though we cannot guarantee strong consistency, it is possible to guarantee eventual consistency and convergence. Right after a network is healed, the key-value store can return stale data. However, you key-values store should guarantee that the data is up-to date after a certain time bound. In other words, the key-value store should have the property of bounded staleness. The time bound for this assignment is 10 seconds.

**Conflict Resolution**

It is possible that after a network is healed, two nodes end up with different values for the same key. Such a conflict should be resolved using causal order, if it can be established. If the events are causally concurrent, then the tie should be resolved using the timestamps on replica nodes. Note that your key-value store needs to have a mechanism to establish a causal relation between events, such as vector clocks.

**Starting the key-value store**

To start a key value store we use the following environmental variables.

"K" is the number of replicas. There are two cases here:

|Nodes| >= K:  In this case, K nodes in the system will behave as replicas and any remaining nodes behave as proxies.
|Nodes| < K: In this case, the system will be operating in degraded mode and since we favor availability, we continue to accept writes in this mode.
 

"VIEW" is the list of ip:ports pairs of nodes.

"IPPORT" is the ip address and port of the node.

An example of starting a key-value store with 4 nodes and K=3:

```
docker run -p 8081:8080 --ip=10.0.0.21 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.21:8080" mycontainer
docker run -p 8082:8080 --ip=10.0.0.22 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.22:8080" mycontainer
docker run -p 8083:8080 --ip=10.0.0.23 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.23:8080" mycontainer
docker run -p 8084:8080 --ip=10.0.0.24 --net=mynet -e K=3 -e VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080" -e IPPORT="10.0.0.24:8080" mycontainer
```

In the above example, you will assign three of nodes as replicas and one as proxy.

### API
**Key-value Operations**

GET, PUT requests are a bit different from the previous assignments. Now they return extra information about the node that processed the write and causal order. The information used to establish causal order is stored in "causal_payload" and "timestamp" fields. The "causal_payload" field is used to establish causality between events. For example, if a node performs a write A followed by write B, then the corresponding causal payloads X_a and X_b should satisfy inequality X_a < X_b. Similarly, a causal payload X of a send event should be smaller that the causal payload Y of the corresponding receive event, i.e. X < Y. The value of the "causal_payload" field is solely depends on the mechanism you use to establish the causal order. The value of the "timestamp" field is the wall clock time on the replica that first processed the write.

To illustrate, let a client A writes a key, and a client B reads that key and then writes it, B's write should replace A's write (even if it lands on a different server). To make sure that this works, we will always pass the causal payload of previous reads into future writes. You must ensure that B's read returns a causal payload higher than the payload associated with A's write!

To consider another example, let 2 clients write concurrently to 2 different nodes respectively. And let T_1 and T_2 be the corresponding write timestamps measured according to the nodes' wall clocks. If T_1 > T_2 then the first write wins. If T_1 < T_2 then the second write wins. However, how can we resolve the writing conflict if T_1 == T_2? Can we use the identity of the nodes?

For better performance, no matter which node is queried, you may want to redirect requests so all replicas handle approximately equal number of requests.
