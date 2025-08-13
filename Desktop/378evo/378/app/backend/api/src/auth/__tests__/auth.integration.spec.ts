import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { AuthModule } from '../auth.module';
import { UserModule } from '../../users/user.module';
import { PrismaService } from '../../prisma/prisma.service';
import { ConfigService } from '@nestjs/config';
import { JwtStrategy } from '../jwt.strategy';
import * as bcrypt from 'bcrypt';

describe('AuthController (integration)', () => {
  let app: INestApplication;
  const mockPrismaService = {
    user: {
      findUnique: jest.fn(),
    },
  };

  beforeEach(async () => {
    const hashedPassword = await bcrypt.hash('password', 10);
    mockPrismaService.user.findUnique.mockResolvedValue({
      id: '1',
      email: 'testuser',
      hashedPassword,
      fullName: 'Test User',
    });

    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AuthModule, UserModule],
      providers: [
        JwtStrategy,
        {
          provide: ConfigService,
          useValue: {
            get: jest.fn((key: string) => {
              if (key === 'JWT_SECRET') {
                return 'test-secret';
              }
              return null;
            }),
          },
        },
      ],
    })
      .overrideProvider(PrismaService)
      .useValue(mockPrismaService)
      .compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/auth/login (POST) with valid credentials', () => {
    return request(app.getHttpServer())
      .post('/auth/login')
      .send({ username: 'testuser', password: 'password' })
      .expect(201)
      .then((response) => {
        expect(response.body).toHaveProperty('access_token');
      });
  });

  it('/auth/login (POST) with invalid credentials', () => {
    mockPrismaService.user.findUnique.mockResolvedValue(null);
    return request(app.getHttpServer())
      .post('/auth/login')
      .send({ username: 'testuser', password: 'wrongpassword' })
      .expect(401);
  });

  afterAll(async () => {
    await app.close();
  });
});