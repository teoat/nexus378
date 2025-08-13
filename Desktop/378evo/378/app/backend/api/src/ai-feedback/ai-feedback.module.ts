import { Module } from '@nestjs/common';
import { AiFeedbackService } from './ai-feedback.service';
import { AiFeedbackController } from './ai-feedback.controller';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [PrismaModule],
  controllers: [AiFeedbackController],
  providers: [AiFeedbackService],
})
export class AiFeedbackModule {}
