import { Model } from 'mongoose';
import { Todo, TodoDocument } from './schemas/todo.schema';
import { CreateTodoDto } from './dto/create-todo.dto';
export declare class TodosService {
    private readonly todoModel;
    constructor(todoModel: Model<TodoDocument>);
    create(createTodoDto: CreateTodoDto): Promise<Todo>;
}
