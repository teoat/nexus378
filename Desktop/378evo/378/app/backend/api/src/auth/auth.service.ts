import { Injectable, UnauthorizedException, Logger } from '@nestjs/common';
import { UserService } from '../users/user.service';
import { JwtService } from '@nestjs/jwt';
import { LoginDto } from './dto/login.dto';
import * as bcrypt from 'bcrypt';
import { User } from '@prisma/client';

@Injectable()
export class AuthService {
  private readonly logger = new Logger(AuthService.name);

  constructor(
    private userService: UserService,
    private jwtService: JwtService,
  ) {}

  /**
   * Validates a user's credentials.
   * @param username The user's email address.
   * @param pass The user's password.
   * @returns The user object without the hashed password, or null if validation fails.
   */
  async validateUser(
    username: string,
    password: string,
  ): Promise<Omit<User, 'hashedPassword'> | null> {
    const user = await this.userService.findOne(username);
    if (user && (await bcrypt.compare(password, user.hashedPassword))) {
      delete user.hashedPassword;
      return user;
    }
    return null;
  }

  /**
   * Logs in a user and returns a JWT access token.
   * @param loginDto The login data transfer object.
   * @returns An object containing the access token.
   */
  async login(loginDto: LoginDto) {
    this.logger.log(`Login attempt for user: ${loginDto.email}`);
    const user = await this.validateUser(loginDto.email, loginDto.password);
    if (!user) {
      this.logger.warn(`Failed login attempt for user: ${loginDto.email}`);
      throw new UnauthorizedException('Invalid credentials');
    }
    const payload = { username: user.email, sub: user.id };
    return {
      access_token: this.jwtService.sign(payload),
    };
  }
}
