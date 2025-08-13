import { IsString, IsNotEmpty, IsIn } from 'class-validator';

export class UpdateDiscrepancyDto {
  @IsString()
  @IsNotEmpty()
  @IsIn(['resolved', 'ignored'])
  status: 'resolved' | 'ignored';
}
