import { Injectable } from '@nestjs/common';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import FormData = require('form-data');
import { IngestionResponseDto } from './dto/ingestion-response.dto';

@Injectable()
export class DataIngestionService {
  constructor(private readonly httpService: HttpService) {}

  async processFile(file: Express.Multer.File): Promise<IngestionResponseDto> {
    const formData = new FormData();
    formData.append('file', file.buffer, file.originalname);

    const response = await firstValueFrom(
      this.httpService.post('http://ingestion-service:8080/upload', formData, {
        headers: {
          ...formData.getHeaders(),
        },
      }),
    );

    return response.data as IngestionResponseDto;
  }
}