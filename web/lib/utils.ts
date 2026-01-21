import { BaseResponseSchema, HttpValidationError } from "@/client"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getErrorMessage(error: HttpValidationError | BaseResponseSchema) {
  if ("detail" in error && Array.isArray(error.detail)) {
    return error.detail.map((e) => e.msg).join(", ")
  }
  return (error as BaseResponseSchema).message
}