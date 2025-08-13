import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { MappingsService } from './mappings.service';
import { MappingsController } from './mappings.controller';
import { Mapping, MappingSchema } from './schemas/mapping.schema';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: Mapping.name, schema: MappingSchema }]),
  ],
  controllers: [MappingsController],
  providers: [MappingsService],
})
export class MappingsModule {}
