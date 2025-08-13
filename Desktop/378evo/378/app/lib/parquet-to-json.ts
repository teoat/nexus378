
import { ParquetReader } from 'parquetjs-lite';

export async function parquetToJson(fileBuffer: Buffer): Promise<any[]> {
  const reader = await ParquetReader.openBuffer(fileBuffer);
  const cursor = reader.getCursor();
  const records = [];
  let record = null;
  while (record = await cursor.next()) {
    records.push(record);
  }
  await reader.close();
  return records;
}
