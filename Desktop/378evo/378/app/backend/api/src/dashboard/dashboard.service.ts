import { Injectable } from '@nestjs/common';
import { AppGateway } from '../websocket/websocket.gateway';

@Injectable()
export class DashboardService {
  constructor(private readonly websocketGateway: AppGateway) {}

  getInsights() {
    // In a real implementation, this would fetch insights from a database
    // or another service. For now, we'll just return a dummy array.
    return [
      { id: 1, text: 'High-value transaction to a new vendor detected.' },
      { id: 2, text: 'Pattern of round-number payments identified.' },
    ];
  }
}
