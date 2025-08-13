import { IsUUID, IsNotEmpty } from 'class-validator';

export class TriggerAnalysisDto {
  @IsUUID()
  @IsNotEmpty()
  caseId: string;
}
