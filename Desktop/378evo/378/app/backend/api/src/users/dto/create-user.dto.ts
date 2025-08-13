import {
  IsEmail,
  IsString,
  IsNotEmpty,
  IsOptional,
  IsArray,
} from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @IsString()
  @IsNotEmpty()
  password: string;

  @IsString()
  @IsOptional()
  fullName?: string;

  @IsArray()
  @IsString({ each: true })
  @IsOptional()
  roles?: string[];
}
