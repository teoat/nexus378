import {
  IsString,
  IsNotEmpty,
  IsIn,
  IsJSON,
  IsOptional,
} from 'class-validator';

export class CreateFeedbackDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @IsString()
  @IsNotEmpty()
  suggestionId: string;

  @IsString()
  @IsIn(['helpful', 'unhelpful', 'inaccurate'])
  feedback: string;

  @IsJSON()
  @IsOptional()
  context?: string;
}
