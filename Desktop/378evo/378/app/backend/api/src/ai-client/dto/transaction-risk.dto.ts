import { IsString, IsNotEmpty, IsNumber, IsBoolean } from 'class-validator';

export class TransactionRiskDto {
  @IsString()
  @IsNotEmpty()
  transaction_id: string;

  @IsNumber()
  fraud_score: number;

  @IsBoolean()
  is_high_risk: boolean;
}
