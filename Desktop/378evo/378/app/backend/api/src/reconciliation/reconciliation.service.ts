import { Injectable } from '@nestjs/common';
import { RabbitMQService } from '../rabbitmq/rabbitmq.service';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class ReconciliationService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly rabbitMQService: RabbitMQService,
  ) {}

  async startReconciliation(
    caseId: string,
    fileId: string,
    mappingId: string,
    scope: string,
    scopeValue: string,
    userId: string,
  ) {
    const job = await this.prisma.reconciliationJob.create({
      data: {
        caseId,
        scope,
        scopeValue,
      },
    });

    await this.rabbitMQService.sendMessage(
      'reconciliation.start',
      JSON.stringify({
        jobId: job.id,
        caseId,
        fileId,
        mappingId,
        scope,
        scopeValue,
        requestedBy: userId,
      }),
    );

    return job;
  }
}
