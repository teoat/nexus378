import {
  IsString,
  IsNotEmpty,
  IsUUID,
  IsArray,
  ValidateNested,
} from 'class-validator';
import { Type } from 'class-transformer';

class MappingPairDto {
  @IsString()
  @IsNotEmpty()
  sourceColumn: string;

  @IsString()
  @IsNotEmpty()
  targetField: string;
}

export class CreateMappingDto {
  @IsUUID()
  @IsNotEmpty()
  caseId: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => MappingPairDto)
  mappings: MappingPairDto[];
}
