import type { ButtonHTMLAttributes, ReactNode } from "react";

export interface BaseComponentProps {
  className?: string;
  children?: ReactNode;
  testId?: string;
}

type ButtonVariant = "primary" | "secondary" | "danger" | "warning" | "info";
type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps
  extends BaseComponentProps,
    Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className"> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  isDisabled?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}
