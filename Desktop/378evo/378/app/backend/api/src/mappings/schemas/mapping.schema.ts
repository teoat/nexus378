import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Schema as MongooseSchema } from 'mongoose';

export type MappingDocument = Mapping & Document;

@Schema({ _id: false }) // _id: false because this will be a subdocument
class MappingPair {
  @Prop({ required: true })
  sourceColumn: string;

  @Prop({ required: true })
  targetField: string;
}

const MappingPairSchema = SchemaFactory.createForClass(MappingPair);

@Schema({ timestamps: true })
export class Mapping {
  @Prop({ required: true, type: MongooseSchema.Types.UUID })
  caseId: string;

  @Prop({ type: [MappingPairSchema], required: true })
  mappings: MappingPair[];
}

export const MappingSchema = SchemaFactory.createForClass(Mapping);
