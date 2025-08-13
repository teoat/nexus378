import { Controller, Post, Body, Get, Param, Patch } from '@nestjs/common';
import { DiscrepanciesService } from './discrepancies.service';
import { TriggerAnalysisDto } from './dto/trigger-analysis.dto';
import { UpdateDiscrepancyDto } from './dto/update-discrepancy.dto';

@Controller('discrepancies')
export class DiscrepanciesController {
  constructor(private readonly discrepanciesService: DiscrepanciesService) {}

  @Post('analyze')
  triggerAnalysis(@Body() triggerAnalysisDto: TriggerAnalysisDto) {
    return this.discrepanciesService.triggerAnalysis(triggerAnalysisDto);
  }

  @Get(':caseId')
  findAll(@Param('caseId') caseId: string) {
    return this.discrepanciesService.findAll(caseId);
  }

  @Patch(':id')
  update(
    @Param('id') id: string,
    @Body() updateDiscrepancyDto: UpdateDiscrepancyDto,
  ) {
    return this.discrepanciesService.update(id, updateDiscrepancyDto);
  }
}
