using System;
using System.Threading;
using System.Threading.Tasks;
using Confluent.Kafka;

namespace Producer
{
    class Program
    {
        static async Task Main(string[] args)
        {
            //const string topicName = "fbEvents";
            string topicName = "demoBizNet";
            //Topic name aus Argumentsliste übernehmen
            if (args.Length > 0)
            {
                topicName = args[0];
            }
            Console.WriteLine("Listen to Kafka topic: " + topicName);


            var pConfig = new ProducerConfig
            {
                //BootstrapServers = "kafka-1:9092",
                BootstrapServers = "localhost:9092",
                //SaslMechanism = SaslMechanism.Plain,
                //SecurityProtocol = SecurityProtocol.SaslSsl,
                // Note: If your root CA certificates are in an unusual location you
                // may need to specify this using the SslCaLocation property.
                //SaslUsername = "HD2RDLULRTRHU7Z7",
                //SaslPassword = "L8bTbJHEmeifXzEBzeFanqM7n88lxHvlqq/xctMaVGaZSlagXtdmRDKO/dESQ3oJ"
            };

            using (var producer = new ProducerBuilder<Null, string>(pConfig).Build())
            {
                var idx = 0;
                while (true)
                {
                    var val = $"test {DateTime.Now: yyyy.MM.dd-HH:mm:ss}";
                    var result = await producer.ProduceAsync(topicName, new Message<Null, string> {Value = val })
                        .ContinueWith(task => task.IsFaulted
                            ? $"error producing message: {task.Exception.Message}"
                            : $"produced to: {task.Result.TopicPartitionOffset}: {val}");

                    Console.WriteLine(result);
                    //// block until all in-flight produce requests have completed (successfully
                    //// or otherwise) or 10s has elapsed.
                    //producer.Flush(TimeSpan.FromSeconds(10));
                    Thread.Sleep(2000);
                    idx++;
                    if (idx > 10)
                    {
                        break;
                    }
                }
            }
        }
    }
}
