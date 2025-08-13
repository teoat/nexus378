import { Injectable, OnModuleInit, Inject } from '@nestjs/common';
import type { ClientGrpc } from '@nestjs/microservices';
import { Observable } from 'rxjs';
import { TransactionRiskDto } from './dto/transaction-risk.dto';
import { join } from 'path';

interface AIService {
  getTransactionRisk(data: {
    transaction_id: string;
  }): Observable<TransactionRiskDto>;
}

@Injectable()
export class AiClientService implements OnModuleInit {
  private aiService: AIService;

  constructor(@Inject('AI_SERVICE') private client: ClientGrpc) {}

  onModuleInit() {
    this.aiService = this.client.getService<AIService>('AIService');
  }

  getTransactionRisk(transactionId: string): Observable<TransactionRiskDto> {
    return this.aiService.getTransactionRisk({ transaction_id: transactionId });
  }
}
