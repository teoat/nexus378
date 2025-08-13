import { IsString, IsNotEmpty, IsIn, IsOptional } from 'class-validator';

export class StartReconciliationDto {
  @IsString()
  @IsNotEmpty()
  fileId: string;

  @IsString()
  @IsNotEmpty()
  mappingId: string;

  @IsString()
  @IsNotEmpty()
  @IsIn(['month', 'trimester', 'all'])
  scope: string;

  @IsString()
  @IsOptional()
  scopeValue?: string;
}
