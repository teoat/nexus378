import { Controller, Get, Post, Body, Param, Put } from '@nestjs/common';
import { MappingsService } from './mappings.service';
import { CreateMappingDto } from './dto/create-mapping.dto';

@Controller('mappings')
export class MappingsController {
  constructor(private readonly mappingsService: MappingsService) {}

  @Post()
  create(@Body() createMappingDto: CreateMappingDto) {
    return this.mappingsService.create(createMappingDto);
  }

  @Get(':caseId')
  findAll(@Param('caseId') caseId: string) {
    return this.mappingsService.findAll(caseId);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateMappingDto: UpdateMappingDto) {
    return this.mappingsService.update(id, updateMappingDto);
  }
}
