import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class TimeTravelService {
  constructor(private readonly prisma: PrismaService) {}

  async rewindAndRerun(caseId: string, snapshotId: string) {
    const snapshot = await this.prisma.caseSnapshot.findUnique({
      where: { id: snapshotId },
    });

    if (!snapshot || snapshot.caseId !== caseId) {
      throw new Error('Snapshot not found or does not belong to the case');
    }

    // In a real implementation, you would use the snapshot data
    // to overwrite the current case state and trigger a new analysis.
    // For now, we'll just log the snapshot data.
    console.log('Rewinding to snapshot:', snapshot.snapshot);

    return { message: `Case ${caseId} rewound to snapshot ${snapshotId}` };
  }
}
