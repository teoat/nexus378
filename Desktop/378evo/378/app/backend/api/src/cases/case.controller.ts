import { Controller, Post, Body, Param, Req, UseGuards } from '@nestjs/common';
import { CaseService } from './case.service';
import { CreateCaseDto } from './dto/create-case.dto';
import { AuthGuard } from '@nestjs/passport';
import { CaseVersioningService } from './case-versioning.service';
import { TimeTravelService } from './time-travel.service';

@Controller('cases')
@UseGuards(AuthGuard('jwt'))
export class CaseController {
  constructor(
    private readonly caseService: CaseService,
    private readonly caseVersioningService: CaseVersioningService,
    private readonly timeTravelService: TimeTravelService,
  ) {}

  @Post()
  create(
    @Body() createCaseDto: CreateCaseDto,
    @Req() req: { user: { id: string } },
  ) {
    return this.caseService.create(createCaseDto, req.user.id);
  }

  @Post(':id/snapshot')
  createSnapshot(
    @Param('id') id: string,
    @Body('description') description: string,
    @Req() req: { user: { id: string } },
  ) {
    return this.caseVersioningService.createSnapshot(
      id,
      description,
      req.user.id,
    );
  }

  @Post(':id/rewind')
  rewindAndRerun(
    @Param('id') id: string,
    @Body('snapshotId') snapshotId: string,
  ) {
    return this.timeTravelService.rewindAndRerun(id, snapshotId);
  }
}
