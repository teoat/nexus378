import { Controller, Post, Body, Param, Req, UseGuards } from '@nestjs/common';
import { ReconciliationService } from './reconciliation.service';
import { StartReconciliationDto } from './dto/start-reconciliation.dto';
import { AuthGuard } from '../auth/auth.guard';

@Controller('cases/:caseId/reconciliation')
@UseGuards(AuthGuard)
export class ReconciliationController {
  constructor(private readonly reconciliationService: ReconciliationService) {}

  @Post('start')
  async start(
    @Param('caseId') caseId: string,
    @Body() startReconciliationDto: StartReconciliationDto,
    @Req() req: { user: { id: string } },
  ) {
    return this.reconciliationService.startReconciliation(
      caseId,
      startReconciliationDto.fileId,
      startReconciliationDto.mappingId,
      startReconciliationDto.scope,
      startReconciliationDto.scopeValue,
      req.user.id,
    );
  }
}
