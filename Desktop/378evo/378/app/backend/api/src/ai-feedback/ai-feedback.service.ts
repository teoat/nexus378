import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateFeedbackDto } from './dto/create-feedback.dto';
import { HelpAgentFeedback } from '@prisma/client';

@Injectable()
export class AiFeedbackService {
  constructor(private prisma: PrismaService) {}

  async create(
    createFeedbackDto: CreateFeedbackDto,
  ): Promise<HelpAgentFeedback> {
    return this.prisma.helpAgentFeedback.create({
      data: createFeedbackDto,
    });
  }
}