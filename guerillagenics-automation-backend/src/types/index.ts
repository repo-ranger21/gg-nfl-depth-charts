export interface HealthResponse {
    status: string;
    timestamp: Date;
}

export interface AutomationData {
    id: string;
    name: string;
    status: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface AutomationDTO {
    name: string;
    status: string;
}

export interface ErrorResponse {
    message: string;
    code?: number;
}