import { Injectable } from '@nestjs/common';
import { RabbitMQService } from '../rabbitmq/rabbitmq.service';
import { HelpContextDto } from './dto/help-context.dto';

@Injectable()
export class HelpService {
  constructor(private readonly rabbitMQService: RabbitMQService) {}

  async sendContext(context: HelpContextDto & { userId: string }) {
    await this.rabbitMQService.sendMessage(
      'help.context',
      JSON.stringify(context),
    );
    return { message: 'Context sent to HelpAgent.' };
  }
}
