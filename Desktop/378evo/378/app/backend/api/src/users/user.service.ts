import { Injectable, ConflictException } from '@nestjs/common';
import { CreateUserDto } from './dto/create-user.dto';
import { PrismaService } from '../prisma/prisma.service'; // Assuming prisma service is in a shared location
import * as bcrypt from 'bcrypt';

@Injectable()
export class UserService {
  constructor(private prisma: PrismaService) {}

  async create(createUserDto: CreateUserDto) {
    const { email, password, fullName } = createUserDto;

    // 1. Check for existing user
    const existingUser = await this.prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      throw new ConflictException('A user with this email already exists.');
    }

    // 2. Hash password
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // 3. Save the new user to the database
    const newUser = await this.prisma.user.create({
      data: {
        email,
        hashedPassword,
        fullName,
      },
    });

    // 4. Return the user object, omitting the password
    // It's a security best practice to not send the hash back to the client
    delete newUser.hashedPassword;
    return newUser;
  }

  findAll() {
    return `This action returns all users (placeholder)`;
  }

  async findOne(email: string) {
    return this.prisma.user.findUnique({
      where: { email },
    });
  }

  remove(id: string) {
    return `This action removes a #${id} user (placeholder)`;
  }
}
