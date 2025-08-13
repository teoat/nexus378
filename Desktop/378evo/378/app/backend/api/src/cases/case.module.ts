import { Module } from '@nestjs/common';
import { CaseService } from './case.service';
import { CaseController } from './case.controller';
import { CaseVersioningService } from './case-versioning.service';
import { TimeTravelService } from './time-travel.service';

@Module({
  controllers: [CaseController],
  providers: [CaseService, CaseVersioningService, TimeTravelService],
})
export class CaseModule {}
