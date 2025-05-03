import { HttpError, HttpValidationError } from "@viralink-ai/sdk";

export class AppError extends Error {}

export class UnauthenticatedError extends AppError {}

export function strError(error: HttpError | HttpValidationError): string {
  if (error.detail && Array.isArray(error.detail)) {
    return error.detail.map((e) => e.msg).join(", ");
  }
  return error.detail || "Unknown error";
}
