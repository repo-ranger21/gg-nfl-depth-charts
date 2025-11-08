export interface AutomationDTO {
    id: string;
    name: string;
    description: string;
    status: 'active' | 'inactive';
    createdAt: Date;
    updatedAt: Date;
}

export interface CreateAutomationDTO {
    name: string;
    description: string;
}

export interface UpdateAutomationDTO {
    name?: string;
    description?: string;
    status?: 'active' | 'inactive';
}