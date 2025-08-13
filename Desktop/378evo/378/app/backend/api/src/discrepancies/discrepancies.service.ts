import { Injectable } from '@nestjs/common';
import { RabbitMQService } from '../rabbitmq/rabbitmq.service';
import { TriggerAnalysisDto } from './dto/trigger-analysis.dto';
import { AppGateway } from '../websocket/websocket.gateway';
import { UpdateDiscrepancyDto } from './dto/update-discrepancy.dto';
import { PrismaService } from '../prisma/prisma.service';
import { Discrepancy } from '@prisma/client';

@Injectable()
export class DiscrepanciesService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly rabbitMQService: RabbitMQService,
    private readonly websocketGateway: AppGateway,
  ) {}

  async triggerAnalysis(
    triggerAnalysisDto: TriggerAnalysisDto,
  ): Promise<{ message: string }> {
    this.websocketGateway.sendAnalysisStarted({
      caseId: triggerAnalysisDto.caseId,
    });
    const message = JSON.stringify(triggerAnalysisDto);
    await this.rabbitMQService.sendMessage('discrepancy-analysis', message);
    return { message: 'Discrepancy analysis has been triggered.' };
  }

  async findAll(caseId: string): Promise<Discrepancy[]> {
    return this.prisma.discrepancy.findMany({ where: { caseId } });
  }

  update(
    id: number,
    updateDiscrepancyDto: UpdateDiscrepancyDto,
  ): Promise<Discrepancy | null> {
    return this.prisma.discrepancy.update({
      where: { id },
      data: updateDiscrepancyDto,
    });
  }
}
