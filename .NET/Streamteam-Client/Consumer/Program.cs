using System;
using System.Threading;
using Confluent.Kafka;

namespace Consumer
{
    class Program
    {
        static void Main(string[] args)
        {
            //const string topicName = "fbEvents";
            string topicName = "rawGames";
            //Topic name aus Argumentsliste übernehmen
            if(args.Length > 0)
            {
                topicName = args[0];
            }
            Console.WriteLine("Listen to Kafka topic: " + topicName);

            //foreach (string arg in args)
            //{
            //    Console.WriteLine("Listen to Kafka topic: " + arg);
            //}

            var cConfig = new ConsumerConfig
            {
                //BootstrapServers = "kafka-1:9092",
                BootstrapServers = "localhost:9092",
                //BootstrapServers = "pkc-lq8gm.westeurope.azure.confluent.cloud:9092",
                //SaslMechanism = SaslMechanism.Plain,
                //SecurityProtocol = SecurityProtocol.SaslSsl,
                //SaslUsername = "HD2RDLULRTRHU7Z7",
                //SaslPassword = "L8bTbJHEmeifXzEBzeFanqM7n88lxHvlqq/xctMaVGaZSlagXtdmRDKO/dESQ3oJ",
                GroupId = Guid.NewGuid().ToString()
                //AutoOffsetReset = AutoOffsetReset.Earliest
            };


            using (var consumer = new ConsumerBuilder<string, string>(cConfig).Build())
            {
                consumer.Subscribe(topicName);
                while (true)
                {
                    try
                    {
                        var consumeResult = consumer.Consume();
                        Console.WriteLine($"consumed Key: {consumeResult.Key}; Value {consumeResult.Value}");
                    }
                    catch (ConsumeException e)
                    {
                        Console.WriteLine($"consume error: {e.Error.Reason}");
                    }

                    //Thread.Sleep(1000);
                    //Thread.Sleep(30);
                }

                consumer.Close();
            }
        }
    }
}
