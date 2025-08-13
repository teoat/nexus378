import {
  SubscribeMessage,
  WebSocketGateway,
  OnGatewayInit,
  WebSocketServer,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Logger } from '@nestjs/common';
import { Socket, Server } from 'socket.io';
import { RabbitMQService } from '../rabbitmq/rabbitmq.service';
import {
  AnalysisStarted,
  AnalysisProgress,
  AnalysisComplete,
  MatchResultPayload,
  UnmatchResultPayload,
} from '@app/types';

@WebSocketGateway()
export class AppGateway
  implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer() server: Server;
  private logger: Logger = new Logger('AppGateway');

  constructor(private readonly rabbitMQService: RabbitMQService) {}

  @SubscribeMessage('msgToServer')
  handleMessage(client: Socket, payload: string): void {
    this.server.emit('msgToClient', payload);
  }

  async afterInit(server: Server) {
    this.logger.log('Init');
    await this.rabbitMQService.consume('reconciliation.results', (msg) => {
      if (msg !== null) {
        const message = JSON.parse(msg.content.toString());
        this.logger.log(
          `Received reconciliation result: ${JSON.stringify(message)}`,
        );
        // Assuming the message contains a 'type' field to distinguish between match and unmatch
        if (message.type === 'match') {
          this.server.emit('match-result', message.data as MatchResultPayload);
        } else {
          this.server.emit(
            'unmatch-result',
            message.data as UnmatchResultPayload,
          );
        }
      }
    });
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  handleConnection(client: Socket) {
    this.logger.log(`Client connected: ${client.id}`);
  }

  sendAnalysisStarted(payload: AnalysisStarted) {
    this.server.emit('analysisStarted', payload);
  }

  sendAnalysisProgress(payload: AnalysisProgress) {
    this.server.emit('analysisProgress', payload);
  }

  sendAnalysisComplete(payload: AnalysisComplete) {
    this.server.emit('analysisComplete', payload);
  }
}
