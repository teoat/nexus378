import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { CreateMappingDto } from './dto/create-mapping.dto';
import { Mapping, MappingDocument } from './schemas/mapping.schema';

@Injectable()
export class MappingsService {
  constructor(
    @InjectModel(Mapping.name)
    private readonly mappingModel: Model<MappingDocument>,
  ) {}

  async create(createMappingDto: CreateMappingDto): Promise<Mapping> {
    const newMapping = new this.mappingModel(createMappingDto);
    return newMapping.save();
  }

  async findAll(caseId: string): Promise<Mapping[]> {
    return this.mappingModel.find({ caseId }).exec();
  }

  async update(
    id: string,
    updateMappingDto: UpdateMappingDto,
  ): Promise<Mapping> {
    return this.mappingModel
      .findByIdAndUpdate(id, updateMappingDto, { new: true })
      .exec();
  }
}
