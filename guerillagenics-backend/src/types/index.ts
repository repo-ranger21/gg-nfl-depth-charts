export type AutomationRequest = {
    decisionId: string;
    parameters: Record<string, any>;
};

export type KPIUpdate = {
    kpiId: string;
    value: number;
};

export type RolloutPlan = {
    planId: string;
    steps: Array<string>;
};

export interface User {
    id: string;
    username: string;
    email: string;
    passwordHash: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface AuthPayload {
    userId: string;
    username: string;
    email: string;
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}