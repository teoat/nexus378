import { Module } from '@nestjs/common';
import { DiscrepanciesController } from './discrepancies.controller';
import { DiscrepanciesService } from './discrepancies.service';
import { RabbitMQModule } from '../rabbitmq/rabbitmq.module';
import { WebSocketModule } from '../websocket/websocket.module';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [RabbitMQModule, WebSocketModule, PrismaModule],
  controllers: [DiscrepanciesController],
  providers: [DiscrepanciesService],
})
export class DiscrepancyModule {}
