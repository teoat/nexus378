import { IsString, IsNotEmpty } from 'class-validator';

export class HelpContextDto {
  @IsString()
  @IsNotEmpty()
  page: string;

  @IsString()
  @IsNotEmpty()
  component: string;
}
