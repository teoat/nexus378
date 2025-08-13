import { TodosService } from './todos.service';
import { CreateTodoDto } from './dto/create-todo.dto';
export declare class TodosController {
    private readonly todosService;
    constructor(todosService: TodosService);
    create(createTodoDto: CreateTodoDto): Promise<import("./schemas/todo.schema").Todo>;
}
