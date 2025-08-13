import { Injectable } from '@nestjs/common';
import { CreateTodoDto } from './dto/create-todo.dto';

@Injectable()
export class TodosService {
  create(createTodoDto: CreateTodoDto) {
    console.log(createTodoDto);
    return 'This action adds a new todo (placeholder)';
  }

  findAll() {
    return `This action returns all todos (placeholder)`;
  }

  findOne(id: number) {
    return `This action returns a #${id} todo (placeholder)`;
  }

  remove(id: number) {
    return `This action removes a #${id} todo (placeholder)`;
  }
}
