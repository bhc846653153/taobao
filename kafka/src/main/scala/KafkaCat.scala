package org.apache.spark.examples.streaming

import java.util.HashMap
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerConfig, ProducerRecord}
import org.json4s._
import org.json4s.jackson.Serialization
import org.json4s.jackson.Serialization.write
import org.apache.spark.SparkConf
import org.apache.spark.streaming._
import org.apache.spark.streaming.Interval
import org.apache.spark.streaming.kafka010._
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerConfig, ProducerRecord}
import org.apache.kafka.common.serialization.StringDeserializer
import org.apache.spark.streaming.dstream.DStream

object KafkaCatCount {
  def main(args: Array[String]): Unit = {
    // 1.初始化Spark配置信息
    val sparkconf: SparkConf=new SparkConf().setAppName("KafkaCatCount")
    // 2.初始化SparkStreamingContext
    val ssc = new StreamingContext(sparkconf, Seconds(5))
    ssc.checkpoint("file:///usr/local/spark-2.4.5-bin-hadoop2.7/taocode/kafka/checkpoint")

    val kafkaParams = Map[String, Object](
      "bootstrap.servers" -> "192.168.100.21:9092",
      "key.deserializer" -> classOf[StringDeserializer],
      "value.deserializer" -> classOf[StringDeserializer],
      "group.id" -> "use_a_separate_group_id_for_each_stream",
      "auto.offset.reset" -> "latest",
      "enable.auto.commit" -> (false: java.lang.Boolean)
    )
    val topics =Array("cat")

    //获取数据
    val stream = KafkaUtils.createDirectStream[String, String](
      ssc,
      LocationStrategies.PreferConsistent,
      ConsumerStrategies.Subscribe[String,String](topics,kafkaParams)
    )
    //打印数据
    val value: DStream[String] = stream.map(crd => crd.value())

    val words = value.flatMap(_.split(" ")).map((_,1))
    val wordCounts = words.updateStateByKey(
      (values:Seq[Int],state:Option[Int])=>{
        var newvalue =state.getOrElse(0)
        values.foreach(newvalue += _)
        Option(newvalue)
      }).foreachRDD(rdd => {
      if(rdd.count !=0 ){
        val props = new HashMap[String, Object]()
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "192.168.100.21:9092")
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
          "org.apache.kafka.common.serialization.StringSerializer")
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
          "org.apache.kafka.common.serialization.StringSerializer")
        // 实例化一个Kafka生产者
        val producer = new KafkaProducer[String, String](props)
        // rdd.collect即将rdd中数据转化为数组，然后write函数将rdd内容转化为json格式
        implicit val formats: DefaultFormats = DefaultFormats
        val str = write(rdd.collect)
        // 封装成Kafka消息，topic为"result"
        val message = new ProducerRecord[String, String]("cat_result", null, str)
        // 给Kafka发送消息
        producer.send(message)
      }
    })
    ssc.start()
    ssc.awaitTermination()
  }
}