import {
  Controller,
  Post,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { DataIngestionService } from './data-ingestion.service';

@Controller('data-ingestion')
export class DataIngestionController {
  constructor(private readonly dataIngestionService: DataIngestionService) {}

  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  uploadFile(@UploadedFile() file: Express.Multer.File) {
    return this.dataIngestionService.processFile(file);
  }
}
