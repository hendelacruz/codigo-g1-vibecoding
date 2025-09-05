/**
 * Datos de prueba para tareas (todos)
 * Estructura: id, name, is_finished, created_at, updated_at
 */

export interface Todo {
  id: number;
  name: string;
  is_finished: boolean;
  created_at: Date;
  updated_at: Date;
}

export const todos: Todo[] = [
  {
    id: 1,
    name: "Implementar autenticación de usuarios",
    is_finished: false,
    created_at: new Date("2024-01-15T09:00:00Z"),
    updated_at: new Date("2024-01-15T09:00:00Z"),
  },
  {
    id: 2,
    name: "Diseñar interfaz de dashboard",
    is_finished: true,
    created_at: new Date("2024-01-14T14:30:00Z"),
    updated_at: new Date("2024-01-16T10:15:00Z"),
  },
  {
    id: 3,
    name: "Configurar base de datos PostgreSQL",
    is_finished: true,
    created_at: new Date("2024-01-13T11:20:00Z"),
    updated_at: new Date("2024-01-14T16:45:00Z"),
  },
  {
    id: 4,
    name: "Crear componentes reutilizables",
    is_finished: false,
    created_at: new Date("2024-01-16T08:15:00Z"),
    updated_at: new Date("2024-01-16T08:15:00Z"),
  },
  {
    id: 5,
    name: "Implementar validación de formularios",
    is_finished: false,
    created_at: new Date("2024-01-17T13:45:00Z"),
    updated_at: new Date("2024-01-17T13:45:00Z"),
  },
  {
    id: 6,
    name: "Optimizar rendimiento de la aplicación",
    is_finished: false,
    created_at: new Date("2024-01-18T10:30:00Z"),
    updated_at: new Date("2024-01-18T10:30:00Z"),
  },
  {
    id: 7,
    name: "Escribir tests unitarios",
    is_finished: true,
    created_at: new Date("2024-01-12T15:20:00Z"),
    updated_at: new Date("2024-01-15T12:30:00Z"),
  },
  {
    id: 8,
    name: "Configurar CI/CD pipeline",
    is_finished: false,
    created_at: new Date("2024-01-19T09:45:00Z"),
    updated_at: new Date("2024-01-19T09:45:00Z"),
  },
  {
    id: 9,
    name: "Documentar API endpoints",
    is_finished: true,
    created_at: new Date("2024-01-11T16:10:00Z"),
    updated_at: new Date("2024-01-13T14:20:00Z"),
  },
  {
    id: 10,
    name: "Implementar sistema de notificaciones",
    is_finished: false,
    created_at: new Date("2024-01-20T11:00:00Z"),
    updated_at: new Date("2024-01-20T11:00:00Z"),
  },
];

// Función utilitaria para obtener tareas por estado
export const getTodosByStatus = (isFinished: boolean): Todo[] => {
  return todos.filter((todo) => todo.is_finished === isFinished);
};

// Función utilitaria para obtener una tarea por ID
export const getTodoById = (id: number): Todo | undefined => {
  return todos.find((todo) => todo.id === id);
};

// Función utilitaria para contar tareas
export const getTodosCount = (): {
  total: number;
  completed: number;
  pending: number;
} => {
  const completed = todos.filter((todo) => todo.is_finished).length;
  const pending = todos.filter((todo) => !todo.is_finished).length;

  return {
    total: todos.length,
    completed,
    pending,
  };
};
