import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class CaseVersioningService {
  constructor(private readonly prisma: PrismaService) {}

  async createSnapshot(caseId: string, description: string, userId: string) {
    const caseData = await this.prisma.case.findUnique({
      where: { id: caseId },
      include: {
        transactions: true,
        matchingResults: true,
        fraudAlerts: true,
      },
    });

    if (!caseData) {
      throw new Error('Case not found');
    }

    const snapshotData = {
      ...caseData,
      transactions: caseData.transactions.map((t) => ({
        ...t,
        id: t.id.toString(),
      })),
      matchingResults: caseData.matchingResults.map((mr) => ({
        ...mr,
        id: mr.id.toString(),
        transactionAId: mr.transactionAId.toString(),
        transactionBId: mr.transactionBId.toString(),
      })),
      fraudAlerts: caseData.fraudAlerts.map((fa) => ({
        ...fa,
        id: fa.id.toString(),
        transactionId: fa.transactionId?.toString(),
      })),
    };

    const snapshot = await this.prisma.caseSnapshot.create({
      data: {
        caseId,
        description,
        createdById: userId,
        snapshot: snapshotData,
      },
    });

    return snapshot;
  }
}
