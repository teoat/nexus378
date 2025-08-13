import { Controller, Post, Body } from '@nestjs/common';
import { AiFeedbackService } from './ai-feedback.service';
import { CreateFeedbackDto } from './dto/create-feedback.dto';
import { HelpAgentFeedback } from '@prisma/client';

@Controller('ai-feedback')
export class AiFeedbackController {
  constructor(private readonly aiFeedbackService: AiFeedbackService) {}

  @Post()
  create(
    @Body() createFeedbackDto: CreateFeedbackDto,
  ): Promise<HelpAgentFeedback> {
    return this.aiFeedbackService.create(createFeedbackDto);
  }
}
