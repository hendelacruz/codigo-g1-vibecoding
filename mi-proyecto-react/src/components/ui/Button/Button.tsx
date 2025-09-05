import { forwardRef } from "react";
import type { ButtonProps } from "../../../types/components";

/**
 * Button component following Vibe Coding principles
 *
 * @param props - ButtonProps interface with all button properties
 * @returns JSX.Element - Rendered button component
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className = "",
      children,
      testId,
      variant = "primary",
      size = "md",
      isLoading = false,
      isDisabled = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      type = "button",
      ...rest
    },
    ref
  ) => {
    // Base classes for all button variants
    const baseClasses = [
      "inline-flex",
      "items-center",
      "justify-center",
      "font-medium",
      "rounded-lg",
      "transition-all",
      "duration-200",
      "focus:outline-none",
      "focus:ring-2",
      "focus:ring-offset-2",
      "disabled:opacity-50",
      "disabled:cursor-not-allowed",
      "disabled:pointer-events-none",
    ];

    // Variant-specific styling classes
    const variantClasses = {
      primary: [
        "bg-blue-600",
        "text-white",
        "hover:bg-blue-700",
        "focus:ring-blue-500",
        "active:bg-blue-800",
      ],
      secondary: [
        "bg-gray-200",
        "text-gray-900",
        "hover:bg-gray-300",
        "focus:ring-gray-500",
        "active:bg-gray-400",
      ],
      danger: [
        "bg-red-600",
        "text-white",
        "hover:bg-red-700",
        "focus:ring-red-500",
        "active:bg-red-800",
      ],
      warning: [
        "bg-yellow-500",
        "text-black",
        "hover:bg-yellow-600",
        "focus:ring-yellow-500",
        "active:bg-yellow-700",
      ],
      info: [
        "bg-blue-200",
        "text-blue-800",
        "hover:bg-blue-300",
        "focus:ring-blue-500",
        "active:bg-blue-400",
      ],
    };

    // Size-specific classes for padding and text size
    const sizeClasses = {
      sm: ["px-3", "py-1.5", "text-sm", "gap-1.5"],
      md: ["px-4", "py-2", "text-base", "gap-2"],
      lg: ["px-6", "py-3", "text-lg", "gap-2.5"],
    };

    // Width classes based on fullWidth prop
    const widthClasses = fullWidth ? ["w-full"] : [];

    // Combine all classes into final className string
    const buttonClasses = [
      ...baseClasses,
      ...variantClasses[variant],
      ...sizeClasses[size],
      ...widthClasses,
      className,
    ].join(" ");

    // Loading spinner component
    const LoadingSpinner = () => (
      <svg
        className="animate-spin h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    return (
      <button
        ref={ref}
        type={type}
        className={buttonClasses}
        disabled={isDisabled || isLoading}
        data-testid={testId}
        aria-disabled={isDisabled || isLoading}
        aria-busy={isLoading}
        {...rest}
      >
        {/* Left icon or loading spinner */}
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          leftIcon && (
            <span className="flex-shrink-0" aria-hidden="true">
              {leftIcon}
            </span>
          )
        )}

        {/* Button content */}
        {children && (
          <span className={isLoading ? "opacity-0" : ""}>{children}</span>
        )}

        {/* Right icon */}
        {!isLoading && rightIcon && (
          <span className="flex-shrink-0" aria-hidden="true">
            {rightIcon}
          </span>
        )}
      </button>
    );
  }
);

// Display name for debugging purposes
Button.displayName = "Button";
