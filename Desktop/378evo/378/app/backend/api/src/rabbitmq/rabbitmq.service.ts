import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { connect, Connection, Channel, ConsumeMessage } from 'amqplib';

@Injectable()
export class RabbitMQService implements OnModuleInit, OnModuleDestroy {
  private connection: Connection;
  private channel: Channel;

  async onModuleInit() {
    this.connection = await connect('amqp://user:password@rabbitmq:5672');
    this.channel = await this.connection.createChannel();
  }

  async onModuleDestroy() {
    await this.channel.close();
    await this.connection.close();
  }

  async sendMessage(queue: string, message: string) {
    await this.channel.assertQueue(queue, { durable: false });
    this.channel.sendToQueue(queue, Buffer.from(message));
  }

  async consume(queue: string, callback: (msg: ConsumeMessage | null) => void) {
    await this.channel.assertQueue(queue, { durable: false });
    await this.channel.consume(queue, (msg) => {
      callback(msg);
      if (msg) {
        this.channel.ack(msg);
      }
    });
  }
}
