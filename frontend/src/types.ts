// src/types.ts
export interface User {
  id: string;
  name: string;
  role: string;
  profile?: {
    github?: string;
    skills?: string[];
  }
}

export interface GraphData {
  nodes: User[];
  links: {
    source: string;
    target: string;
  }[];
}
