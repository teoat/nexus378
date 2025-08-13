import { Injectable } from '@nestjs/common';
import { CreateCaseDto } from './dto/create-case.dto';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class CaseService {
  constructor(private readonly prisma: PrismaService) {}

  create(createCaseDto: CreateCaseDto, userId: string) {
    return this.prisma.case.create({
      data: {
        ...createCaseDto,
        leadInvestigatorId: userId,
      },
    });
  }

  findAll() {
    return this.prisma.case.findMany();
  }

  findOne(id: string) {
    return this.prisma.case.findUnique({ where: { id } });
  }

  remove(id: string) {
    return this.prisma.case.delete({ where: { id } });
  }
}
