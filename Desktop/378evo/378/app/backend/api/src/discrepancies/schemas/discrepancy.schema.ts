import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Schema as MongooseSchema } from 'mongoose';

export type DiscrepancyDocument = Discrepancy & Document;

@Schema({ timestamps: true })
export class Discrepancy {
  @Prop({ required: true, type: MongooseSchema.Types.UUID })
  caseId: string;

  @Prop({
    required: true,
    enum: ['missing_statement', 'balance_mismatch', 'unclassified_transaction'],
  })
  type: string;

  @Prop({ required: true })
  description: string;

  @Prop({
    required: true,
    enum: ['open', 'resolved', 'ignored'],
    default: 'open',
  })
  status: string;
}

export const DiscrepancySchema = SchemaFactory.createForClass(Discrepancy);
