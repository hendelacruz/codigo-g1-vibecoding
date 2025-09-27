import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';

// Pagination component variants using CVA
const paginationVariants = cva(
  "flex items-center justify-center space-x-2",
  {
    variants: {
      size: {
        sm: "text-sm",
        md: "text-base", 
        lg: "text-lg",
      },
    },
    defaultVariants: {
      size: "md",
    },
  }
);

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
  {
    variants: {
      variant: {
        default: "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50",
        active: "bg-blue-600 text-white hover:bg-blue-700",
        ghost: "text-gray-500 hover:text-gray-700 hover:bg-gray-100",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

export interface PaginationProps extends VariantProps<typeof paginationVariants> {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showFirstLast?: boolean;
  showPrevNext?: boolean;
  maxVisiblePages?: number;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  showFirstLast = true,
  showPrevNext = true,
  maxVisiblePages = 5,
  size,
  className,
}) => {
  // Calculate visible page numbers
  const getVisiblePages = () => {
    const pages: number[] = [];
    const halfVisible = Math.floor(maxVisiblePages / 2);
    
    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, currentPage + halfVisible);
    
    // Adjust if we're near the beginning or end
    if (endPage - startPage + 1 < maxVisiblePages) {
      if (startPage === 1) {
        endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
      } else {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  const visiblePages = getVisiblePages();
  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;

  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav 
      className={cn(paginationVariants({ size }), className)}
      aria-label="Pagination Navigation"
    >
      {/* First page button */}
      {showFirstLast && !isFirstPage && (
        <button
          onClick={() => onPageChange(1)}
          className={cn(buttonVariants({ variant: "ghost", size }))}
          aria-label="Go to first page"
        >
          ««
        </button>
      )}

      {/* Previous page button */}
      {showPrevNext && (
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={isFirstPage}
          className={cn(buttonVariants({ variant: "default", size }))}
          aria-label="Go to previous page"
        >
          ‹ Anterior
        </button>
      )}

      {/* Page number buttons */}
      {visiblePages.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={cn(
            buttonVariants({ 
              variant: page === currentPage ? "active" : "default", 
              size 
            })
          )}
          aria-label={`Go to page ${page}`}
          aria-current={page === currentPage ? "page" : undefined}
        >
          {page}
        </button>
      ))}

      {/* Next page button */}
      {showPrevNext && (
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={isLastPage}
          className={cn(buttonVariants({ variant: "default", size }))}
          aria-label="Go to next page"
        >
          Siguiente ›
        </button>
      )}

      {/* Last page button */}
      {showFirstLast && !isLastPage && (
        <button
          onClick={() => onPageChange(totalPages)}
          className={cn(buttonVariants({ variant: "ghost", size }))}
          aria-label="Go to last page"
        >
          »»
        </button>
      )}
    </nav>
  );
};

export default Pagination;