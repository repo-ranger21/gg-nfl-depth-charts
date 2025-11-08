export interface Automation {
    id: string;
    name: string;
    description: string;
    status: 'active' | 'inactive';
    createdAt: Date;
    updatedAt: Date;
}

export interface AutomationCreateInput {
    name: string;
    description: string;
}

export interface AutomationUpdateInput {
    name?: string;
    description?: string;
    status?: 'active' | 'inactive';
}