import { Response } from "express";

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  meta?: Record<string, any>;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

export function successResponse<T>(
  res: Response,
  data: T,
  meta: Record<string, any> = {},
  statusCode: number = 200
): Response {
  const body: ApiResponse<T> = {
    success: true,
    data,
    meta: {
      timestamp: new Date().toISOString(),
      ...meta,
    },
  };
  return res.status(statusCode).json(body);
}

export function errorResponse(
  res: Response,
  code: string,
  message: string,
  statusCode: number = 400,
  details: any = null
): Response {
  const body: ApiResponse = {
    success: false,
    error: {
      code,
      message,
      ...(details ? { details } : {}),
    },
    meta: {
      timestamp: new Date().toISOString(),
    },
  };
  return res.status(statusCode).json(body);
}
