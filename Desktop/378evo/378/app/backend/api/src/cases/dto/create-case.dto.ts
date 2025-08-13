import { IsString, IsNotEmpty, IsOptional, IsUUID } from 'class-validator';

export class CreateCaseDto {
  @IsString()
  @IsNotEmpty()
  caseName: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsUUID()
  @IsOptional()
  leadInvestigatorId?: string;
}
