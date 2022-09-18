# Motivation: Stream processing & publisher-subscribers

In data engineering, at some point, one will naturally move beyond batch processing (querying bounded datasets) and instead carry out stream processing. One of the industry leading frameworks for streaming data is _Apache Kafka_ - a tool that allows engineers to _produce_ data in real time and push them to _topics_, which are then read and processed by _consumers_.

# The concept of topics

Conceptually, _Topics_ are like queues - with some subtle but meaningful differences. Read more [here](http://www.differencebetween.net/technology/internet/difference-between-queue-and-topic/). The way to think about it is that a topic is a generalization of a queue - where queues can only have one consumer and producer (typically, anyway), and the producer knows the specific consumer on the other end of the queue, it's not the case in a topic. In a topic, a group of publishers can push to a FIFO data structure (the topic) and a group of consumers can _read_ from it.

Topics are the foundation of the publisher-subscriber model.

# Understanding how Apache Kafka works

<details open>
<summary><b>A distributed streaming platform</b></summary>
<br>

The core idea behind Kafka that it is built for streams (i.e. inifinite ordered sequences of data) in a distributed way. Distributed, as in, Kafka works in a cluster, where each node is called a **Broker**. At a high level, Kafka is a set of machines(real or virtual) working together to handle and process real-time infinite data in a scalable way.

</details>

<details open>
<summary><b>Partitions</b></summary>
<br>

Topics can be conceptually understood as append-only logs. At scale, it is easy to imagine that if we constrained a topic to a single machine, things would get tricky very quickly since vertical scaling (dumping more compute at the problem) can only go so far.

Kafka deals with this problem by partitioning, taking a single topic log and breaking it into multiple logs, each of which can live on a separate _node_ within a Kafka cluster - and processing messages can be split among these nodes. (It is worth noting at this point that Kafka topics are saved directly to disk with some clever optimizations to avoid slow reads and writes, and each partition can be thought of as a partition on a disk, just not necessarily on the same machine)

But how exactly does this partitioning in Kafka work? Having broken a topic up into partitions, we need a way of deciding which messages to write to which partitions. Typically, if a message has no key (no notion of partitioning or sort order), the messages will be distributed across the nodes in some default way (in the past, a round-robin fashion, but this is no longer true for later versions of Kafka). In this case, all partitions get some share of the data, but there is no notion of ordering of the input messages. But, if we have a key - say, a user ID - then the destination partition will be computed from the hash of a key, and in doing so we can guarantee that the messages having the same key always land in the same partition, and in the correct FIFO order. A useful application of this, for example, is using some `userId` as a key - then we can easily query a partition and have all messages to do with that user in order.

Each message will be stored in the broker (node) disk and receive an offset (a unique identifier). This offset is unique at the partition level - each partition has its own offsets. These messages are now read-only - that is, they cannot be deleted or edited. Producers use the offset to read the messages, reading from oldest to newest.

Read more in the [confluent docs](https://developer.confluent.io/learn-kafka/apache-kafka/partitions/#:~:text=Kafka%20Partitioning&text=Partitioning%20takes%20the%20single%20topic,many%20nodes%20in%20the%20cluster.).

</details>

<details open>
<summary><b>Brokers</b></summary>
<br>

Kafka works in a distributed way, with each cluster containing as many brokers as needed. Each broker in a cluster is identified by an ID and contains _at least_ one partition of a topic. The key responsibility of a broker (node in the cluster) is to manage the partitions assigned to it - that is, handle the read's and write's.

There are two key concepts relevant to brokers - replication factor and partition leadership. To ensure the reliability of the cluster, we have the idea of replication factor - that is, for a given partition, we replicate it exactly as many times as the replication factor (like a backup). For a given partition, the replication factor is intuitively bounded by the total number of brokers in the cluster.

The second concept flows naturally from replication factor, and it's used to answer the question of "with replications, where do we do the read's and write's?". The idea of _partition leadership_ comes in - that is, for a given set of nodes on which a given partition is replicated, exactly one is the _leader_. The leader is the only one that receives messages, and their replicas will just sync the data.

</details>

<details open>
<summary><b>Zookeeper</b></summary>
<br>

Taken from [here](https://dattell.com/data-architecture-blog/what-is-zookeeper-how-does-it-support-kafka/#:~:text=ZooKeeper%20is%20used%20in%20distributed,of%20Kafka%20topics%20and%20messages.).

ZooKeeper is used in distributed systems for service synchronization and as a naming registry. When working with Apache Kafka, ZooKeeper is primarily used to track the status of nodes in the Kafka cluster and maintain a list of Kafka topics and messages.

Amongst other things, it handles the re-election of partition leaders if a given leader goes down.

</details>

<details open>
<summary><b>Producers</b></summary>
<br>

The whole point of Kafka is to support n-m mappings of producers to consumers in a publisher-subscriber model, with scalability and fault tolerance. Producers produce messages - a partitioner maps each message to a topic partition, and the producer sends a produce request to the leader of that partition. If no key is provided in the messages, the message will be allocated to a given partition in a default way. But if a key is provided, a hash will be generated, which determines to which partition it goes.

When we are working with the concept of messages, there’s something called Acknowledgment (ack). The ack is basically a confirmation that the message was delivered. In Kafka, we can configure this ack when producing the messages. There are three different levels of configuration for that:

- ack = 0: When we configure the ack = 0, we’re saying that we don’t want to receive the ack from Kafka. In case of broker failure, the message will be lost;
- ack = 1: This is the default configuration, with that we’re saying that we want to receive an ack from the leader of the partition. The data will only be lost if the leader goes down (still there’s a chance);
- ack = all: This is the most reliable configuration. We are saying that we want to not only receive a confirmation from the leader but from their replicas as well. This is the most secure configuration since there’s no data loss. Remembering that the replicas need to be in-sync (ISR). If a single replica isn’t, Kafka will wait for the sync to send back de ack.

</details>

<details open>
<summary><b>Consumers and consumer groups</b></summary>
<br>

Consumers are applications (e.g. some microservice) subscribed to one or more topics that will read messages from there. They can read from one or more partitions of a given topic.

</details>

## Sources

- [The confluent docs](https://www.confluent.io/blog/apache-kafka-intro-how-kafka-works/)
- [This great medium post](https://medium.com/swlh/apache-kafka-what-is-and-how-it-works-e176ab31fcd5)

* [This other great medium post](https://towardsdatascience.com/how-to-build-a-simple-kafka-producer-and-consumer-with-python-a967769c4742)
* [This article](https://www.mikulskibartosz.name/how-does-kafka-cluster-work/)
* [Another bit from the confluent docs](https://docs.confluent.io/platform/current/clients/producer.html#:~:text=The%20Kafka%20producer%20is%20conceptually,the%20leader%20of%20that%20partition.)
* [This really great SO post](https://stackoverflow.com/questions/60835817/what-is-a-partition-leader-in-apache-kafka)

# A demo

## The idea of this demo

1. The dockerfile specified specifies starting up a number of zookeeper containers and Kafka containers, just like a cluster
2. We write a producer and a consumer in python, and start them up, like in a production environment with microservices
3. We kill one Kafka container - that's a broker going down, and we should be able to observe the leadership selection procedure, allowing for fault tolerance!
