import { Module } from '@nestjs/common';
import { ReconciliationController } from './reconciliation.controller';
import { ReconciliationService } from './reconciliation.service';
import { RabbitMQModule } from '../rabbitmq/rabbitmq.module';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [RabbitMQModule, PrismaModule],
  controllers: [ReconciliationController],
  providers: [ReconciliationService],
})
export class ReconciliationModule {}
