import { CacheModule } from '@nestjs/cache-manager';
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { UserModule } from './users/user.module';
import { CaseModule } from './cases/case.module';
import { DataIngestionModule } from './data-ingestion/data-ingestion.module';
import { MappingsModule } from './mappings/mappings.module';
import { DiscrepancyModule } from './discrepancies/discrepancy.module';
import { RabbitMQModule } from './rabbitmq/rabbitmq.module';
import { AiClientModule } from './ai-client/ai-client.module';
import { WebSocketModule } from './websocket/websocket.module';
import { ReconciliationModule } from './reconciliation/reconciliation.module';
import { APP_GUARD } from '@nestjs/core';
import { JwtAuthGuard } from './auth/jwt-auth.guard';
import { TodosModule } from './todos/todos.module';
import { LoggerModule } from './logger/logger.module';
import { ReportingModule } from './reporting/reporting.module';
import { TrainingModule } from './training/training.module';
import { AiFeedbackModule } from './ai-feedback/ai-feedback.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { HelpModule } from './help/help.module';

@Module({
  imports: [
    CacheModule.register({
      isGlobal: true, // Make cache available everywhere
      ttl: 60000, // 60 seconds
    }),
    AuthModule,
    UserModule,
    CaseModule,
    DataIngestionModule,
    MappingsModule,
    DiscrepancyModule,
    RabbitMQModule,
    AiClientModule,
    WebSocketModule,
    ReconciliationModule,
    TodosModule,
    LoggerModule,
    ReportingModule,
    TrainingModule,
    AiFeedbackModule,
    DashboardModule,
    HelpModule,
  ],
  controllers: [AppController],
  providers: [
    AppService,
    {
      provide: APP_GUARD,
      useClass: JwtAuthGuard,
    },
  ],
})
export class AppModule {}
