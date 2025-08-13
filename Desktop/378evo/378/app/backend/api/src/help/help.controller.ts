import { Controller, Post, Body, Req, UseGuards } from '@nestjs/common';
import { HelpService } from './help.service';
import { AuthGuard } from '../auth/auth.guard';
import { HelpContextDto } from './dto/help-context.dto';

@Controller('help')
@UseGuards(AuthGuard)
export class HelpController {
  constructor(private readonly helpService: HelpService) {}

  @Post('context')
  sendContext(
    @Body() context: HelpContextDto,
    @Req() req: { user: { id: string } },
  ) {
    return this.helpService.sendContext({ ...context, userId: req.user.id });
  }
}
