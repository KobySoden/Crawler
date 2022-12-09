import pika

def connect():
    #connect to broker
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.1.245'))
    return connection.channel()

"""send message via channel to q aka topic"""
def send(msg, channel, q):
    #create a topic to send messages to
    channel.queue_declare(queue=q)

    channel.basic_publish(exchange='',
                        routing_key=q,
                        body=msg)

    #print(" [x] Sent " + msg)

def recieve(q, channel, callback):
    channel.queue_declare(queue=q)

    channel.basic_consume(queue=q,
                        auto_ack=True, #remove this for manual message delation after consumption
                        on_message_callback=callback)

    channel.start_consuming()

def decode(ch, method, properties, body):
    body.decode()
    #stop consuming loop
    #channel.stop_consuming()
    print(body.decode())

if __name__ == "__main__":
    #channel = connect()
    #send('https://www.google.com', channel, 'hello')
    #channel.close()

    channel = connect()
    print(recieve('https://en.wikipedia.org', channel, decode))
    channel.close()
