import { Test, TestingModule } from '@nestjs/testing';
import { DiscrepanciesService } from './discrepancies.service';
import { getModelToken } from '@nestjs/mongoose';
import { RabbitMQService } from '../rabbitmq/rabbitmq.service';
import { AppGateway } from '../websocket/websocket.gateway';

describe('DiscrepanciesService', () => {
  let service: DiscrepanciesService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        DiscrepanciesService,
        {
          provide: getModelToken('Discrepancy'),
          useValue: {},
        },
        {
          provide: RabbitMQService,
          useValue: {
            sendMessage: jest.fn(),
          },
        },
        {
          provide: AppGateway,
          useValue: {
            sendAnalysisStarted: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<DiscrepanciesService>(DiscrepanciesService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
