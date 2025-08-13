import { Module } from '@nestjs/common';
import { AiClientService } from './ai-client.service';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { join } from 'path';

@Module({
  imports: [
    ClientsModule.register([
      {
        name: 'AI_SERVICE',
        transport: Transport.GRPC,
        options: {
          package: 'ai_service',
          protoPath: join(process.cwd(), '../../protos/ai_service.proto'),
        },
      },
    ]),
  ],
  providers: [AiClientService],
  exports: [AiClientService],
})
export class AiClientModule {}
