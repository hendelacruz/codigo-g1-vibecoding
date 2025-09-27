import React from 'react'
import { cn } from '../../lib/utils'

// Card component props - extends HTML div attributes for flexibility
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "rounded-lg border border-gray-200 bg-white text-gray-950 shadow-sm",
          className
        )}
        {...props}
      />
    )
  }
)

Card.displayName = "Card"

// CardHeader component props - extends HTML div attributes for flexibility
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("flex flex-col space-y-1.5 p-6", className)}
        {...props}
      />
    )
  }
)

CardHeader.displayName = "CardHeader"

// CardTitle component props - extends HTML heading attributes for flexibility
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

export const CardTitle = React.forwardRef<HTMLParagraphElement, CardTitleProps>(
  ({ className, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={cn("text-2xl font-semibold leading-none tracking-tight", className)}
        {...props}
      />
    )
  }
)

CardTitle.displayName = "CardTitle"

// CardContent component props - extends HTML div attributes for flexibility
// eslint-disable-next-line @typescript-eslint/no-empty-object-type
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
    )
  }
)

CardContent.displayName = "CardContent"